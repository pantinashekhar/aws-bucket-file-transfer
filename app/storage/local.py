import os
from typing import List, BinaryIO
from app.core.config import settings
from app.storage.base import StorageClient, StorageObject

class LocalStorageClient(StorageClient):
    def __init__(self, root: str | None = None) -> None:
        self.root = root or settings.LOCAL_STORAGE_ROOT

    def _bucket_path(self, bucket: str) -> str:
        return os.path.join(self.root, bucket)

    def _object_path(self, bucket: str, key: str) -> str:
        return os.path.join(self._bucket_path(bucket), key)

    async def list_objects(self, bucket: str, prefix: str | None = None) -> List[StorageObject]:
        bucket_path = self._bucket_path(bucket)
        result: List[StorageObject] = []
        if not os.path.isdir(bucket_path):
            return result
        for root, _, files in os.walk(bucket_path):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, bucket_path)
                if prefix and not rel_path.startswith(prefix):
                    continue
                size = os.path.getsize(full_path)
                result.append(StorageObject(key=rel_path.replace("\\", "/"), size=size))
        return result

    async def upload_file(self, bucket: str, key: str, file_obj: BinaryIO) -> None:
        obj_path = self._object_path(bucket, key)
        os.makedirs(os.path.dirname(obj_path), exist_ok=True)
        with open(obj_path, "wb") as f:
            while True:
                chunk = file_obj.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

    async def download_file(self, bucket: str, key: str) -> bytes:
        obj_path = self._object_path(bucket, key)
        with open(obj_path, "rb") as f:
            return f.read()
