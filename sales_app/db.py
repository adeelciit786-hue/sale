import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Render injects DATABASE_URL automatically
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # fixes Render sleep disconnects
    pool_size=5,
    max_overflow=10
)

# Optional session factory
SessionLocal = sessionmaker(bind=engine)
