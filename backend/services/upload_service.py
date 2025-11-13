import os
import hashlib
import subprocess
from pathlib import Path
from fastapi import UploadFile
import aiofiles
import logging

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(__file__).parent.parent / "backups" 
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024 * 1024  # 50 GB

# Docker MSSQL container name ve backup dizini
MSSQL_CONTAINER = os.environ.get('MSSQL_CONTAINER', 'postgrator_mssql')
MSSQL_BACKUP_PATH = '/var/opt/mssql/backup'

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
    
    # Docker MSSQL container'ına kopyala
    try:
        docker_file_name = f"{job_id}_{upload_file.filename}"
        # Docker'a dosyayı kopyala
        result = subprocess.run(
            ['docker', 'cp', str(file_path), f'{MSSQL_CONTAINER}:{MSSQL_BACKUP_PATH}/{docker_file_name}'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Dosya Docker container'a kopyalandı: {MSSQL_BACKUP_PATH}/{docker_file_name}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Docker'a kopyalama başarısız (Docker kullanılmıyor olabilir): {e.stderr}")
    except FileNotFoundError:
        logger.warning("Docker komutu bulunamadı (Docker kurulu değil)")
    except Exception as e:
        logger.warning(f"Docker kopyalama hatası: {e}")
    
    return str(file_path), sha256_hash.hexdigest()

def get_backup_file_path(job_id: str) -> Path:
    """Get backup file path for a job"""
    files = list(BACKUP_DIR.glob(f"{job_id}_*"))
    if files:
        return files[0]
    return None
