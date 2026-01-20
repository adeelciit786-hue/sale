import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Render injects this automatically
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # handle Render sleep/wake
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"},  # safe for Render Postgres
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
