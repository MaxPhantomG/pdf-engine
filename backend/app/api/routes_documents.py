import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Header
from typing import List

from app.db.session import SessionLocal
from app.db.models import Document, User
from app.services.file_service import save_upload_file
from worker.app.tasks import process_pdf
from app.config import STORAGE_ROOT

router = APIRouter()

def get_current_user(x_user_token: str = Header(None, alias="X-User-Token")):
    db = SessionLocal()
    try:
        if not x_user_token:
            raise HTTPException(status_code=401, detail="Token missing")
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
        # Убедимся, что папка для файлов существует
        os.makedirs(STORAGE_ROOT, exist_ok=True)
        
        uploaded_docs = []
        for file in files:
            # 1. Создаем запись в БД, чтобы получить ID
            doc = Document(user_id=current_user.id, name=file.filename, status="queued")
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            # 2. Формируем путь и сохраняем файл физически
            file_path = Path(STORAGE_ROOT) / f"doc_{doc.id}_{file.filename}"
            save_upload_file(file, file_path)
            
            # 3. Обновляем путь и размер в БД
            doc.file_path = str(file_path)
            doc.size = os.path.getsize(file_path)
            db.commit()
            
            # 4. ОТПРАВЛЯЕМ ЗАДАЧУ В ВОРКЕР (Асинхронно)
            process_pdf.delay(doc.id)
            
            uploaded_docs.append({"id": doc.id, "name": doc.name, "status": doc.status})
            
        return {"status": "ok", "documents": uploaded_docs}
    finally:
        db.close()

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
