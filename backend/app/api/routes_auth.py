from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db

from app.schemas.auth import RegisterRequest
from app.schemas.auth import LoginRequest
from app.schemas.auth import TokenResponse

from app.core.security import (
    hash_password,
    verify_password
)

from app.core.auth import (
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
