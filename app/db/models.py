from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base

class FileOperationLog(Base):
    __tablename__ = "file_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)  # "list", "upload", "download"
    bucket = Column(String, nullable=False)
    key = Column(String, nullable=True)
    status = Column(String, nullable=False)  # "success", "error"
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
