from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255))
    file_path = Column(String(512))
    size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum("queued", "processing", "ready", "failed", name="doc_status"), default="queued")
    pages_count = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)
    user = relationship("User", back_populates="documents")
    fragments = relationship("DocumentFragment", back_populates="document", cascade="all, delete-orphan")

class DocumentFragment(Base):
    __tablename__ = "document_fragments"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page = Column(Integer)
    text = Column(Text)

    document = relationship("Document", back_populates="fragments")
