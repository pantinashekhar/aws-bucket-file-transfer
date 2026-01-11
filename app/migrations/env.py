import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context
from alembic.script import ScriptDirectory
from app.db.base import Base  # ADJUST: import your Base (e.g., from app import Base or app.models)
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine  # Sync engine
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

"""Run migrations synchronously."""



db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError("DATABASE_URL not set")

if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)  # Sync psycopg2
else:
    db_url = db_url.replace('postgresql://', 'postgresql://', 1)

# Sync engine for Alembic (uses psycopg2 implicitly)
connectable = create_engine(
    db_url,
    poolclass=NullPool,
    echo=True  # Debug SQL
)





target_metadata = Base.metadata  # Your models' metadata

with connectable.connect() as connection:  # Sync context
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

connectable.dispose()


def run_migrations_offline() -> None:
    """Offline mode not supported for async."""
    raise RuntimeError("Async engine only.")

def do_run_migrations(connection: AsyncConnection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run async migrations."""
    connectable = create_async_engine(db_url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
