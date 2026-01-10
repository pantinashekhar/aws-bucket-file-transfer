import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from db.base import Base
from db.models import FileOperationLog

async def init_db():
    """One-time DB initialization - creates tables"""
    # Use your Docker Postgres connection
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:Krishna123@localhost:5432/s3_transfer_db",
        echo=True  # Shows SQL queries
    )
    
    async with engine.begin() as conn:
        # Creates all tables defined in models
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
