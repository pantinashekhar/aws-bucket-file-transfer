import os
import aiofiles
from typing import List
from io import BytesIO
from .base import StorageClient, StorageObject

class LocalStorageClient(StorageClient):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "test"), exist_ok=True)  # Source bucket
        os.makedirs(os.path.join(self.data_dir, "backup"), exist_ok=True)  # Dest bucket

    async def list_objects(self, bucket: str, prefix: str | None = None) -> List[StorageObject]:
        bucket_path = os.path.join(self.data_dir, bucket)
        if not os.path.exists(bucket_path):
            return []
        
        objects = []
        for root, _, files in os.walk(bucket_path):
            for file in files:
                key = os.path.relpath(os.path.join(root, file), bucket_path)
                if prefix and not key.startswith(prefix):
                    continue
                size = os.path.getsize(os.path.join(root, file))
                objects.append(StorageObject(key, size))
        return objects

    async def upload_file(self, bucket: str, key: str, file_obj: BinaryIO) -> None:
        bucket_path = os.path.join(self.data_dir, bucket, key)
        os.makedirs(os.path.dirname(bucket_path), exist_ok=True)
        
        data = file_obj.read()
        async with aiofiles.open(bucket_path, 'wb') as f:
            await f.write(data)
        print(f"✅ Uploaded {bucket}/{key}")

    async def download_file(self, bucket: str, key: str) -> bytes:
        file_path = os.path.join(self.data_dir, bucket, key)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{bucket}/{key} not found")
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

# Create test file
async def create_test_file():
    async with aiofiles.open("data/test/foo.txt", 'w') as f:
        await f.write("Hello fake S3 world!")
