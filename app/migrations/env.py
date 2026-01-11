import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

# Alembic config FIRST
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# NO APP IMPORTS - define metadata inline or fix later
# Temporary: skip metadata or use string-based
target_metadata = None  # Run structure-only first

def run_migrations_online() -> None:
    db_url = os.environ.get('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = 'postgresql+psycopg2://' + db_url[10:]
    else:
        db_url = 'postgresql+psycopg2://' + db_url[12:]
    
    config.set_main_option('sqlalchemy.url', db_url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
    
    connectable.dispose()

def run_migrations_offline() -> None:
    """Offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
