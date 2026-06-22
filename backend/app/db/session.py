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

class _SessionLocalProxy:
    def __init__(self):
        self._factory = None  

    def __call__(self, *args, **kwargs):
        if self._factory is None:
            Engine = get_engine()
            self._factory = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
        return self._factory(*args, **kwargs)

SessionLocal = _SessionLocalProxy()

class _EngineProxy:
    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            self._engine = get_engine()
        return self._engine

    def __getattr__(self, item):
        eng = self._get_engine()
        return getattr(eng, item)

engine = _EngineProxy()

def get_db():
    Engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

