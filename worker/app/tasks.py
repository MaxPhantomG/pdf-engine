from .worker import app
from app.db.session import SessionLocal
from app.db.models import Document, DocumentFragment
from app.services.processor import extract_text_with_pages
import logging

logger = logging.getLogger("worker_logger")

@app.task(bind=True, max_retries=3)
def process_pdf(self, document_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"status": "error", "message": "Document not found"}

        doc.status = "processing"
        db.commit()

        pages_data = extract_text_with_pages(doc.file_path)

        db.query(DocumentFragment).filter(DocumentFragment.document_id == document_id).delete()
        
        for page_num, text in pages_data:
            fragment = DocumentFragment(
                document_id=document_id,
                page=page_num,
                text=text
            )
            db.add(fragment)

        doc.status = "ready"
        db.commit()
        
        logger.info(f"Document {document_id} processed successfully. Created {len(pages_data)} fragments.")
        return {"status": "success", "fragments_count": len(pages_data)}

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing doc {document_id}: {str(e)}")
        doc.status = "error"
        db.commit()
        raise self.retry(exc=e, countdown=300)
    finally:
        db.close()
