from fastapi import FastAPI, APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
import asyncio

from services import upload_service, migration_service
from services.migration_service import jobs
from utils.websocket_manager import manager
import psycopg

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="BAK to PostgreSQL Migration")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@api_router.get("/")
async def root():
    return {"message": "BAK to PostgreSQL Migration API"}

@api_router.post("/import/demo")
async def import_demo():
    """
    Demo mode - simulates migration without actual MSSQL/PostgreSQL
    """
    try:
        # Create demo job
        job_id = await migration_service.create_job(
            "postgresql://demo:demo@demo:5432/demo_db", 
            "public", 
            "demo_northwind.bak",
            is_demo=True
        )
        
        # Start demo migration in background
        asyncio.create_task(migration_service.run_demo_migration(job_id))
        
        return {"jobId": job_id, "status": "queued", "demo": True}
    
    except Exception as e:
        logger.error(f"Demo import failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/import")
async def import_backup(
    file: UploadFile = File(...),
    pgUri: str = Form(...),
    schema: str = Form("public")
):
    """
    Upload .bak file and start migration
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.bak'):
            raise HTTPException(status_code=400, detail="Sadece .bak dosyaları desteklenmektedir")
        
        # Test PostgreSQL connection
        try:
            conn = await psycopg.AsyncConnection.connect(pgUri)
            await conn.close()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PostgreSQL bağlantısı başarısız: {e}")
        
        # Create job
        job_id = await migration_service.create_job(pgUri, schema, file.filename)
        
        # Save uploaded file
        bak_path, sha256 = await upload_service.save_upload_file(file, job_id)
        logger.info(f"File uploaded: {bak_path}, SHA256: {sha256}")
        
        # Start migration in background
        asyncio.create_task(migration_service.run_migration(job_id))
        
        return {"jobId": job_id, "status": "queued"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status and progress
    """
    job = migration_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    return {
        "jobId": job.job_id,
        "status": job.status,
        "stage": job.stage,
        "percent": job.percent,
        "currentTable": job.stats.current_table,
        "stats": {
            "tablesDone": job.stats.tables_done,
            "tablesTotal": job.stats.tables_total,
            "elapsedSec": job.stats.elapsed_sec
        },
        "error": job.error
    }

@api_router.get("/jobs/{job_id}/tables")
async def get_job_tables(job_id: str):
    """
    Get list of tables for a job
    """
    job = migration_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    tables = [{
        "schema": t.schema_name,
        "name": t.table_name,
        "rowCount": t.row_count,
        "copied": t.copied,
        "error": t.error
    } for t in job.tables]
    
    return {"tables": tables}

@api_router.get("/jobs/{job_id}/tables/{table_name}/rows")
async def get_table_data(job_id: str, table_name: str, page: int = 1, pageSize: int = 100):
    """
    Get paginated table data
    """
    job = migration_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    try:
        conn = await psycopg.AsyncConnection.connect(job.pg_uri)
        
        try:
            from services import postgres_service
            columns, rows, total = await postgres_service.fetch_table_data_paginated(
                conn, job.schema, table_name, page, pageSize
            )
            
            return {
                "columns": columns,
                "rows": rows,
                "total": total,
                "page": page,
                "pageSize": pageSize
            }
        finally:
            await conn.close()
    
    except Exception as e:
        logger.error(f"Failed to fetch table data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs/{job_id}/artifacts/{filename}")
async def download_artifact(job_id: str, filename: str):
    """
    Download artifact file (schema.sql, rowcount.csv, errors.log)
    """
    allowed_files = ['schema.sql', 'rowcount.csv', 'errors.log']
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Geçersiz dosya adı")
    
    artifact_path = Path(f"/app/artifacts/{job_id}/{filename}")
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    return FileResponse(artifact_path, filename=filename)

@api_router.websocket("/jobs/{job_id}/stream")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates
    """
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, job_id)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
