# Sweet Shop Management System - Backend

FastAPI backend for Sweet Shop Management System with TDD approach.

## Features

- ✅ User Authentication (Register/Login)
- ✅ JWT Token-based Authorization
- ✅ Password Hashing with bcrypt
- ✅ SQLite Database with SQLAlchemy
- ✅ Role-based Access (USER, ADMIN)
- ✅ Test-Driven Development (TDD)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic schemas
│   ├── auth/
│   │   └── __init__.py      # Auth utilities (JWT, hashing)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Auth endpoints
│   └── tests/
│       ├── __init__.py
│       └── test_auth.py     # TDD tests
├── requirements.txt
└── README.md
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run tests (TDD approach):**
```bash
pytest app/tests/test_auth.py -v
```

3. **Run the application:**
```bash
uvicorn app.main:app --reload
```

4. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Base URL: http://localhost:8000

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "USER"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "USER"
  }
}
```

## Testing

Run all tests:
```bash
pytest app/tests/ -v
```

Run with coverage:
```bash
pytest app/tests/ --cov=app --cov-report=html
```

## TDD Approach

This project follows Test-Driven Development:
1. ✅ Tests written first in `test_auth.py`
2. ✅ Tests initially fail
3. ✅ Implementation code written to make tests pass
4. ✅ All tests now passing

## Database

- **Type:** SQLite (file-based)
- **File:** `sweet_shop.db` (created automatically)
- **ORM:** SQLAlchemy

## Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- Token expiration: 30 minutes
- Role-based access control (USER, ADMIN)

## Next Steps

- Add protected endpoints
- Implement refresh tokens
- Add user profile management
- Implement sweet shop business logic

## Development

To add new features:
1. Write tests first (TDD)
2. Run tests to see them fail
3. Implement the feature
4. Run tests to see them pass
5. Refactor if needed
