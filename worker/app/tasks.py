from celery import Celery
from app.db.session import SessionLocal
from app.db.models import Document, DocumentFragment, User
import time

celery_app = Celery('tasks', broker='redis://redis:6379/0')

@celery_app.task(name="process_pdf")
def process_pdf(doc_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc: return "Not found"

        # Имитируем работу
        doc.status = "processing"
        db.commit()
        
        time.sleep(5) # Имитация долгого парсинга PDF
        
        doc.status = "completed"
        db.commit()
        return f"Doc {doc_id} processed"
    except Exception as e:
        if doc:
            doc.status = "error"
            db.commit()
        return str(e)
    finally:
        db.close()
