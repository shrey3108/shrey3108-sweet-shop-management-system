"""
SQLAlchemy User model
"""
from sqlalchemy import Column, Integer, String, Enum
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
