import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Ensure service root is on sys.path when running Alembic directly
MIGRATIONS_DIR = os.path.abspath(os.path.dirname(__file__))
SERVICE_ROOT = os.path.abspath(os.path.join(MIGRATIONS_DIR, ".."))
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)

from app.config import settings
from app.database import Base
from app.models import *  # noqa: F401,F403

config = context.config
fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", settings.database_url.replace("asyncpg", "psycopg2"))

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
