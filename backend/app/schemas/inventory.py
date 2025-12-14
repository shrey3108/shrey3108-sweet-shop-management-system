"""
Pydantic schemas for inventory operations
"""
from pydantic import BaseModel, Field, ConfigDict


class InventoryOperation(BaseModel):
    """Schema for inventory quantity operations (purchase/restock)"""
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class InventoryResponse(BaseModel):
    """Response schema for inventory operations"""
    id: int
    name: str
    category: str
    price: float
    quantity: int
    message: str
    
    model_config = ConfigDict(from_attributes=True)
