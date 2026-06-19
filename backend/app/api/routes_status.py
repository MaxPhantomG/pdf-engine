from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import User, Document
from app.db.session import get_db
from app.schemas.status import StatusResponse
from app.core.security import get_current_user

router = APIRouter(
    prefix="/status",
    tags=["status"]
)

@router.get("/{document_id}", response_model=StatusResponse)
def get_document_status(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": document.status}