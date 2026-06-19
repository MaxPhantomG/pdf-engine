from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.search import SearchResult
from app.services.index_service import search_in_index

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.get("/", response_model=List[SearchResult])
def search_documents(query: str = Query(..., min_length=3)):
    results = search_in_index(query)
    return results