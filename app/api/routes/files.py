from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from storage.base import StorageClient, StorageObject
from storage.deps import get_storage_client

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/buckets/{bucket}/objects", response_model=list[dict])
async def list_objects(
    bucket: str,
    prefix: str | None = None,
    storage: StorageClient = Depends(get_storage_client),
):
    objects: list[StorageObject] = await storage.list_objects(bucket=bucket, prefix=prefix)
    return [
        {"key": obj.key, "size": obj.size}
        for obj in objects
    ]

@router.post("/buckets/{bucket}/objects")
async def upload_object(
    bucket: str,
    key: str,
    file: UploadFile = File(...),
    storage: StorageClient = Depends(get_storage_client),
):
    try:
        await storage.upload_file(bucket=bucket, key=key, file_obj=file.file)
        return {"bucket": bucket, "key": key, "status": "uploaded"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/buckets/{bucket}/objects/{key:path}")
async def download_object(
    bucket: str,
    key: str,
    storage: StorageClient = Depends(get_storage_client),
):
    try:
        data = await storage.download_file(bucket=bucket, key=key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Object not found")
    return StreamingResponse(iter([data]))
