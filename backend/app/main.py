from fastapi import FastAPI
from app.api.routes_documents import router as documents_router
from app.api.routes_search import router as search_router
from app.api.routes_status import router as status_router
from app.api.routes_auth import router as auth_router
from app.db.session import engine
from app.db.models import Base, User, Document, DocumentFragment    

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PDF Engine MVP")

app.include_router(auth_router, prefix="/api/auth") 
app.include_router(documents_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(status_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "PDF Engine MVP is running"}
