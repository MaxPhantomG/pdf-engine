from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from pydantic import BaseModel
import secrets 
import logging 

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthPayload(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(payload: AuthPayload, db: Session = Depends(get_db)):
    logger.error(f"--- ATTEMPT REGISTER: {payload.username} (len: {len(payload.password)}) ---")
    
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    # Обрезаем пароль до 71 байта (с запасом)
    safe_password = payload.password.encode('utf-8')[:71].decode('utf-8', 'ignore')
    
    try:
        hashed_pwd = pwd_context.hash(safe_password)
        new_user = User(
            username=payload.username,
            hashed_password=hashed_pwd,
            token=secrets.token_hex(16)
        )
        db.add(new_user)
        db.commit()
        return {"message": "User created"}
    except Exception as e:
        logger.error(f"Bcrypt error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при создании пароля")

@router.post("/login")
def login(payload: AuthPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    
    safe_password = payload.password[:72]
    
    if not user or not pwd_context.verify(safe_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    user.token = secrets.token_hex(16)
    db.commit()
    return {"token": user.token, "username": user.username}
