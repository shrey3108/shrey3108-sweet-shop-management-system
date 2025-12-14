"""
Pydantic schemas for Sweet model validation and serialization
"""
from pydantic import BaseModel, Field


class SweetBase(BaseModel):
    """Base sweet schema with common attributes"""
    name: str = Field(..., min_length=1, description="Sweet name")
    category: str = Field(..., min_length=1, description="Sweet category")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    quantity: int = Field(..., ge=0, description="Quantity must be non-negative")


class SweetCreate(SweetBase):
    """Schema for creating a new sweet"""
    pass


class SweetUpdate(SweetBase):
    """Schema for updating an existing sweet"""
    pass


class SweetResponse(SweetBase):
    """Schema for sweet response"""
    id: int

    model_config = {"from_attributes": True}


class SweetSearchParams(BaseModel):
    """Schema for sweet search parameters"""
    name: str | None = None
    category: str | None = None
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = Field(None, ge=0)
