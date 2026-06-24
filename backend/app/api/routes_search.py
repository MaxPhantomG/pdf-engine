from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.db.models import Document
from app.services.index_service import find_matches
from app.schemas.search import SearchResponse, SearchResult, SearchMatch

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., min_length=1, description="Поисковый запрос"),
    db: Session = Depends(get_db)
):
    """
    Поиск по документам
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Пустой поисковый запрос")
    
    documents = db.query(Document).filter(
        Document.status == "ready",
        Document.content.isnot(None)
    ).all()
    
    results = []
    total_matches = 0
    
    for doc in documents:
        matches = find_matches(doc.content, query)
        
        if matches:
            search_matches = [
                SearchMatch(
                    snippet=m["snippet"],
                    highlight=m["highlight"],
                    position=m["position"]
                )
                for m in matches
            ]
            
            results.append(SearchResult(
                document_id=doc.id,
                document_name=doc.name,
                matches=search_matches,
                total_matches=len(search_matches)
            ))
            
            total_matches += len(search_matches)
    
    return SearchResponse(
        query=query,
        results=results,
        total_documents=len(results),
        total_matches=total_matches
    )

@router.get("/documents/{document_id}/content")
async def get_document_content(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить полное содержимое документа
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if not doc.content:
        raise HTTPException(status_code=404, detail="Содержимое документа не доступно")
    
    return {
        "document_id": doc.id,
        "document_name": doc.name,
        "content": doc.content,
        "pages_count": doc.pages_count
    }

@router.get("/documents/{document_id}/search")
async def search_in_document(
    document_id: int,
    query: str = Query(..., min_length=1, description="Поисковый запрос"),
    db: Session = Depends(get_db)
):
    """
    Поиск внутри конкретного документа
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if not doc.content:
        raise HTTPException(status_code=404, detail="Содержимое документа не доступно")
    
    matches = find_matches(doc.content, query)
    
    search_matches = [
        SearchMatch(
            snippet=m["snippet"],
            highlight=m["highlight"],
            position=m["position"]
        )
        for m in matches
    ]
    
    return SearchResult(
        document_id=doc.id,
        document_name=doc.name,
        matches=search_matches,
        total_matches=len(search_matches)
    )
