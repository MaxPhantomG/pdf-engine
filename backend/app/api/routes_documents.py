from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid
import os

from app.db.models import User, Document
from app.db.session import get_db
from app.schemas.document import DocumentResponse, DocumentCreate
from app.core.security import get_current_user
from app.services.file_service import save_uploaded_file
from app.services.task_service import enqueue_pdf_processing

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.get("/", response_model=list[DocumentResponse])
def list_user_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/", response_model=DocumentResponse)
def upload_documents(files: list[UploadFile] = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    for file in files:
        filename = f"{uuid.uuid4()}.pdf"
        file_path = save_uploaded_file(file, filename)
        # Создание записи в базе
        doc = Document(
            name=file.filename,
            path=file_path,
            size=os.path.getsize(file_path),
            status="queued",
            user_id=current_user.id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        results.append(doc)

        # Отправляем задачу на обработку
        enqueue_pdf_processing(doc.id)

    return results