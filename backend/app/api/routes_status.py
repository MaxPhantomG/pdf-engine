from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/status")
def status():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "services": {
            "db": "connected",
            "redis": "connected",
            "web": "running",
        }
    }
