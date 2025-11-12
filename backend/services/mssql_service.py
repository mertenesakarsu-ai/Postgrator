import pyodbc
import logging
from typing import List, Dict, Any
from pathlib import Path
import os

logger = logging.getLogger(__name__)

MSSQL_HOST = os.environ.get('MSSQL_HOST', 'localhost')
MSSQL_PORT = os.environ.get('MSSQL_PORT', '1433')
MSSQL_SA_PWD = os.environ.get('MSSQL_SA_PWD', 'YourStrong!Passw0rd')
TEMP_DB = os.environ.get('TEMP_DB', 'TempFromBak')

def get_connection_string(database='master'):
    return f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={MSSQL_HOST},{MSSQL_PORT};DATABASE={database};UID=sa;PWD={MSSQL_SA_PWD};TrustServerCertificate=yes;"

async def verify_backup(bak_path: str) -> bool:
    """
    Verify .bak file integrity using RESTORE VERIFYONLY
    """
    try:
        conn = pyodbc.connect(get_connection_string(), autocommit=True)
        cursor = conn.cursor()
        
        query = f"RESTORE VERIFYONLY FROM DISK = '{bak_path}'"
        logger.info(f"Verifying backup: {query}")
        cursor.execute(query)
        
        cursor.close()
        conn.close()
        logger.info("Backup verification successful")
        return True
    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        raise

async def get_backup_file_list(bak_path: str) -> List[Dict[str, str]]:
    """
    Get logical file names from backup using RESTORE FILELISTONLY
    """
    try:
        conn = pyodbc.connect(get_connection_string(), autocommit=True)
        cursor = conn.cursor()
        
        query = f"RESTORE FILELISTONLY FROM DISK = '{bak_path}'"
        cursor.execute(query)
        
        files = []
        for row in cursor.fetchall():
            files.append({
                'logical_name': row.LogicalName,
                'type': row.Type  # D = Data, L = Log
            })
        
        cursor.close()
        conn.close()
        return files
    except Exception as e:
        logger.error(f"Failed to get file list: {e}")
        raise

async def restore_database(bak_path: str, logical_files: List[Dict[str, str]]) -> bool:
    """
    Restore database to TEMP_DB
    """
    try:
        conn = pyodbc.connect(get_connection_string(), autocommit=True)
        cursor = conn.cursor()
        
        # Drop if exists
        try:
            cursor.execute(f"ALTER DATABASE [{TEMP_DB}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            cursor.execute(f"DROP DATABASE [{TEMP_DB}]")
        except:
            pass
        
        # Build RESTORE command with MOVE clauses
        move_clauses = []
        for lf in logical_files:
            if lf['type'] == 'D':
                move_clauses.append(f"MOVE '{lf['logical_name']}' TO '/var/opt/mssql/data/{TEMP_DB}.mdf'")
            elif lf['type'] == 'L':
                move_clauses.append(f"MOVE '{lf['logical_name']}' TO '/var/opt/mssql/data/{TEMP_DB}.ldf'")
        
        restore_query = f"""
        RESTORE DATABASE [{TEMP_DB}]
        FROM DISK = '{bak_path}'
        WITH {', '.join(move_clauses)},
        RECOVERY, REPLACE
        """
        
        logger.info(f"Restoring database: {restore_query}")
        cursor.execute(restore_query)
        
        cursor.close()
        conn.close()
        logger.info(f"Database restored to {TEMP_DB}")
        return True
    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        raise

async def discover_schema() -> Dict[str, Any]:
    """
    Discover schema from restored database
    Returns: {
        'tables': [{
            'schema': str,
            'name': str,
            'columns': [{'name': str, 'type': str, 'max_length': int, ...}],
            'primary_key': {'columns': [str]},
            'foreign_keys': [...],
            'indexes': [...]
        }]
    }
    """
    try:
        conn = pyodbc.connect(get_connection_string(TEMP_DB))
        cursor = conn.cursor()
        
        schema_info = {'tables': []}
        
        # Get all user tables
        cursor.execute("""
        SELECT s.name as schema_name, t.name as table_name, t.object_id
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE t.is_ms_shipped = 0
        ORDER BY s.name, t.name
        """)
        
        tables = cursor.fetchall()
        
        for table in tables:
            schema_name, table_name, object_id = table
            table_info = {
                'schema': schema_name,
                'name': table_name,
                'columns': [],
                'primary_key': None,
                'foreign_keys': [],
                'indexes': []
            }
            
            # Get columns
            cursor.execute(f"""
            SELECT 
                c.name,
                t.name as type_name,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                c.is_identity
            FROM sys.columns c
            INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
            WHERE c.object_id = ?
            ORDER BY c.column_id
            """, object_id)
            
            for col in cursor.fetchall():
                table_info['columns'].append({
                    'name': col.name,
                    'type': col.type_name,
                    'max_length': col.max_length,
                    'precision': col.precision,
                    'scale': col.scale,
                    'is_nullable': col.is_nullable,
                    'is_identity': col.is_identity
                })
            
            # Get primary key
            cursor.execute(f"""
            SELECT kc.name as column_name
            FROM sys.key_constraints k
            INNER JOIN sys.index_columns ic ON k.parent_object_id = ic.object_id AND k.unique_index_id = ic.index_id
            INNER JOIN sys.columns kc ON ic.object_id = kc.object_id AND ic.column_id = kc.column_id
            WHERE k.parent_object_id = ? AND k.type = 'PK'
            ORDER BY ic.key_ordinal
            """, object_id)
            
            pk_cols = [row.column_name for row in cursor.fetchall()]
            if pk_cols:
                table_info['primary_key'] = {'columns': pk_cols}
            
            # Get foreign keys
            cursor.execute(f"""
            SELECT 
                fk.name as fk_name,
                c.name as column_name,
                rs.name as ref_schema,
                rt.name as ref_table,
                rc.name as ref_column
            FROM sys.foreign_keys fk
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
            INNER JOIN sys.tables rt ON fkc.referenced_object_id = rt.object_id
            INNER JOIN sys.schemas rs ON rt.schema_id = rs.schema_id
            INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
            WHERE fk.parent_object_id = ?
            """, object_id)
            
            for fk in cursor.fetchall():
                table_info['foreign_keys'].append({
                    'name': fk.fk_name,
                    'column': fk.column_name,
                    'ref_schema': fk.ref_schema,
                    'ref_table': fk.ref_table,
                    'ref_column': fk.ref_column
                })
            
            # Get indexes
            cursor.execute(f"""
            SELECT 
                i.name as index_name,
                i.is_unique,
                c.name as column_name
            FROM sys.indexes i
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            WHERE i.object_id = ? AND i.is_primary_key = 0 AND i.type > 0
            ORDER BY i.name, ic.key_ordinal
            """, object_id)
            
            idx_dict = {}
            for idx in cursor.fetchall():
                if idx.index_name not in idx_dict:
                    idx_dict[idx.index_name] = {
                        'name': idx.index_name,
                        'is_unique': idx.is_unique,
                        'columns': []
                    }
                idx_dict[idx.index_name]['columns'].append(idx.column_name)
            
            table_info['indexes'] = list(idx_dict.values())
            
            schema_info['tables'].append(table_info)
        
        cursor.close()
        conn.close()
        
        logger.info(f"Discovered {len(schema_info['tables'])} tables")
        return schema_info
    except Exception as e:
        logger.error(f"Schema discovery failed: {e}")
        raise

async def get_table_row_count(schema: str, table: str) -> int:
    """
    Get row count for a table
    """
    try:
        conn = pyodbc.connect(get_connection_string(TEMP_DB))
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Failed to get row count: {e}")
        return 0

async def fetch_table_data_batch(schema: str, table: str, columns: List[str], offset: int, limit: int) -> List[tuple]:
    """
    Fetch data batch from MSSQL table
    """
    try:
        conn = pyodbc.connect(get_connection_string(TEMP_DB))
        cursor = conn.cursor()
        
        col_names = ', '.join([f'[{c}]' for c in columns])
        query = f"SELECT {col_names} FROM [{schema}].[{table}] ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to fetch data batch: {e}")
        raise
