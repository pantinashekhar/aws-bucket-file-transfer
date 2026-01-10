from typing import List, Protocol, BinaryIO

class StorageObject:
    def __init__(self, key: str, size: int | None = None):
        self.key = key
        self.size = size

class StorageClient(Protocol):
    async def list_objects(self, bucket: str, prefix: str | None = None) -> List[StorageObject]:
        ...

    async def upload_file(self, bucket: str, key: str, file_obj: BinaryIO) -> None:
        ...

    async def download_file(self, bucket: str, key: str) -> bytes:
        ...
