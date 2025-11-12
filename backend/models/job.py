from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class Stage(str, Enum):
    VERIFY = "verify"
    RESTORE = "restore"
    SCHEMA_DISCOVERY = "schema_discovery"
    DDL_APPLY = "ddl_apply"
    DATA_COPY = "data_copy"
    CONSTRAINTS_APPLY = "constraints_apply"
    VALIDATE = "validate"
    DONE = "done"

class TableInfo(BaseModel):
    schema_name: str
    table_name: str
    row_count: int = 0
    copied: bool = False
    duration_sec: Optional[float] = None
    error: Optional[str] = None
    percent: int = 0
    migrated_rows: int = 0

class JobStats(BaseModel):
    tables_done: int = 0
    tables_total: int = 0
    elapsed_sec: float = 0
    current_table: Optional[str] = None
    rows_migrated: int = 0

class Job(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.QUEUED
    stage: Stage = Stage.VERIFY
    percent: int = 0
    pg_uri: str
    schema: str = Field(default="public", alias="schema")
    bak_filename: str
    stats: JobStats = Field(default_factory=JobStats)
    tables: List[TableInfo] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    is_demo: bool = False

class ProgressEvent(BaseModel):
    event_type: str  # stage, table_progress, log, done, error
    data: Dict[str, Any]
