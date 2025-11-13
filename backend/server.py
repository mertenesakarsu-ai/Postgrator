
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse

from starlette.middleware.cors import CORSMiddleware
import os
import logging

import asyncio

from services import upload_service, migration_service
from services.migration_service import jobs
from utils.websocket_manager import manager
import psycopg



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
        
        # Fix PostgreSQL URI for Docker environment
        # Replace localhost/127.0.0.1 with 'postgres' service name
        fixed_pgUri = pgUri.replace('localhost', 'postgres').replace('127.0.0.1', 'postgres')
        
        # Test PostgreSQL connection
        try:
            conn = await psycopg.AsyncConnection.connect(fixed_pgUri)
            await conn.close()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PostgreSQL bağlantısı başarısız: {e}")
        
        # Create job with fixed URI
        job_id = await migration_service.create_job(fixed_pgUri, schema, file.filename)
        
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
    
    # Demo mode: return mock data
    if job.is_demo:
        return _get_demo_table_data(table_name, page, pageSize)
    
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

def _get_demo_table_data(table_name: str, page: int, pageSize: int):
    """Generate mock data for demo tables"""
    demo_data = {
        "Customers": {
            "columns": ["CustomerID", "CompanyName", "ContactName", "Country", "Phone"],
            "total": 91,
            "rows": [
                ["ALFKI", "Alfreds Futterkiste", "Maria Anders", "Germany", "030-0074321"],
                ["ANATR", "Ana Trujillo Emparedados", "Ana Trujillo", "Mexico", "(5) 555-4729"],
                ["ANTON", "Antonio Moreno Taquería", "Antonio Moreno", "Mexico", "(5) 555-3932"],
                ["AROUT", "Around the Horn", "Thomas Hardy", "UK", "(171) 555-7788"],
                ["BERGS", "Berglunds snabbköp", "Christina Berglund", "Sweden", "0921-12 34 65"],
            ]
        },
        "Orders": {
            "columns": ["OrderID", "CustomerID", "OrderDate", "ShipCity", "Freight"],
            "total": 830,
            "rows": [
                [10248, "VINET", "1996-07-04", "Reims", 32.38],
                [10249, "TOMSP", "1996-07-05", "Münster", 11.61],
                [10250, "HANAR", "1996-07-08", "Rio de Janeiro", 65.83],
                [10251, "VICTE", "1996-07-08", "Lyon", 41.34],
                [10252, "SUPRD", "1996-07-09", "Charleroi", 51.30],
            ]
        },
        "Order Details": {
            "columns": ["OrderID", "ProductID", "UnitPrice", "Quantity", "Discount"],
            "total": 2155,
            "rows": [
                [10248, 11, 14.00, 12, 0.0],
                [10248, 42, 9.80, 10, 0.0],
                [10248, 72, 34.80, 5, 0.0],
                [10249, 14, 18.60, 9, 0.0],
                [10249, 51, 42.40, 40, 0.0],
            ]
        },
        "Products": {
            "columns": ["ProductID", "ProductName", "CategoryID", "UnitPrice", "UnitsInStock"],
            "total": 77,
            "rows": [
                [1, "Chai", 1, 18.00, 39],
                [2, "Chang", 1, 19.00, 17],
                [3, "Aniseed Syrup", 2, 10.00, 13],
                [4, "Chef Anton's Cajun Seasoning", 2, 22.00, 53],
                [5, "Chef Anton's Gumbo Mix", 2, 21.35, 0],
            ]
        },
        "Categories": {
            "columns": ["CategoryID", "CategoryName", "Description"],
            "total": 8,
            "rows": [
                [1, "Beverages", "Soft drinks, coffees, teas, beers, and ales"],
                [2, "Condiments", "Sweet and savory sauces, relishes, spreads"],
                [3, "Confections", "Desserts, candies, and sweet breads"],
                [4, "Dairy Products", "Cheeses"],
                [5, "Grains/Cereals", "Breads, crackers, pasta, and cereal"],
            ]
        },
        "Employees": {
            "columns": ["EmployeeID", "FirstName", "LastName", "Title", "City"],
            "total": 9,
            "rows": [
                [1, "Nancy", "Davolio", "Sales Representative", "Seattle"],
                [2, "Andrew", "Fuller", "Vice President, Sales", "Tacoma"],
                [3, "Janet", "Leverling", "Sales Representative", "Kirkland"],
                [4, "Margaret", "Peacock", "Sales Representative", "Redmond"],
                [5, "Steven", "Buchanan", "Sales Manager", "London"],
            ]
        },
        "Suppliers": {
            "columns": ["SupplierID", "CompanyName", "ContactName", "Country", "Phone"],
            "total": 29,
            "rows": [
                [1, "Exotic Liquids", "Charlotte Cooper", "UK", "(171) 555-2222"],
                [2, "New Orleans Cajun Delights", "Shelley Burke", "USA", "(100) 555-4822"],
                [3, "Grandma Kelly's Homestead", "Regina Murphy", "USA", "(313) 555-5735"],
                [4, "Tokyo Traders", "Yoshi Nagase", "Japan", "(03) 3555-5011"],
                [5, "Cooperativa de Quesos", "Antonio del Valle", "Spain", "(98) 598 76 54"],
            ]
        },
        "Shippers": {
            "columns": ["ShipperID", "CompanyName", "Phone"],
            "total": 3,
            "rows": [
                [1, "Speedy Express", "(503) 555-9831"],
                [2, "United Package", "(503) 555-3199"],
                [3, "Federal Shipping", "(503) 555-9931"],
            ]
        }
    }
    
    # Get table data or return empty
    table_data = demo_data.get(table_name, {
        "columns": ["ID", "Name"],
        "total": 0,
        "rows": []
    })
    
    # Simulate pagination
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    paginated_rows = table_data["rows"][start_idx:end_idx]
    
    return {
        "columns": table_data["columns"],
        "rows": paginated_rows,
        "total": table_data["total"],
        "page": page,
        "pageSize": pageSize
    }

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
