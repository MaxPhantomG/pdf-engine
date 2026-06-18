from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    id: int
    filename: str
    size: int
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class DocumentStatusResponse(BaseModel):
    id: int
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

