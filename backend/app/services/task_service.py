from sqlalchemy.orm import Session
from app.db.models import Task, Document


def create_task(db: Session, document_id: int) -> Task:
    """Создает задачу обработки документа"""
    task = Task(document_id=document_id, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def mark_task_processing(db: Session, task_id: int):
    """Отмечает задачу как обрабатывается"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "processing"
        db.commit()


def mark_task_completed(db: Session, task_id: int, document_id: int):
    """Отмечает задачу как завершенная и обновляет статус документа"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "completed"
        db.commit()
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        doc.status = "ready"
        db.commit()


def mark_task_failed(db: Session, task_id: int, document_id: int, error_message: str):
    """Отмечает задачу как неудачная"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "failed"
        task.error_message = error_message
        db.commit()
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        doc.status = "error"
        db.commit()


def get_pending_tasks(db: Session) -> list:
    """Получает все задачи в статусе pending"""
    return db.query(Task).filter(Task.status == "pending").all()

