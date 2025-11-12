import os
import hashlib
from pathlib import Path
from fastapi import UploadFile
import aiofiles
import logging

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(__file__).parent.parent / "backups" 
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024 * 1024  # 50 GB

async def save_upload_file(upload_file: UploadFile, job_id: str) -> tuple[str, str]:
    """
    Save uploaded .bak file and return (file_path, sha256_hash)
    """
    file_path = BACKUP_DIR / f"{job_id}_{upload_file.filename}"
    
    # Calculate SHA-256 while saving
    sha256_hash = hashlib.sha256()
    total_size = 0
    
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await upload_file.read(8192 * 1024):  # 8MB chunks
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                # Clean up and raise error
                await f.close()
                file_path.unlink(missing_ok=True)
                raise ValueError(f"Dosya boyutu limiti aşıldı (max {MAX_FILE_SIZE // (1024**3)} GB)")
            
            await f.write(chunk)
            sha256_hash.update(chunk)
    
    logger.info(f"Dosya kaydedildi: {file_path} ({total_size / (1024**3):.2f} GB)")
    return str(file_path), sha256_hash.hexdigest()

def get_backup_file_path(job_id: str) -> Path:
    """Get backup file path for a job"""
    files = list(BACKUP_DIR.glob(f"{job_id}_*"))
    if files:
        return files[0]
    return None
