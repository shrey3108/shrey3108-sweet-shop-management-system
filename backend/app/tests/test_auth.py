"""
TDD Tests for Authentication - Written FIRST before implementation
These tests should initially fail, then pass after implementation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create a test client with fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_new_user_success(self, client):
        """Test successful registration of a new user"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "role": "USER"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "USER"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
        assert "password" not in data
    
    def test_register_duplicate_user_fails(self, client):
        """Test that registering duplicate email fails"""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "Password123!",
                "role": "USER"
            }
        )
        
        # Second registration with same email should fail
        response = client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "DifferentPass456!",
                "role": "USER"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_admin_user(self, client):
        """Test registration of admin user"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!",
                "role": "ADMIN"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "ADMIN"
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "Password123!",
                "role": "USER"
            }
        )
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_success(self, client):
        """Test successful login with correct credentials"""
        # First register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "login@example.com",
                "password": "MyPassword123!",
                "role": "USER"
            }
        )
        
        # Now try to login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "MyPassword123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client):
        """Test login fails with incorrect password"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "CorrectPassword123!",
                "role": "USER"
            }
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_returns_user_info(self, client):
        """Test that login returns user information along with token"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "info@example.com",
                "password": "Password123!",
                "role": "ADMIN"
            }
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "info@example.com",
                "password": "Password123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "info@example.com"
        assert data["user"]["role"] == "ADMIN"
        assert "id" in data["user"]


class TestPasswordHashing:
    """Test password hashing security"""
    
    def test_password_is_hashed(self, client):
        """Test that passwords are not stored in plain text"""
        password = "PlainTextPassword123!"
        response = client.post(
            "/api/auth/register",
            json={
                "email": "hash@example.com",
                "password": password,
                "role": "USER"
            }
        )
        
        # The response should not contain the plain password
        assert password not in str(response.json())
        
        # Should be able to login with the password (proving it's hashed correctly)
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "hash@example.com",
                "password": password
            }
        )
        assert login_response.status_code == 200
