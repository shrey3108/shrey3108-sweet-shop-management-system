"""
Pydantic schemas for User model validation and serialization
"""
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation (registration)"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: int
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data"""
    email: str | None = None
