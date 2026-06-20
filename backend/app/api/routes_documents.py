from fastapi import APIRint, APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid
import os
from app.db.models import User, Document
from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.core.security import get_current_user
from app.services.file_service import save_uploaded_file
from app.services.task_service import enqueue_pdf_processing
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=list[DocumentResponse])
async def upload_documents(
    files: list[UploadFile] = File(...), 
    current_user: User = Depends(get_currentint_user), 
    db: Session = Depends(get_db)
):
    results = []
    for file in files:
        # 1. Валидация расширения
        if not file.filename.lower().endswith('.pdf'):
            logger.error(f"Invalid file type: {file.filename}")
            continue # Или raise HTTPException, если нужно прерывать всё

        try:
            filename = f"{uuid.uuid4()}.pdf"
            file_path = await save_uploaded_file(file, filename)
            
            # 2. Создание записи
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
            
            # 3. Постановка в очередь
            enqueue_pdf_processing(doc.id)
            results.append(doc)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to upload {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}")

    return results