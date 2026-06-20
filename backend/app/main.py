from fastapi import FastAPI
from app.api.routes_auth import router as auth_router
from app.api import routes_documents, routes_status, routes_search
from app.core.logging import logger

app = FastAPI(title="PDF Engine API")

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(routes_documents.router)
app.include_router(routes_status.router)
app.include_router(routes_search.router)

@app.on_event("startup")
async def startup_event():
    logger.info("PDF Engine API started successfully.")

@app.get("/")
def root():
    return {"status": "ok", "message": "PDF Engine API is running"}