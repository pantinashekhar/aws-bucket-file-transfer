from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SQLEnum
from app.db.base import Base
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from enum import Enum

class OperationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class FileOperationLog(Base):
    __tablename__ = "file_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    bucket = Column(String, nullable=False)
    key = Column(String, nullable=True)
    status = Column(String, nullable=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TransferJob(AsyncAttrs, Base):
    __tablename__ = "transfer_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    source_bucket = Column(String)
    source_key = Column(String)
    dest_bucket = Column(String)
    dest_key = Column(String)
    status = Column(SQLEnum(OperationStatus), default=OperationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String, nullable=True)
