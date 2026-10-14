import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache
def get_engine() -> Engine:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env first.")
    # Recent SQLAlchemy defaults "postgresql://" to psycopg v3; this project installs psycopg2.
    return create_engine(url.replace("postgresql://", "postgresql+psycopg2://", 1), pool_pre_ping=True)
