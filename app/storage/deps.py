import os
from app.storage.local import LocalStorageClient
from app.storage.s3 import S3StorageClient

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")

async def get_storage_client():
    if STORAGE_BACKEND == "s3":
        return S3StorageClient()
    return LocalStorageClient()
