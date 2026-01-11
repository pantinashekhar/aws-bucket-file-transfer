import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine  # Add create_engine here
from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import target metadata
from app.db.base import Base
# ... (keep existing imports up to from sqlalchemy import pool)
# Remove: from sqlalchemy.ext.asyncio, asyncio imports

target_metadata = Base.metadata  # Your models

def run_migrations_online() -> None:
    """Run migrations synchronously with psycopg2."""
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError("DATABASE_URL not set")
    
    # FORCE psycopg2 sync driver - CRITICAL
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    else:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    connectable = create_engine(
        db_url,
        poolclass=NullPool,
        echo=True
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
    
    connectable.dispose()


def run_migrations_offline() -> None:
    """Run migrations offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()  # Sync call - no asyncio.run()

