# app/main.py
from fastapi import FastAPI
import logging

# Импорт маршрутов
from app.api.routes_auth import router as auth_router
from app.api import routes_documents, routes_status, routes_search

# Настройка логирования
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Создаем обработчик файла, сохраняем логи в logs/error.log
import os
LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'error.log'))
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Можно добавить дополнительный обработчик — например, консольный
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI(
    title="PDF Engine API"
)

app.include_router(auth_router)
app.include_router(routes_documents.router)
app.include_router(routes_status.router)
app.include_router(routes_search.router)

# Логирование при старте приложения
@app.on_event("startup")
async def startup_event():
    logger.info("Приложение запущено и готово принимать запросы.")


# Логирование в корне для запросов
@app.get("/")
def root():
    logger.info("Обращение к корневому эндпоинту '/'")
    return {
        "status": "ok"
    }