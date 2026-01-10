#!/usr/bin/env python3
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base

async def main():
    url = os.getenv('DATABASE_URL')
    if url and url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to DB...")
    engine = create_async_engine(url)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ All available tables created!')
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
