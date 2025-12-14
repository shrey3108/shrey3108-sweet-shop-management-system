"""
TDD Tests for Sweet Management - Written FIRST before implementation
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


class TestCreateSweet:
    """Test sweet creation (Admin only)"""
    
    def test_create_sweet_as_admin_success(self, client, admin_token):
        """Test admin can create a sweet"""
        response = client.post(
            "/api/sweets",
            json={
                "name": "Chocolate Bar",
                "category": "Chocolate",
                "price": 2.99,
                "quantity": 100
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chocolate Bar"
        assert data["category"] == "Chocolate"
        assert data["price"] == 2.99
        assert data["quantity"] == 100
        assert "id" in data
    
    def test_create_sweet_as_user_forbidden(self, client, user_token):
        """Test regular user cannot create a sweet"""
        response = client.post(
            "/api/sweets",
            json={
                "name": "Gummy Bears",
                "category": "Gummy",
                "price": 1.99,
                "quantity": 50
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_create_sweet_without_auth_unauthorized(self, client):
        """Test creating sweet without authentication fails"""
        response = client.post(
            "/api/sweets",
            json={
                "name": "Lollipop",
                "category": "Hard Candy",
                "price": 0.99,
                "quantity": 200
            }
        )
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials
    
    def test_create_sweet_invalid_data(self, client, admin_token):
        """Test creating sweet with invalid data fails"""
        response = client.post(
            "/api/sweets",
            json={
                "name": "",  # Empty name
                "category": "Candy",
                "price": -5.00,  # Negative price
                "quantity": -10  # Negative quantity
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422


class TestListSweets:
    """Test listing all sweets"""
    
    def test_list_sweets_empty(self, client):
        """Test listing sweets when none exist"""
        response = client.get("/api/sweets")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_sweets_with_data(self, client, admin_token):
        """Test listing sweets returns all sweets"""
        # Create multiple sweets
        sweets = [
            {"name": "Chocolate Bar", "category": "Chocolate", "price": 2.99, "quantity": 100},
            {"name": "Gummy Bears", "category": "Gummy", "price": 1.99, "quantity": 50},
            {"name": "Lollipop", "category": "Hard Candy", "price": 0.99, "quantity": 200}
        ]
        
        for sweet in sweets:
            client.post(
                "/api/sweets",
                json=sweet,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # List all sweets
        response = client.get("/api/sweets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Chocolate Bar"
    
    def test_list_sweets_no_auth_required(self, client, admin_token):
        """Test listing sweets doesn't require authentication"""
        # Create a sweet as admin
        client.post(
            "/api/sweets",
            json={"name": "Candy Cane", "category": "Candy", "price": 1.50, "quantity": 75},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # List without auth
        response = client.get("/api/sweets")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestSearchSweets:
    """Test sweet search functionality"""
    
    def test_search_by_name(self, client, admin_token):
        """Test searching sweets by name"""
        # Create test sweets
        client.post(
            "/api/sweets",
            json={"name": "Dark Chocolate", "category": "Chocolate", "price": 3.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Milk Chocolate", "category": "Chocolate", "price": 2.99, "quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Gummy Bears", "category": "Gummy", "price": 1.99, "quantity": 75},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Search by name
        response = client.get("/api/sweets/search?name=chocolate")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("chocolate" in sweet["name"].lower() for sweet in data)
    
    def test_search_by_category(self, client, admin_token):
        """Test searching sweets by category"""
        # Create test sweets
        client.post(
            "/api/sweets",
            json={"name": "Dark Chocolate", "category": "Chocolate", "price": 3.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Gummy Bears", "category": "Gummy", "price": 1.99, "quantity": 75},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Search by category
        response = client.get("/api/sweets/search?category=Gummy")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Gummy"
    
    def test_search_by_price_range(self, client, admin_token):
        """Test searching sweets by price range"""
        # Create test sweets
        client.post(
            "/api/sweets",
            json={"name": "Cheap Candy", "category": "Candy", "price": 0.99, "quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Mid Chocolate", "category": "Chocolate", "price": 2.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Premium Truffle", "category": "Chocolate", "price": 5.99, "quantity": 20},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Search by price range
        response = client.get("/api/sweets/search?min_price=2.00&max_price=4.00")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mid Chocolate"
    
    def test_search_combined_filters(self, client, admin_token):
        """Test searching with multiple filters combined"""
        # Create test sweets
        client.post(
            "/api/sweets",
            json={"name": "Dark Chocolate", "category": "Chocolate", "price": 3.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Milk Chocolate", "category": "Chocolate", "price": 2.99, "quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/api/sweets",
            json={"name": "Chocolate Gummy", "category": "Gummy", "price": 3.50, "quantity": 75},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Search with name and category
        response = client.get("/api/sweets/search?name=chocolate&category=Chocolate")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(sweet["category"] == "Chocolate" for sweet in data)


class TestUpdateSweet:
    """Test sweet update functionality (Admin only)"""
    
    def test_update_sweet_as_admin_success(self, client, admin_token):
        """Test admin can update a sweet"""
        # Create a sweet
        create_response = client.post(
            "/api/sweets",
            json={"name": "Old Name", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Update the sweet
        response = client.put(
            f"/api/sweets/{sweet_id}",
            json={"name": "New Name", "category": "Chocolate", "price": 2.99, "quantity": 75},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["category"] == "Chocolate"
        assert data["price"] == 2.99
        assert data["quantity"] == 75
    
    def test_update_sweet_as_user_forbidden(self, client, admin_token, user_token):
        """Test regular user cannot update a sweet"""
        # Create a sweet as admin
        create_response = client.post(
            "/api/sweets",
            json={"name": "Candy", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Try to update as user
        response = client.put(
            f"/api/sweets/{sweet_id}",
            json={"name": "Updated", "category": "Candy", "price": 2.99, "quantity": 60},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    def test_update_nonexistent_sweet(self, client, admin_token):
        """Test updating non-existent sweet returns 404"""
        response = client.put(
            "/api/sweets/99999",
            json={"name": "Ghost", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_update_sweet_without_auth(self, client, admin_token):
        """Test updating sweet without auth fails"""
        # Create a sweet
        create_response = client.post(
            "/api/sweets",
            json={"name": "Candy", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Try to update without auth
        response = client.put(
            f"/api/sweets/{sweet_id}",
            json={"name": "Updated", "category": "Candy", "price": 2.99, "quantity": 60}
        )
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


class TestDeleteSweet:
    """Test sweet deletion functionality (Admin only)"""
    
    def test_delete_sweet_as_admin_success(self, client, admin_token):
        """Test admin can delete a sweet"""
        # Create a sweet
        create_response = client.post(
            "/api/sweets",
            json={"name": "To Delete", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Delete the sweet
        response = client.delete(
            f"/api/sweets/{sweet_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get("/api/sweets")
        assert len(get_response.json()) == 0
    
    def test_delete_sweet_as_user_forbidden(self, client, admin_token, user_token):
        """Test regular user cannot delete a sweet"""
        # Create a sweet as admin
        create_response = client.post(
            "/api/sweets",
            json={"name": "Protected", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Try to delete as user
        response = client.delete(
            f"/api/sweets/{sweet_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    def test_delete_nonexistent_sweet(self, client, admin_token):
        """Test deleting non-existent sweet returns 404"""
        response = client.delete(
            "/api/sweets/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
    
    def test_delete_sweet_without_auth(self, client, admin_token):
        """Test deleting sweet without auth fails"""
        # Create a sweet
        create_response = client.post(
            "/api/sweets",
            json={"name": "Protected", "category": "Candy", "price": 1.99, "quantity": 50},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sweet_id = create_response.json()["id"]
        
        # Try to delete without auth
        response = client.delete(f"/api/sweets/{sweet_id}")
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials
