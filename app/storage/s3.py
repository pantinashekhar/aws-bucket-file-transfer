# S3.py - Complete S3 file transfer service using FastAPI and Boto3
# Built for production-ready file upload/download with PostgreSQL metadata tracking

import boto3
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

# Database configuration (PostgreSQL)
DATABASE_URL = "postgresql://postgres:Krishna123@localhost/s3_transfer_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "amzn-s3-bucket-file-transfer")
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

app = FastAPI(title="S3 File Transfer Service")

# Database Models
class FileMetadata(Base):
    __tablename__ = "file_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String)
    bucket = Column(String)
    s3_key = Column(String)
    size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic models
class FileResponse(BaseModel):
    file_id: str
    filename: str
    s3_url: str
    size: int

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## Upload File Endpoint
@app.post("/upload/", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload file to S3 and store metadata in PostgreSQL"""
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{file_id}_{file.filename}"
    
    try:
        # Upload to S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        # Get file size
        file_size = file.size or 0
        
        # Store metadata
        db_file = FileMetadata(
            file_id=file_id,
            filename=file.filename,
            bucket=S3_BUCKET,
            s3_key=s3_key,
            size=file_size
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Generate presigned URL
        s3_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )
        
        return FileResponse(
            file_id=file_id,
            filename=file.filename,
            s3_url=s3_url,
            size=file_size
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

## Download File Endpoint
@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Generate presigned URL for file download"""
    
    # Query metadata from database
    db = SessionLocal()
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.file_id == file_id
    ).first()
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        s3_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': file_metadata.bucket,
                'Key': file_metadata.s3_key
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {"download_url": s3_url, "filename": file_metadata.filename}
        
    finally:
        db.close()

## List Files Endpoint
@app.get("/files/")
async def list_files(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List uploaded files with pagination"""
    
    files = db.query(FileMetadata).offset(skip).limit(limit).all()
    
    result = []
    for file in files:
        s3_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': file.bucket, 'Key': file.s3_key},
            ExpiresIn=3600
        )
        result.append({
            "file_id": file.file_id,
            "filename": file.filename,
            "size": file.size,
            "uploaded_at": file.uploaded_at,
            "s3_url": s3_url
        })
    
    return {"files": result, "total": len(files)}

## Delete File Endpoint
@app.delete("/files/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete file from S3 and database"""
    
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.file_id == file_id
    ).first()
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete from S3
        s3_client.delete_object(
            Bucket=file_metadata.bucket,
            Key=file_metadata.s3_key
        )
        
        # Delete from database
        db.delete(file_metadata)
        db.commit()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

## Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "S3 File Transfer"}


## Root Endpoint
@app.get("/")
async def root():
    """Root endpoint - API documentation available at /docs"""
    return {
        "message": "S3 File Transfer Service",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload/": "Upload file to S3",
            "GET /download/{file_id}": "Get download URL",
            "GET /files/": "List files",
            "DELETE /files/{file_id}": "Delete file",
            "GET /health": "Health check",
            "GET /docs": "Interactive API docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
