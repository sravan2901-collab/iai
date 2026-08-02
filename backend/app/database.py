import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Handle SQLite fallback for local development if PostgreSQL is not installed/configured
database_url = settings.DATABASE_URL

if not database_url.startswith("sqlite"):
    try:
        import psycopg2
        engine = create_engine(database_url, pool_pre_ping=True)
    except Exception:
        # Fall back to local SQLite DB if PostgreSQL driver or database is unavailable
        print("[DATABASE] PostgreSQL unavailable. Falling back to local SQLite database: sqlite:///./aksharai_dev.db")
        database_url = "sqlite:///./aksharai_dev.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
