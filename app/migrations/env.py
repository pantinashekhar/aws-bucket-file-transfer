"""Alembic env.py for async SQLAlchemy on Heroku."""

import os
import sys
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine
from sqlalchemy.ext.asyncio import AsyncConnection
from alembic import context

# Add your app's root to Python path (adjust 'app' if your package is different)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Import your SQLAlchemy Base/models (adjust import path to your models file)
from app.db.base import Base  # e.g., from app.models import Base; replace with your actual import
# target_metadata = None causes issues; use your Base.metadata
target_metadata = Base.metadata

# Alembic Config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set dynamic DATABASE_URL for Heroku
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+asyncpg://")
config.set_main_option("sqlalchemy.url", url)

def run_migrations_offline() -> None:
    """Run migrations offline (not used for async)."""
    raise NotImplementedError("Async mode only.")

def do_run_migrations(connection: AsyncConnection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table="alembic_version"  # Alembic tracking table
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
