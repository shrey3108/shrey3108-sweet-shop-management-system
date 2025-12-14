"""
Inventory Management API Endpoints

Handles purchase and restock operations for sweets.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inventory import InventoryOperation, InventoryResponse
from app.services.inventory_service import InventoryService
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User


router = APIRouter(prefix="/api/sweets", tags=["inventory"])


@router.post("/{sweet_id}/purchase", response_model=InventoryResponse)
async def purchase_sweet(
    sweet_id: int,
    operation: InventoryOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Purchase a sweet (decrease quantity)
    
    - **sweet_id**: ID of the sweet to purchase
    - **quantity**: Amount to purchase (must be > 0)
    
    Authentication required (any user can purchase).
    Returns error if out of stock or insufficient quantity.
    """
    sweet = InventoryService.purchase_sweet(db, sweet_id, operation.quantity)
    
    return InventoryResponse(
        id=sweet.id,
        name=sweet.name,
        category=sweet.category,
        price=sweet.price,
        quantity=sweet.quantity,
        message=f"Successfully purchased {operation.quantity} units of {sweet.name}"
    )


@router.post("/{sweet_id}/restock", response_model=InventoryResponse)
async def restock_sweet(
    sweet_id: int,
    operation: InventoryOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Restock a sweet (increase quantity) - ADMIN ONLY
    
    - **sweet_id**: ID of the sweet to restock
    - **quantity**: Amount to add to stock (must be > 0)
    
    Admin authentication required.
    """
    sweet = InventoryService.restock_sweet(db, sweet_id, operation.quantity)
    
    return InventoryResponse(
        id=sweet.id,
        name=sweet.name,
        category=sweet.category,
        price=sweet.price,
        quantity=sweet.quantity,
        message=f"Successfully restocked {operation.quantity} units of {sweet.name}"
    )
