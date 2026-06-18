from fastapi import FastAPI

from app.api.routes_auth import (
    router as auth_router
)

app = FastAPI(
    title="PDF Engine API"
)

app.include_router(
    auth_router
)


@app.get("/")
def root():
    return {
        "status": "ok"
    }
