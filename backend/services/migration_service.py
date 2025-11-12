import asyncio
import logging
from pathlib import Path
import time
from typing import Dict
import json
import csv
import io

from models.job import Job, JobStatus, Stage, TableInfo
from utils.websocket_manager import manager

# Lazy imports to avoid loading heavy dependencies when not needed
mssql_service = None
postgres_service = None
upload_service = None

def _ensure_services():
    """Lazy load services only when needed for real migration"""
    global mssql_service, postgres_service, upload_service
    if mssql_service is None:
        from services import mssql_service as ms
        from services import postgres_service as ps
        from services import upload_service as us
        mssql_service = ms
        postgres_service = ps
        upload_service = us

logger = logging.getLogger(__name__)

# In-memory job storage (for MVP; production would use database)
jobs: Dict[str, Job] = {}

async def create_job(pg_uri: str, schema: str, bak_filename: str) -> str:
    """Create a new migration job"""
    job = Job(
        pg_uri=pg_uri,
        schema=schema,
        bak_filename=bak_filename
    )
    jobs[job.job_id] = job
    return job.job_id

def get_job(job_id: str) -> Job:
    """Get job by ID"""
    return jobs.get(job_id)

async def send_progress(job_id: str, event_type: str, **kwargs):
    """Send progress update via WebSocket"""
    await manager.send_event(job_id, event_type, kwargs)

async def run_migration(job_id: str):
    """
    Main migration pipeline
    """
    _ensure_services()  # Load services when needed
    
    job = jobs.get(job_id)
    if not job:
        return
    
    start_time = time.time()
    
    try:
        job.status = JobStatus.RUNNING
        await send_progress(job_id, "log", level="info", msg="Migrasyon başlatıldı")
        
        # Stage 1: Verify
        job.stage = Stage.VERIFY
        job.percent = 5
        await send_progress(job_id, "stage", v="verify")
        await send_progress(job_id, "log", level="info", msg=".bak dosyası doğrulanıyor...")
        
        bak_path = upload_service.get_backup_file_path(job_id)
        if not bak_path:
            raise Exception("Backup dosyası bulunamadı")
        
        # Verify backup
        await mssql_service.verify_backup(str(bak_path))
        await send_progress(job_id, "log", level="info", msg="✓ Backup doğrulandı")
        
        # Stage 2: Restore
        job.stage = Stage.RESTORE
        job.percent = 15
        await send_progress(job_id, "stage", v="restore")
        await send_progress(job_id, "log", level="info", msg="MSSQL'e restore ediliyor...")
        
        # Get file list
        logical_files = await mssql_service.get_backup_file_list(str(bak_path))
        await mssql_service.restore_database(str(bak_path), logical_files)
        await send_progress(job_id, "log", level="info", msg="✓ Database restore edildi")
        
        # Stage 3: Schema Discovery
        job.stage = Stage.SCHEMA_DISCOVERY
        job.percent = 25
        await send_progress(job_id, "stage", v="schema_discovery")
        await send_progress(job_id, "log", level="info", msg="Şema analiz ediliyor...")
        
        schema_info = await mssql_service.discover_schema()
        
        # Initialize table list
        for table in schema_info['tables']:
            row_count = await mssql_service.get_table_row_count(table['schema'], table['name'])
            job.tables.append(TableInfo(
                schema_name=table['schema'],
                table_name=table['name'],
                row_count=row_count
            ))
        
        job.stats.tables_total = len(job.tables)
        await send_progress(job_id, "log", level="info", msg=f"✓ {len(job.tables)} tablo bulundu")
        
        # Stage 4: DDL Apply
        job.stage = Stage.DDL_APPLY
        job.percent = 35
        await send_progress(job_id, "stage", v="ddl_apply")
        await send_progress(job_id, "log", level="info", msg="PostgreSQL şema oluşturuluyor...")
        
        pg_conn = await postgres_service.get_pg_connection(job.pg_uri)
        
        try:
            await postgres_service.create_schema(pg_conn, job.schema)
            ddl_sql = await postgres_service.generate_and_apply_ddl(pg_conn, schema_info, job.schema)
            
            # Save DDL to file
            artifacts_dir = Path(f"/app/artifacts/{job_id}")
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "schema.sql").write_text(ddl_sql)
            
            await send_progress(job_id, "log", level="info", msg="✓ Tablolar oluşturuldu")
            
            # Stage 5: Data Copy
            job.stage = Stage.DATA_COPY
            job.percent = 45
            await send_progress(job_id, "stage", v="data_copy")
            
            batch_size = 10000
            
            for idx, table_meta in enumerate(schema_info['tables']):
                table_name = table_meta['name']
                schema_name = table_meta['schema']
                job.stats.current_table = f"{schema_name}.{table_name}"
                
                await send_progress(job_id, "log", level="info", msg=f"Kopyalanıyor: {table_name}")
                
                # Truncate table
                await postgres_service.truncate_table(pg_conn, job.schema, table_name)
                
                # Get columns
                columns = [col['name'] for col in table_meta['columns']]
                
                # Copy data in batches
                offset = 0
                table_job_info = job.tables[idx]
                total_rows = table_job_info.row_count
                
                if total_rows > 0:
                    while offset < total_rows:
                        rows = await mssql_service.fetch_table_data_batch(
                            schema_name, table_name, columns, offset, batch_size
                        )
                        
                        if rows:
                            await postgres_service.copy_data_to_table(
                                pg_conn, job.schema, table_name, columns, rows
                            )
                        
                        offset += batch_size
                        
                        # Progress update
                        progress = min(100, int((offset / total_rows) * 100))
                        await send_progress(job_id, "table_progress",
                            table=table_name,
                            rows=min(offset, total_rows),
                            total=total_rows,
                            percent=progress
                        )
                
                table_job_info.copied = True
                job.stats.tables_done += 1
                
                # Update overall progress
                job.percent = 45 + int((job.stats.tables_done / job.stats.tables_total) * 30)
            
            await send_progress(job_id, "log", level="info", msg="✓ Tüm veriler kopyalandı")
            
            # Stage 6: Constraints Apply
            job.stage = Stage.CONSTRAINTS_APPLY
            job.percent = 80
            await send_progress(job_id, "stage", v="constraints_apply")
            await send_progress(job_id, "log", level="info", msg="Primary key'ler uygulanıyor...")
            
            await postgres_service.apply_primary_keys(pg_conn, schema_info, job.schema)
            
            await send_progress(job_id, "log", level="info", msg="Foreign key'ler uygulanıyor...")
            await postgres_service.apply_foreign_keys(pg_conn, schema_info, job.schema)
            
            await send_progress(job_id, "log", level="info", msg="Index'ler uygulanıyor...")
            await postgres_service.apply_indexes(pg_conn, schema_info, job.schema)
            
            await send_progress(job_id, "log", level="info", msg="✓ Kısıtlamalar uygulandı")
            
            # Stage 7: Validate
            job.stage = Stage.VALIDATE
            job.percent = 90
            await send_progress(job_id, "stage", v="validate")
            await send_progress(job_id, "log", level="info", msg="Doğrulama yapılıyor...")
            
            # Validate row counts
            rowcount_data = []
            all_valid = True
            
            for table_info in job.tables:
                pg_count = await postgres_service.get_table_row_count(
                    pg_conn, job.schema, table_info.table_name
                )
                
                match = pg_count == table_info.row_count
                if not match:
                    all_valid = False
                    table_info.error = f"Satır sayısı uyuşmuyor: MSSQL={table_info.row_count}, PG={pg_count}"
                
                rowcount_data.append({
                    'table': table_info.table_name,
                    'mssql_rows': table_info.row_count,
                    'pg_rows': pg_count,
                    'match': match
                })
            
            # Save rowcount report
            with open(artifacts_dir / "rowcount.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['table', 'mssql_rows', 'pg_rows', 'match'])
                writer.writeheader()
                writer.writerows(rowcount_data)
            
            if all_valid:
                await send_progress(job_id, "log", level="info", msg="✓ Tüm tablolar doğrulandı")
            else:
                await send_progress(job_id, "log", level="warning", msg="⚠ Bazı tablolarda uyuşmazlık var")
            
            # Stage 8: Done
            job.stage = Stage.DONE
            job.percent = 100
            job.status = JobStatus.DONE
            job.stats.elapsed_sec = time.time() - start_time
            
            await send_progress(job_id, "stage", v="done")
            await send_progress(job_id, "done", success=True)
            await send_progress(job_id, "log", level="info", 
                msg=f"✓ Migrasyon tamamlandı ({job.stats.elapsed_sec:.1f} saniye)")
        
        finally:
            await pg_conn.close()
    
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        job.status = JobStatus.FAILED
        job.error = str(e)
        
        # Save error log
        artifacts_dir = Path(f"/app/artifacts/{job_id}")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "errors.log").write_text(f"Error: {e}\n")
        
        await send_progress(job_id, "error", msg=str(e))
        await send_progress(job_id, "log", level="error", msg=f"Hata: {e}")


async def run_demo_migration(job_id: str):
    """
    Demo migration - simulates the process without real databases
    """
    job = jobs.get(job_id)
    if not job:
        return
    
    start_time = time.time()
    
    try:
        job.status = JobStatus.RUNNING
        await send_progress(job_id, "log", level="info", msg="Demo migrasyon başlatıldı")
        
        # Stage 1: Verify (simulated)
        job.stage = Stage.VERIFY
        job.percent = 5
        await send_progress(job_id, "stage", v="verify")
        await send_progress(job_id, "log", level="info", msg=".bak dosyası doğrulanıyor...")
        await asyncio.sleep(1)
        await send_progress(job_id, "log", level="info", msg="✓ Backup doğrulandı (demo)")
        
        # Stage 2: Restore (simulated)
        job.stage = Stage.RESTORE
        job.percent = 15
        await send_progress(job_id, "stage", v="restore")
        await send_progress(job_id, "log", level="info", msg="MSSQL'e restore ediliyor...")
        await asyncio.sleep(1.5)
        await send_progress(job_id, "log", level="info", msg="✓ Database restore edildi (demo)")
        
        # Stage 3: Schema Discovery (simulated)
        job.stage = Stage.SCHEMA_DISCOVERY
        job.percent = 25
        await send_progress(job_id, "stage", v="schema_discovery")
        await send_progress(job_id, "log", level="info", msg="Şema analiz ediliyor...")
        await asyncio.sleep(1)
        
        # Create demo tables
        demo_tables = [
            {"schema": "dbo", "name": "Customers", "rows": 91},
            {"schema": "dbo", "name": "Orders", "rows": 830},
            {"schema": "dbo", "name": "Order Details", "rows": 2155},
            {"schema": "dbo", "name": "Products", "rows": 77},
            {"schema": "dbo", "name": "Categories", "rows": 8},
            {"schema": "dbo", "name": "Employees", "rows": 9},
            {"schema": "dbo", "name": "Suppliers", "rows": 29},
            {"schema": "dbo", "name": "Shippers", "rows": 3}
        ]
        
        for table in demo_tables:
            job.tables.append(TableInfo(
                schema_name=table['schema'],
                table_name=table['name'],
                row_count=table['rows']
            ))
        
        job.stats.tables_total = len(job.tables)
        await send_progress(job_id, "log", level="info", msg=f"✓ {len(job.tables)} tablo bulundu (demo)")
        
        # Stage 4: DDL Apply (simulated)
        job.stage = Stage.DDL_APPLY
        job.percent = 35
        await send_progress(job_id, "stage", v="ddl_apply")
        await send_progress(job_id, "log", level="info", msg="PostgreSQL şema oluşturuluyor...")
        await asyncio.sleep(1)
        await send_progress(job_id, "log", level="info", msg="✓ Tablolar oluşturuldu (demo)")
        
        # Stage 5: Data Migration (simulated)
        job.stage = Stage.DATA_COPY
        job.percent = 45
        await send_progress(job_id, "stage", v="data_migration")
        await send_progress(job_id, "log", level="info", msg="Veri aktarımı başladı...")
        
        for idx, table_info in enumerate(job.tables):
            await send_progress(job_id, "log", level="info", 
                msg=f"[{idx+1}/{len(job.tables)}] {table_info.table_name} aktarılıyor...")
            
            # Simulate progress
            for i in range(0, 101, 25):
                table_info.percent = i
                table_info.migrated_rows = int(table_info.row_count * i / 100)
                await send_progress(job_id, "table_progress", 
                    table=table_info.table_name,
                    p=i,
                    rows=table_info.migrated_rows
                )
                await asyncio.sleep(0.3)
            
            table_info.percent = 100
            table_info.migrated_rows = table_info.row_count
            job.stats.tables_done += 1
            job.stats.rows_migrated += table_info.row_count
            
            # Update overall progress
            job.percent = 45 + int(40 * (idx + 1) / len(job.tables))
            
            await send_progress(job_id, "progress", 
                p=job.percent,
                tables_done=job.stats.tables_done,
                tables_total=job.stats.tables_total,
                rows=job.stats.rows_migrated
            )
        
        await send_progress(job_id, "log", level="info", msg="✓ Veri aktarımı tamamlandı (demo)")
        
        # Stage 6: Constraints (simulated)
        job.stage = Stage.CONSTRAINTS_APPLY
        job.percent = 90
        await send_progress(job_id, "stage", v="constraints")
        await send_progress(job_id, "log", level="info", msg="Kısıtlamalar uygulanıyor...")
        await asyncio.sleep(1)
        await send_progress(job_id, "log", level="info", msg="✓ Primary key'ler oluşturuldu (demo)")
        await send_progress(job_id, "log", level="info", msg="✓ Foreign key'ler oluşturuldu (demo)")
        await send_progress(job_id, "log", level="info", msg="✓ Index'ler oluşturuldu (demo)")
        
        # Stage 7: Validation (simulated)
        job.stage = Stage.VALIDATION
        job.percent = 95
        await send_progress(job_id, "stage", v="validation")
        await send_progress(job_id, "log", level="info", msg="Veri doğrulanıyor...")
        await asyncio.sleep(1)
        await send_progress(job_id, "log", level="info", msg="✓ Tüm tablolar doğrulandı (demo)")
        
        # Stage 8: Done
        job.stage = Stage.DONE
        job.percent = 100
        job.status = JobStatus.DONE
        job.stats.elapsed_sec = time.time() - start_time
        
        await send_progress(job_id, "stage", v="done")
        await send_progress(job_id, "done", success=True)
        await send_progress(job_id, "log", level="info", 
            msg=f"✓ Demo migrasyon tamamlandı ({job.stats.elapsed_sec:.1f} saniye)")
    
    except Exception as e:
        logger.error(f"Demo migration failed: {e}", exc_info=True)
        job.status = JobStatus.FAILED
        job.error = str(e)
        await send_progress(job_id, "error", msg=str(e))
        await send_progress(job_id, "log", level="error", msg=f"Hata: {e}")
