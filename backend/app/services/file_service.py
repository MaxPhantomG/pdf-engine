import os
import shutil
from pathlib import Path
from app.config import settings


STORAGE_DIR = Path(settings.STORAGE_PATH) if hasattr(settings, 'STORAGE_PATH') else Path("./storage")
FILES_DIR = STORAGE_DIR / "files"
EXTRACTED_DIR = STORAGE_DIR / "extracted"


def ensure_directories():
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def get_user_files_dir(user_id: int) -> Path:
    user_dir = FILES_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_extracted_dir(user_id: int) -> Path:
    user_dir = EXTRACTED_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def save_uploaded_file(user_id: int, filename: str, file_content: bytes) -> tuple[str, int]:
    """
    Сохраняет загруженный файл.
    Возвращает (путь_к_файлу, размер)
    """
    ensure_directories()
    user_dir = get_user_files_dir(user_id)
    file_path = user_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    size = file_path.stat().st_size
    return str(file_path), size


def get_file_path(user_id: int, filename: str) -> Path:
    return get_user_files_dir(user_id) / filename


def get_extracted_path(user_id: int, doc_id: int) -> Path:
    user_dir = get_user_extracted_dir(user_id)
    return user_dir / f"doc_{doc_id}.json"


def delete_file(file_path: str):
    """Удаляет файл"""
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

