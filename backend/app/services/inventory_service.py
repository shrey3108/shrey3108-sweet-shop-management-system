"""
Business logic for inventory management

Handles purchase and restock operations with proper transaction management.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sweet import Sweet


class InventoryService:
    """Service layer for inventory operations"""
    
    @staticmethod
    def purchase_sweet(db: Session, sweet_id: int, quantity: int) -> Sweet:
        """
        Process a purchase by decreasing sweet quantity
        
        Args:
            db: Database session
            sweet_id: ID of the sweet to purchase
            quantity: Amount to purchase
            
        Returns:
            Updated sweet object
            
        Raises:
            HTTPException: If sweet not found, out of stock, or insufficient quantity
        """
        # Get sweet from database
        sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
        
        if not sweet:
            raise HTTPException(status_code=404, detail="Sweet not found")
        
        # Check if out of stock
        if sweet.quantity == 0:
            raise HTTPException(status_code=400, detail="Sweet is out of stock")
        
        # Check if sufficient quantity available
        if sweet.quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Only {sweet.quantity} available"
            )
        
        # Decrease quantity
        sweet.quantity -= quantity
        db.commit()
        db.refresh(sweet)
        
        return sweet
    
    @staticmethod
    def restock_sweet(db: Session, sweet_id: int, quantity: int) -> Sweet:
        """
        Restock a sweet by increasing quantity (Admin only - enforced by router)
        
        Args:
            db: Database session
            sweet_id: ID of the sweet to restock
            quantity: Amount to add to stock
            
        Returns:
            Updated sweet object
            
        Raises:
            HTTPException: If sweet not found
        """
        # Get sweet from database
        sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
        
        if not sweet:
            raise HTTPException(status_code=404, detail="Sweet not found")
        
        # Increase quantity
        sweet.quantity += quantity
        db.commit()
        db.refresh(sweet)
        
        return sweet
