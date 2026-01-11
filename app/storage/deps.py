from app.storage.local import LocalStorageClient

def get_storage_client() -> LocalStorageClient:
    # kept simple for now; later can switch to real S3
    return LocalStorageClient()
