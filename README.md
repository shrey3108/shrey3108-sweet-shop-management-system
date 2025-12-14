# Sweet Shop Management System – Backend (FastAPI)

A production-ready RESTful API backend for managing a sweet shop's inventory, user authentication, and role-based access control. Built using FastAPI with comprehensive test coverage following Test-Driven Development (TDD) principles.

## Project Overview

This backend system provides a complete API solution for sweet shop management operations. It handles user authentication with JWT tokens, manages product inventory with full CRUD operations, and implements granular role-based permissions. The system supports real-time inventory tracking through purchase and restock operations, along with advanced search and filtering capabilities.

The project emphasizes code quality through TDD, with all features developed test-first to ensure reliability and maintainability.

## Features

### Authentication & Authorization
- **User Registration & Login**: Secure user account creation with email validation
- **JWT-Based Authentication**: Stateless token-based authentication using python-jose
- **Password Security**: Bcrypt hashing for secure password storage
- **Role-Based Access Control**: Two-tier system (USER, ADMIN) with endpoint-level protection

### Sweet Management
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality for sweets
- **Admin Protection**: Create, update, and delete operations restricted to ADMIN role
- **Public Access**: List and search operations available to all authenticated users
- **Data Validation**: Pydantic schemas ensure data integrity (price > 0, quantity ≥ 0)

### Inventory Management
- **Purchase Operations**: Any authenticated user can purchase sweets (decreases quantity)
- **Stock Validation**: Prevents purchases when out of stock or insufficient quantity
- **Restock Operations**: ADMIN-only endpoint to replenish inventory
- **Transaction Safety**: Database transactions ensure inventory consistency

### Search & Filtering
- **Name-Based Search**: Case-insensitive partial matching on sweet names
- **Category Filtering**: Exact match filtering by product category
- **Price Range Filtering**: Filter sweets within min/max price bounds
- **Combined Filters**: Support for multiple simultaneous filter criteria

### Database & Testing
- **SQLite Database**: File-based database with SQLAlchemy ORM
- **Comprehensive Test Suite**: 42+ automated tests covering all endpoints
- **Test-Driven Development**: All features developed with tests written first
- **Isolated Test Database**: Separate database for test runs with automatic cleanup

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** 0.109.0 | Modern web framework with automatic OpenAPI documentation |
| **SQLAlchemy** 2.0.25 | ORM for database operations with declarative models |
| **SQLite** | Lightweight file-based relational database |
| **Pydantic** 2.5.3 | Data validation and serialization using Python type hints |
| **python-jose** 3.3.0 | JWT token creation and validation (HS256 algorithm) |
| **bcrypt** 4.1.2 | Secure password hashing |
| **Pytest** 7.4.4 | Testing framework with fixture support |
| **Uvicorn** 0.27.0 | ASGI server for running FastAPI applications |
| **HTTPx** 0.26.0 | Test client for API endpoint testing |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── database.py                  # SQLAlchemy database configuration
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User model with role enum
│   │   └── sweet.py                 # Sweet product model
│   │
│   ├── schemas/                     # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py                  # User, Token schemas
│   │   ├── sweet.py                 # Sweet CRUD schemas
│   │   └── inventory.py             # Inventory operation schemas
│   │
│   ├── auth/                        # Authentication utilities
│   │   ├── __init__.py              # Password hashing, JWT creation
│   │   └── dependencies.py          # Auth dependencies (get_current_user, require_admin)
│   │
│   ├── routers/                     # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                  # POST /api/auth/register, /login
│   │   ├── sweets.py                # Full CRUD + search endpoints
│   │   └── inventory.py             # POST /api/sweets/{id}/purchase, /restock
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── sweet_service.py         # Sweet CRUD and search logic
│   │   └── inventory_service.py     # Purchase and restock logic
│   │
│   └── tests/                       # Pytest test suite
│       ├── __init__.py
│       ├── test_auth.py             # 9 auth tests (registration, login, hashing)
│       ├── test_sweets.py           # 19 sweet tests (CRUD, search, permissions)
│       └── test_inventory.py        # 14 inventory tests (purchase, restock, validation)
│
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
├── sweet_shop.db                    # SQLite database (auto-created)
└── README.md                        # This file
```

## Setup Instructions

### Prerequisites
- Python 3.12+ installed
- pip package manager

### Installation

1. **Clone the repository** (or navigate to the backend directory)
   ```bash
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The server will start at `http://127.0.0.1:8000`

5. **Access API Documentation**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## Running Tests

The project includes a comprehensive test suite with 42+ automated tests covering all functionality.

### Run all tests
```bash
pytest app/tests/ -v
```

### Run specific test files
```bash
# Authentication tests (9 tests)
pytest app/tests/test_auth.py -v

# Sweet management tests (19 tests)
pytest app/tests/test_sweets.py -v

# Inventory tests (14 tests)
pytest app/tests/test_inventory.py -v
```

### Test coverage includes
- ✅ User registration with validation (duplicate email, invalid format)
- ✅ User login with credential verification
- ✅ Password hashing (bcrypt security)
- ✅ JWT token generation and validation
- ✅ Role-based access control (USER vs ADMIN permissions)
- ✅ Sweet CRUD operations with authorization
- ✅ Search and filtering functionality
- ✅ Inventory purchase with stock validation
- ✅ Inventory restock (admin-only)
- ✅ HTTP status codes (401 vs 403 for auth failures)

**All tests passing:** ✅ 42 passed

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and receive JWT token | No |

**Example Registration:**
```json
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "USER"
}
```

**Example Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "USER"
  }
}
```

### Sweet Management Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/sweets` | Create new sweet | Yes | ADMIN |
| GET | `/api/sweets` | List all sweets | Yes | Any |
| GET | `/api/sweets/search` | Search sweets with filters | Yes | Any |
| PUT | `/api/sweets/{id}` | Update sweet | Yes | ADMIN |
| DELETE | `/api/sweets/{id}` | Delete sweet | Yes | ADMIN |

**Search Query Parameters:**
- `name`: Partial name matching (case-insensitive)
- `category`: Exact category match
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter

**Example Sweet Creation:**
```json
POST /api/sweets
Authorization: Bearer <admin_token>
{
  "name": "Chocolate Bar",
  "category": "Chocolate",
  "price": 2.99,
  "quantity": 150
}
```

### Inventory Management Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/sweets/{id}/purchase` | Purchase sweet (decrease quantity) | Yes | Any |
| POST | `/api/sweets/{id}/restock` | Restock sweet (increase quantity) | Yes | ADMIN |

**Example Purchase:**
```json
POST /api/sweets/1/purchase
Authorization: Bearer <user_token>
{
  "quantity": 5
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Chocolate Bar",
  "category": "Chocolate",
  "price": 2.99,
  "quantity": 145,
  "message": "Successfully purchased 5 units of Chocolate Bar"
}
```

**Purchase Validations:**
- ❌ Fails if sweet is out of stock (quantity = 0)
- ❌ Fails if requested quantity exceeds available stock
- ❌ Fails if quantity ≤ 0

**Restock Example:**
```json
POST /api/sweets/1/restock
Authorization: Bearer <admin_token>
{
  "quantity": 100
}
```

## Authorization Behavior

The API implements strict authorization with distinct HTTP status codes:

- **403 Forbidden**: Returned when credentials are missing (no Authorization header)
- **403 Forbidden**: Returned when user lacks required role (e.g., USER trying to access ADMIN endpoint)
- **401 Unauthorized**: Returned when JWT token is invalid or expired

This behavior is enforced by FastAPI's `HTTPBearer` security dependency and thoroughly tested in the test suite.

## Database Schema

### User Table
- `id`: Integer (Primary Key)
- `email`: String (Unique, Indexed)
- `hashed_password`: String
- `role`: Enum (USER, ADMIN)

### Sweet Table
- `id`: Integer (Primary Key)
- `name`: String
- `category`: String
- `price`: Float (must be > 0)
- `quantity`: Integer (must be ≥ 0)

## Development Approach

This project follows **Test-Driven Development (TDD)** methodology:

1. ✅ **Tests Written First**: All features have tests written before implementation
2. ✅ **Red-Green-Refactor**: Tests fail initially, then implementation makes them pass
3. ✅ **Comprehensive Coverage**: Every endpoint, validation rule, and edge case is tested
4. ✅ **Isolated Testing**: Each test uses a fresh database with automatic cleanup

## Test Report

**Total Tests:** 42 passing
- **Authentication Tests:** 9 passed
  - User registration (success, duplicate, invalid email, admin creation)
  - User login (success, wrong password, nonexistent user, user info return)
  - Password hashing verification
  
- **Sweet Management Tests:** 19 passed
  - Create sweet (admin success, user forbidden, no auth, invalid data)
  - List sweets (empty, with data, no auth required)
  - Search sweets (by name, category, price range, combined filters)
  - Update sweet (admin success, user forbidden, nonexistent, no auth)
  - Delete sweet (admin success, user forbidden, nonexistent, no auth)
  
- **Inventory Tests:** 14 passed
  - Purchase sweet (success, quantity reduction, out of stock, insufficient stock, invalid quantity, nonexistent, no auth)
  - Restock sweet (admin success, quantity increase, user blocked, invalid quantity, nonexistent, no auth, out-of-stock restock)

## My AI Usage

This project was developed with the assistance of AI tools (GitHub Copilot and ChatGPT) to accelerate development while maintaining high code quality.

**How AI Was Used:**
- **Boilerplate Generation**: AI helped generate initial file structures, imports, and repetitive code patterns
- **Test Writing**: AI assisted in creating comprehensive test cases following TDD principles
- **Debugging**: AI provided suggestions for resolving dependency conflicts (bcrypt/passlib compatibility, datetime deprecation warnings)
- **Code Refactoring**: AI helped refactor code for better separation of concerns (service layer extraction)
- **Documentation**: AI assisted in writing docstrings and this README

**Developer Ownership:**
- All AI-generated code was carefully reviewed and understood before integration
- Code structure and architecture decisions were made by the developer
- Business logic was designed and validated by the developer
- The developer maintains full ownership and deep understanding of the entire codebase
- AI served as an intelligent assistant, not an autonomous developer

**Learning Outcomes:**
Through this project, I gained hands-on experience with:
- FastAPI framework and async Python development
- JWT-based authentication implementation
- Role-based access control patterns
- SQLAlchemy ORM with declarative models
- Test-Driven Development methodology
- Pytest fixtures and test isolation
- RESTful API design principles
- Dependency injection in FastAPI

---

## License

This project is for educational and demonstration purposes.

## Contact

For questions or feedback about this project, please open an issue in the repository.
