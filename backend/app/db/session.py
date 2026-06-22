import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url():
    return os.getenv("DATABASE_URL", "postgresql://postgres:example@db:5432/postgres")

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        url = get_database_url()
        _engine = create_engine(url, echo=False, pool_size=5)
    return _engine

def get_db():
    Engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

