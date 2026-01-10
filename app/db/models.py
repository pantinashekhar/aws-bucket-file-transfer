from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SQLEnum
from db.base import Base
from enum import Enum
class FileOperationLog(Base):
    __tablename__ = "file_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)  # "list", "upload", "download"
    bucket = Column(String, nullable=False)
    key = Column(String, nullable=True)
    status = Column(String, nullable=False)  # "success", "error"
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OperationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TransferJob(Base):
    __tablename__ = "transfer_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    source_bucket = Column(String, nullable=False)
    source_key = Column(String, nullable=False)
    dest_bucket = Column(String, nullable=False)
    dest_key = Column(String, nullable=False)
    status = Column(SQLEnum(OperationStatus), default=OperationStatus.PENDING, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())