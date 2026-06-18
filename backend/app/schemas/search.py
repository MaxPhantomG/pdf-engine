from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str


class SearchResultItem(BaseModel):
    document_id: int
    filename: str
    page: int
    snippet: str

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    results: list[SearchResultItem]

