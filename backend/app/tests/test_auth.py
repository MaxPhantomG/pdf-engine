import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app
from app.db.session import get_db
from app.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Создает и очищает базу данных перед КАЖДЫМ тестом."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# ==========================================
# ТЕСТЫ РЕГИСТРАЦИИ (/api/auth/register)
# ==========================================

def test_register_success():
    """1. Успешная регистрация пользователя."""
    response = client.post("/api/auth/register", json={
        "username": "test_user",
        "password": "strong_password123"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "User created"}

def test_register_duplicate_username():
    """2. Ошибка при регистрации с уже существующим юзернеймом."""
    # Регистрируем первого
    client.post("/api/auth/register", json={"username": "clone", "password": "123"})
    
    # Пытаемся зарегистрировать дубликат
    response = client.post("/api/auth/register", json={"username": "clone", "password": "456"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Пользователь уже существует"

def test_register_missing_fields():
    """3. Ошибка при отсутствии обязательных полей (Pydantic validation)."""
    response = client.post("/api/auth/register", json={"username": "only_user"})  # забыли пароль
    assert response.status_code == 422
    assert "detail" in response.json()

def test_register_long_password():
    """4. Регистрация с ультра-длинным паролем (успех, так как код обрезает его до 71 байта)."""
    long_pass = "a" * 150
    response = client.post("/api/auth/register", json={
        "username": "longpass_user",
        "password": long_pass
    })
    assert response.status_code == 200
    assert response.json() == {"message": "User created"}

# ==========================================
# ТЕСТЫ АВТОРИЗАЦИИ (/api/auth/login)
# ==========================================

def test_login_success():
    """5. Успешный вход и получение токена."""
    client.post("/api/auth/register", json={"username": "login_user", "password": "my_password"})
    
    response = client.post("/api/auth/login", json={
        "username": "login_user", 
        "password": "my_password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["username"] == "login_user"
    assert len(data["token"]) == 32

def test_login_wrong_password():
    """6. Ошибка при неверном пароле."""
    client.post("/api/auth/register", json={"username": "secure_user", "password": "correct_pwd"})
    
    response = client.post("/api/auth/login", json={
        "username": "secure_user", 
        "password": "WRONG_PASSWORD"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"

def test_login_non_existent_user():
    """7. Ошибка при входе незарегистрированного пользователя."""
    response = client.post("/api/auth/login", json={
        "username": "ghost_user", 
        "password": "some_password"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"

def test_login_updates_token():
    """8. Проверка, что при повторном входе генерируется новый токен."""
    client.post("/api/auth/register", json={"username": "token_user", "password": "pwd"})
    

    resp1 = client.post("/api/auth/login", json={"username": "token_user", "password": "pwd"})
    token1 = resp1.json()["token"]
    

    resp2 = client.post("/api/auth/login", json={"username": "token_user", "password": "pwd"})
    token2 = resp2.json()["token"]
    
    assert token1 != token2

# ==========================================
# ТЕСТЫ ДОСТУПА С ТОКЕНОМ (взаимосвязь)
# ==========================================

def test_access_protected_route_without_token():
    """9. Попытка обратиться к документам без токена (X-User-Token)."""
    response = client.get("/api/documents")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token missing"

def test_access_protected_route_with_invalid_token():
    """10. Попытка обратиться с несуществующим токеном."""
    response = client.get("/api/documents", headers={"X-User-Token": "fake_invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_access_protected_route_success():
    """11. Успешный доступ к списку документов с валидным токеном."""
    client.post("/api/auth/register", json={"username": "doc_user", "password": "pwd"})
    login_resp = client.post("/api/auth/login", json={"username": "doc_user", "password": "pwd"})
    token = login_resp.json()["token"]
    
    response = client.get("/api/documents", headers={"X-User-Token": token})
    assert response.status_code == 200
    assert response.json() == []  
