from pydantic import BaseModel
from typing import Optional

class DocumentCreate(BaseModel):
    name: str
    owner_id: int

class DocumentResponse(BaseModel):
    id: int
    name: str
    status: str
    uploaded_at: str

    class Config:
        orm_mode = True
