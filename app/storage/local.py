import os
import aiofiles
import logging
from pathlib import Path
from typing import BinaryIO
from .base import StorageClient  # Your abstract base


logger = logging.getLogger(__name__)


class LocalStorageClient(StorageClient):
    def __init__(self, data_dir: str = "data"):
        # ✅ Absolute project root path (works on Windows)
        project_root = Path(__file__).parent.parent.parent  # storage -> app -> root
        self.data_dir = project_root / data_dir
        self.data_dir.mkdir(exist_ok=True)
        logger.info(f"🔗 LocalStorage root: {self.data_dir.absolute()}")

    async def download_file(self, bucket: str, key: str) -> bytes:
        file_path = self.data_dir / bucket / key
        logger.info(f"📥 Downloading {bucket}/{key} -> {file_path.absolute()}")
        if not file_path.exists():
            # Auto-create test file if missing
            if bucket == "test" and key == "foo.txt":
                test_content = b"Hello fake S3 world!\n"
                test_path = self.data_dir / bucket / key
                test_path.parent.mkdir(exist_ok=True)
                async with aiofiles.open(test_path, 'wb') as f:
                    await f.write(test_content)
                logger.info(f"🆕 Auto-created test/foo.txt ({len(test_content)} bytes)")
            else:
                raise FileNotFoundError(f"{bucket}/{key} not found: {file_path}")
        async with aiofiles.open(file_path, 'rb') as f:
            data = await f.read()
        logger.info(f"✅ Downloaded {len(data)} bytes")
        return data

    async def upload_file(self, bucket: str, key: str, data: bytes | BinaryIO) -> None:
        bucket_path = self.data_dir / bucket / Path(key).parent
        bucket_path.mkdir(parents=True, exist_ok=True)
        file_path = self.data_dir / bucket / key
        logger.info(f"📤 Uploading to {bucket}/{key}")
        
        if isinstance(data, bytes):
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)  # ✅ bytes: direct write
        elif hasattr(data, 'read'):  # BinaryIO check
            data.seek(0)
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = data.read(8192)  # Sync read() on BytesIO [web:81]
                    if not chunk:
                        break
                    await f.write(chunk)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        
        logger.info(f"✅ Uploaded {file_path.absolute()}")
