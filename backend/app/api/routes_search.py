from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/search")
def search_documents(query: str) -> List[Dict[str, str]]:
    return [{"document_id": "1", "page": "1", "snippet": f"Results for '{query}'"}]
