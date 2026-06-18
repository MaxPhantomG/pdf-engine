from sqlalchemy.orm import Session
from app.db.models import DocumentFragment, Document


def index_document(db: Session, document_id: int, pages_data: dict):
    """
    Индексирует документ, создавая фрагменты для каждой страницы.
    
    Args:
        db: Database session
        document_id: ID документа
        pages_data: Словарь {page_num: text}
    """
    # Удаляем старые фрагменты если они есть
    db.query(DocumentFragment).filter(
        DocumentFragment.document_id == document_id
    ).delete()
    
    # Создаем новые фрагменты
    for page_num, text in pages_data.items():
        if text.strip():  # Только если есть текст
            fragment = DocumentFragment(
                document_id=document_id,
                page=int(page_num),
                text=text
            )
            db.add(fragment)
    
    db.commit()


def search_fragments(db: Session, query: str, user_id: int) -> list:
    """
    Ищет фрагменты по запросу.
    Используется простой текстовый поиск.
    """
    query_lower = query.lower()
    
    results = db.query(DocumentFragment, Document).join(
        Document, DocumentFragment.document_id == Document.id
    ).filter(
        Document.user_id == user_id,
        Document.status == "ready",
        DocumentFragment.text.ilike(f"%{query}%")
    ).all()
    
    formatted_results = []
    for fragment, doc in results:
        # Вырезаем snippet (контекст вокруг найденного текста)
        text = fragment.text
        idx = text.lower().find(query_lower)
        
        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(text), idx + len(query) + 50)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
        else:
            snippet = text[:200]
        
        formatted_results.append({
            "document_id": doc.id,
            "filename": doc.filename,
            "page": fragment.page,
            "snippet": snippet
        })
    
    return formatted_results

