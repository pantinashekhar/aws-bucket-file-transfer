import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

load_dotenv()


config = context.config
connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
    url=os.getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")
)
