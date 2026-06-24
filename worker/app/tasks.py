from celery import Celery
from app.db.session import SessionLocal
from app.db.models import Document, DocumentFragment
from app.services.pdf_service import extract_text_with_pages, extract_text  
import logging


logger = logging.getLogger(__name__)

celery_app = Celery('tasks', broker='redis://redis:6379/0')

@celery_app.task(name="process_pdf")
def process_pdf(doc_id: int):
    """
    Обработка загруженного PDF:
    1. Извлечь полный текст и сохранить в Document.content (для поиска)
    2. Разбить на страницы и сохранить в DocumentFragment (для пагинации)
    """
    db = SessionLocal()
    doc = None  
    
    try:
        # Получаем документ из БД
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.error(f"Document {doc_id} not found")
            return f"Document {doc_id} not found"

        logger.info(f"Starting processing document {doc_id}: {doc.name}")
        
        # Ставим статус "в обработке"
        doc.status = "processing"
        db.commit()
        

        try:
            full_text = extract_text(doc.file_path)
            doc.content = full_text
            logger.info(f"Extracted {len(full_text)} characters from document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to extract full text from {doc_id}: {e}")
        
        try:
            pages_data = extract_text_with_pages(doc.file_path)
            
            db.query(DocumentFragment).filter(DocumentFragment.document_id == doc_id).delete()
            
            for page_num, text_content in pages_data:
                fragment = DocumentFragment(
                    document_id=doc.id,
                    page=page_num,
                    text=text_content
                )
                db.add(fragment)
            
            doc.pages_count = len(pages_data)
            logger.info(f"Saved {len(pages_data)} page fragments for document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to extract pages from {doc_id}: {e}")

        doc.status = "ready"
        db.commit()
        
        logger.info(f"Document {doc_id} processed successfully")
        return {
            "status": "success",
            "doc_id": doc_id,
            "pages_count": doc.pages_count,
            "content_length": len(doc.content) if doc.content else 0
        }
        
    except Exception as e:
        logger.exception(f"Error processing doc {doc_id}: {e}")
        
        db.rollback()
        
        if doc:
            doc.status = "failed"
            db.commit()
        
        return {
            "status": "error",
            "doc_id": doc_id,
            "error": str(e)
        }
    finally:
        db.close()
