import os
from typing import Final

DATABASE_URL: Final[str] = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/pdfengine")
REDIS_URL: Final[str] = os.getenv("REDIS_URL", "redis://redis:6379/0")
STORAGE_ROOT: Final[str] = os.getenv("STORAGE_ROOT", "storage/files")
