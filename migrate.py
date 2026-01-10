#!/usr/bin/env python3
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from db.base import Base
from db.models import FileOperationLog, TransferJob

async def init_db():
    """Create all database tables"""
    # Fix Heroku DATABASE_URL format
    url = os.getenv('DATABASE_URL')
    if url and url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://')
    
    if not url:
        print("❌ DATABASE_URL not found")
        return
    
    print(f"🔗 Connecting to: {url.split('@')[1] if '@' in url else url[:50]}...")
    
    engine = create_async_engine(url, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
