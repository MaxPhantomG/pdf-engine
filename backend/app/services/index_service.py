from typing import List, Dict, Tuple
import re
import logging

logger = logging.getLogger("index_service")

def find_matches(text: str, query: str, context_chars: int = 100) -> List[Dict[str, str]]:
    """
    Ищет совпадения query в text и возвращает список сниппетов
    
    Args:
        text: Текст документа
        query: Поисковый запрос
        context_chars: Количество символов до и после совпадения для сниппета
    
    Returns:
        Список словарей с сниппетами: [{"snippet": "...", "highlight": "..."}, ...]
    """
    if not text or not query:
        return []
    
    text_lower = text.lower()
    query_lower = query.lower().strip()
    
    if not query_lower:
        return []
    
    matches = []
    start = 0
    
    while True:
        pos = text_lower.find(query_lower, start)
        if pos == -1:
            break
        
        snippet_start = max(0, pos - context_chars)
        snippet_end = min(len(text), pos + len(query) + context_chars)
        
        snippet = text[snippet_start:snippet_end]
        highlighted = text[pos:pos + len(query)]
        
        matches.append({
            "snippet": snippet,
            "highlight": highlighted,
            "position": pos
        })
        
        start = pos + len(query)
    
    logger.info(f"Found {len(matches)} matches for query '{query}'")
    return matches
