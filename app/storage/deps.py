from .local import LocalStorageClient  # Your fake impl

async def get_storage_client():
    return LocalStorageClient()
