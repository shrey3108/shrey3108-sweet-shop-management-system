"""
TDD Tests for Inventory Management

Tests written FIRST before implementation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    """Create admin user and return auth token"""
    # Register admin user
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@sweetshop.com",
            "password": "AdminPass123!",
            "role": "ADMIN"
        }
    )
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@sweetshop.com",
            "password": "AdminPass123!"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client):
    """Create regular user and return auth token"""
    # Register regular user
    client.post(
        "/api/auth/register",
        json={
            "email": "user@sweetshop.com",
            "password": "UserPass123!",
            "role": "USER"
        }
    )
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user@sweetshop.com",
            "password": "UserPass123!"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_sweet(client, admin_token):
    """Create a sample sweet for testing"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Test Candy",
            "category": "Candy",
            "price": 2.99,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


class TestPurchaseSweet:
    """Test cases for purchasing sweets (decreasing quantity)"""
    
    def test_purchase_sweet_success(self, client, user_token, sample_sweet):
        """Test successful purchase decreases quantity"""
        sweet_id = sample_sweet["id"]
        initial_quantity = sample_sweet["quantity"]
        purchase_amount = 5
        
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": purchase_amount},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sweet_id
        assert data["quantity"] == initial_quantity - purchase_amount
        assert "message" in data
        
    def test_purchase_reduces_quantity_correctly(self, client, user_token, sample_sweet):
        """Test multiple purchases reduce quantity correctly"""
        sweet_id = sample_sweet["id"]
        
        # First purchase
        client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 10},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Second purchase
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 15},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 100 - 10 - 15  # 75
        
    def test_purchase_when_out_of_stock(self, client, admin_token, user_token):
        """Test purchase fails when sweet is out of stock"""
        # Create sweet with 0 quantity
        create_response = client.post(
            "/api/sweets",
            json={
                "name": "Out of Stock",
                "category": "Candy",
                "price": 1.99,
                "quantity": 0
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 400
        assert "out of stock" in response.json()["detail"].lower()
        
    def test_purchase_exceeds_available_quantity(self, client, admin_token, user_token):
        """Test purchase fails when requested amount exceeds available quantity"""
        # Create sweet with limited quantity
        create_response = client.post(
            "/api/sweets",
            json={
                "name": "Limited Stock",
                "category": "Candy",
                "price": 1.99,
                "quantity": 5
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 10},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 400
        assert "insufficient stock" in response.json()["detail"].lower()
        
    def test_purchase_invalid_quantity(self, client, user_token, sample_sweet):
        """Test purchase fails with invalid quantity (negative or zero)"""
        sweet_id = sample_sweet["id"]
        
        # Test zero quantity
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 0},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 422
        
        # Test negative quantity
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": -5},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 422
        
    def test_purchase_nonexistent_sweet(self, client, user_token):
        """Test purchase fails for non-existent sweet"""
        response = client.post(
            "/api/sweets/99999/purchase",
            json={"quantity": 5},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404
        
    def test_purchase_without_auth(self, client, sample_sweet):
        """Test purchase fails without authentication"""
        sweet_id = sample_sweet["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/purchase",
            json={"quantity": 5}
        )
        
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code == 403


class TestRestockSweet:
    """Test cases for restocking sweets (increasing quantity)"""
    
    def test_restock_by_admin_success(self, client, admin_token, sample_sweet):
        """Test admin can successfully restock a sweet"""
        sweet_id = sample_sweet["id"]
        initial_quantity = sample_sweet["quantity"]
        restock_amount = 50
        
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": restock_amount},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sweet_id
        assert data["quantity"] == initial_quantity + restock_amount
        assert "message" in data
        
    def test_restock_increases_quantity_correctly(self, client, admin_token, sample_sweet):
        """Test multiple restocks increase quantity correctly"""
        sweet_id = sample_sweet["id"]
        
        # First restock
        client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 25},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Second restock
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 30},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 100 + 25 + 30  # 155
        
    def test_restock_blocked_for_regular_user(self, client, user_token, sample_sweet):
        """Test regular user cannot restock (admin only)"""
        sweet_id = sample_sweet["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 50},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
        
    def test_restock_invalid_quantity(self, client, admin_token, sample_sweet):
        """Test restock fails with invalid quantity (negative or zero)"""
        sweet_id = sample_sweet["id"]
        
        # Test zero quantity
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 0},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
        # Test negative quantity
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": -10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
    def test_restock_nonexistent_sweet(self, client, admin_token):
        """Test restock fails for non-existent sweet"""
        response = client.post(
            "/api/sweets/99999/restock",
            json={"quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
        
    def test_restock_without_auth(self, client, sample_sweet):
        """Test restock fails without authentication"""
        sweet_id = sample_sweet["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 50}
        )
        
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code == 403
        
    def test_restock_out_of_stock_sweet(self, client, admin_token):
        """Test admin can restock a sweet that's out of stock"""
        # Create sweet with 0 quantity
        create_response = client.post(
            "/api/sweets",
            json={
                "name": "Restocked Item",
                "category": "Candy",
                "price": 1.99,
                "quantity": 0
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/sweets/{sweet_id}/restock",
            json={"quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 100
