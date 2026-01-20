import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DATABASE_URL is injected by Render (env variable)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # prevents stale connections after sleep
    pool_size=5,
    max_overflow=10
)

# Session factory (used later if needed)
SessionLocal = sessionmaker(bind=engine)
