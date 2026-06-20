from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.search import SearchResult
from app.services.index_service import search_in_index
from app.db.session import get_db
from app.db.models import User
from app.core.security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.get("/", response_model=List[SearchResult])
def search_documents(
    query: str = Query(..., min_length=3),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = search_in_index(query, user_id=current_user.id)
    return results