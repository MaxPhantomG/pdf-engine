from celery import Celery
from app.db.session import SessionLocal
from app.db.models import Document, DocumentFragment
from app.services.pdf_service import extract_text_with_pages

celery_app = Celery('tasks', broker='redis://redis:6379/0')

@celery_app.task(name="process_pdf")
def process_pdf(doc_id: int):
    db = SessionLocal()
    try:
        # Получаем документ из БД
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc: 
            return f"Document {doc_id} not found"

        # Ставим статус "в обработке"
        doc.status = "processing"
        db.commit()
        
        # 1. Извлекаем текст из PDF (используем ваш готовый сервис)
        # Он возвращает список: [(1, "Текст стр 1"), (2, "Текст стр 2"), ...]
        pages_data = extract_text_with_pages(doc.file_path)
        
        # 2. Сохраняем каждую страницу как фрагмент (Индексация)
        for page_num, text_content in pages_data:
            fragment = DocumentFragment(
                document_id=doc.id,
                page=page_num,
                text=text_content
            )
            db.add(fragment)
        
        # 3. Обновляем статус на "готово" (важно: в БД enum "ready", а не "completed")
        doc.status = "ready"
        doc.pages_count = len(pages_data)
        db.commit()
        
        return f"Doc {doc_id} processed successfully. {len(pages_data)} pages indexed."
        
    except Exception as e:
        db.rollback() # Откатываем транзакцию в случае ошибки БД
        if doc:
            doc.status = "failed" # Статус ошибки
            db.commit()
        return f"Error processing doc {doc_id}: {str(e)}"
    finally:
        db.close()
