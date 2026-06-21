from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Header
from typing import List
from pathlib import Path
from fastapi import Header
from app.db.session import SessionLocal
from app.db.models import Document, User
from app.services.pdf_service import extract_text_with_pages
from app.services.file_service import save_upload_file
from worker.app.tasks import process_pdf

router = APIRouter()

# 1. Умная функция получения текущего пользователя
def get_current_user(x_user_token: str = Header(None, alias="X-User-Token")):
    db = SessionLocal()
    try:
        if not x_user_token:
            raise HTTPException(status_code=401, detail="Token missing")
        # Ищем пользователя, у которого в базе совпадает токен
        user = db.query(User).filter(User.token == x_user_token).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    finally:
        db.close()

@router.get("/documents")
def list_documents(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # 2. Фильтруем документы: только те, что принадлежат текущему пользователю
        docs = db.query(Document).filter(Document.user_id == current_user.id).all()
        return [
            {"id": d.id, "name": d.name, "status": d.status, "uploaded_at": d.uploaded_at}
            for d in docs
        ]
    finally:
        db.close()

@router.post("/documents/")
async def upload_documents(
    files: List[UploadFile] = File(...), 
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        for file in files:
            # Используем current_user.id вместо 1
            doc = Document(user_id=current_user.id, name=file.filename, status="queued")
            db.add(doc)
            db.commit()
            db.refresh(doc)
        return {"status": "ok"}
    finally:
        db.close()

# 3. Добавим удаление (чтобы "что-то можно было сделать")
@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        db.delete(doc)
        db.commit()
        return {"message": "Deleted"}
    finally:
        db.close()
