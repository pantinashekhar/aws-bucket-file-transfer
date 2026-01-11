#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base

load_dotenv()

async def main():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("DATABASE_URL environment variable not set!")
    
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    print(f"Connecting to DB: {url}")
    engine = create_async_engine(url, echo=True)
    
    # DROP all tables first
    async with engine.begin() as conn:
        print("⏳ Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tables dropped")
        
        # CREATE all tables
        print("⏳ Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())