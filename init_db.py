#!/usr/bin/env python3
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from db.base import Base
from db.models import FileOperationLog, TransferJob  # Add your models here

async def main():
    url = os.getenv('DATABASE_URL')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to {url.split('@')[-1].split('/')[0]}...")
    engine = create_async_engine(url, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Tables created successfully!')
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
