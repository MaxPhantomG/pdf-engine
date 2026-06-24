from pydantic import BaseModel, Field
from typing import List, Optional

class SearchMatch(BaseModel):
    snippet: str = Field(..., description="Сниппет с контекстом")
    highlight: str = Field(..., description="Подсвеченное совпадение")
    position: int = Field(..., description="Позиция в тексте")

class SearchResult(BaseModel):
    document_id: int = Field(..., description="ID документа")
    document_name: str = Field(..., description="Название документа")
    matches: List[SearchMatch] = Field(default_factory=list, description="Найденные совпадения")
    total_matches: int = Field(..., description="Общее количество совпадений")

class SearchResponse(BaseModel):
    query: str = Field(..., description="Поисковый запрос")
    results: List[SearchResult] = Field(default_factory=list, description="Результаты поиска")
    total_documents: int = Field(..., description="Общее количество найденных документов")
    total_matches: int = Field(..., description="Общее количество совпадений")
