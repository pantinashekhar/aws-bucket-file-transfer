from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.storage.base import StorageClient, StorageObject
from app.storage.deps import get_storage_client

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/health")
async def health():
    return {"status": "ok", "message": "S3 Transfer Service ready"}

@router.get("/buckets/{bucket}/objects", response_model=List[dict])
async def list_objects(
    bucket: str,
    prefix: Optional[str] = Query(None, description="Object key prefix"),
    storage: StorageClient = Depends(get_storage_client),
):
    if not bucket or len(bucket) > 63 or not bucket.replace('-', '').replace('.', '').isalnum():
        raise HTTPException(400, "Invalid bucket name")
    
    try:
        objects = await storage.list_objects(bucket=bucket, prefix=prefix)
        return [{"key": obj.key, "size": obj.size} for obj in objects]
    except Exception as e:
        raise HTTPException(500, f"Storage error: {str(e)}")

@router.post("/buckets/{bucket}/objects")
async def upload_object(
    bucket: str,
    key: str,
    file: UploadFile = File(..., description="File to upload"),
    storage: StorageClient = Depends(get_storage_client),
):
    if not bucket or len(bucket) > 63:
        raise HTTPException(400, "Invalid bucket name")
    if not key or len(key) > 1024:
        raise HTTPException(400, "Invalid object key")

    if not file.content_type or file.size is None or file.size > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(413, "File too large or invalid")

    try:
        await storage.upload_file(bucket=bucket, key=key, file_obj=file.file)
        return {
            "bucket": bucket,
            "key": key,
            "size": file.size,
            "status": "uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.get("/buckets/{bucket}/objects/{key:path}")
async def download_object(
    bucket: str,
    key: str,
    storage: StorageClient = Depends(get_storage_client),
):
    if not bucket or len(bucket) > 63:
        raise HTTPException(400, "Invalid bucket name")
    if not key:
        raise HTTPException(400, "Object key required")

    try:
        data = await storage.download_file(bucket=bucket, key=key)
        return StreamingResponse(
            iter([data]),
            media_type="application/octet-stream",
            headers={"Content-Length": str(len(data))}
        )
    except FileNotFoundError:
        raise HTTPException(404, f"Object not found: {bucket}/{key}")
    except Exception as e:
        raise HTTPException(500, f"Download failed: {str(e)}")
