import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "S3 Transfer Service"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/s3_transfer_db",
    )
    LOCAL_STORAGE_ROOT: str = os.getenv("LOCAL_STORAGE_ROOT", "./data")

settings = Settings()