import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# --- ТЕСТЫ РЕГИСТРАЦИИ ---

def test_register_success():
    """1. Успешная регистрация нового пользователя"""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_register_duplicate_email():
    """2. Ошибка при регистрации существующего email"""
    client.post("/api/auth/register", json={
        "email": "dup@example.com", "password": "password", "full_name": "User 1"
    })
    response = client.post("/api/auth/register", json={
        "email": "dup@example.com", "password": "password", "full_name": "User 2"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_register_invalid_email():
    """3. Ошибка при невалидном формате email"""
    response = client.post("/api/auth/register", json={
        "email": "invalid-email", "password": "password", "full_name": "User"
    })
    assert response.status_code == 422 # Pydantic validation error

def test_register_empty_password():
    """4. Ошибка при пустом пароле"""
    response = client.post("/api/auth/register", json={
        "email": "empty@example.com", "password": "", "full_name": "User"
    })
    assert response.status_code == 400 or response.status_code == 422

# --- ТЕСТЫ АВТОРИЗАЦИИ (LOGIN) ---

def test_login_success():
    """5. Успешный вход и получение токена"""
    # Сначала регистрируем
    client.post("/api/auth/register", json={
        "email": "login@example.com", "password": "correct_pass", "full_name": "Login User"
    })
    # Входим
    response = client.post("/api/auth/login", data={
        "username": "login@example.com",
        "password": "correct_pass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password():
    """6. Ошибка при неверном пароле"""
    response = client.post("/api/auth/login", data={
        "username": "login@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_login_non_existent_user():
    """7. Ошибка при входе несуществующего пользователя"""
    response = client.post("/api/auth/login", data={
        "username": "ghost@example.com",
        "password": "any_password"
    })
    assert response.status_code == 401

# --- ТЕСТЫ ЗАЩИЩЕННЫХ РОУТОВ ---

def test_access_protected_without_token():
    """8. Ошибка доступа к защищенному роуту без токена"""
    response = client.get("/api/documents")
    assert response.status_code == 401

def test_access_protected_with_invalid_token():
    """9. Ошибка при использовании поддельного токена"""
    response = client.get("/api/documents", headers={"Authorization": "Bearer not_a_real_token"})
    assert response.status_code == 401

def test_access_protected_success():
    """10. Успешный доступ с валидным токеном"""
    resp = client.post("/api/auth/login", data={
        "username": "login@example.com",
        "password": "correct_pass"
    })
    token = resp.json()["access_token"]
    response = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
