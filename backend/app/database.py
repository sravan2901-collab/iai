import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Handle SQLite fallback for local development if PostgreSQL is not installed/configured
database_url = settings.DATABASE_URL

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BACKEND_DIR, "aksharai_dev.db")

if not database_url.startswith("sqlite"):
    try:
        import psycopg2
        engine = create_engine(database_url, pool_pre_ping=True)
    except Exception:
        print(f"[DATABASE] PostgreSQL unavailable. Falling back to local SQLite database: {DEFAULT_DB_PATH}")
        database_url = f"sqlite:///{DEFAULT_DB_PATH}"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    if "./aksharai_dev.db" in database_url:
        database_url = f"sqlite:///{DEFAULT_DB_PATH}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
