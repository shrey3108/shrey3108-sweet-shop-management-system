"""
Sweet service layer for business logic
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.sweet import Sweet
from app.schemas.sweet import SweetCreate, SweetUpdate


class SweetService:
    """Service class for sweet-related operations"""
    
    @staticmethod
    def create_sweet(db: Session, sweet_data: SweetCreate) -> Sweet:
        """
        Create a new sweet
        
        Args:
            db: Database session
            sweet_data: Sweet creation data
        
        Returns:
            Created sweet
        """
        new_sweet = Sweet(
            name=sweet_data.name,
            category=sweet_data.category,
            price=sweet_data.price,
            quantity=sweet_data.quantity
        )
        
        db.add(new_sweet)
        db.commit()
        db.refresh(new_sweet)
        
        return new_sweet
    
    @staticmethod
    def get_all_sweets(db: Session) -> List[Sweet]:
        """
        Get all sweets
        
        Args:
            db: Database session
        
        Returns:
            List of all sweets
        """
        return db.query(Sweet).all()
    
    @staticmethod
    def get_sweet_by_id(db: Session, sweet_id: int) -> Optional[Sweet]:
        """
        Get a sweet by ID
        
        Args:
            db: Database session
            sweet_id: Sweet ID
        
        Returns:
            Sweet if found, None otherwise
        """
        return db.query(Sweet).filter(Sweet.id == sweet_id).first()
    
    @staticmethod
    def search_sweets(
        db: Session,
        name: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Sweet]:
        """
        Search sweets with optional filters
        
        Args:
            db: Database session
            name: Optional name filter (case-insensitive partial match)
            category: Optional category filter (exact match)
            min_price: Optional minimum price filter
            max_price: Optional maximum price filter
        
        Returns:
            List of matching sweets
        """
        query = db.query(Sweet)
        
        # Apply name filter (case-insensitive partial match)
        if name:
            query = query.filter(Sweet.name.ilike(f"%{name}%"))
        
        # Apply category filter (exact match)
        if category:
            query = query.filter(Sweet.category == category)
        
        # Apply price range filters
        if min_price is not None:
            query = query.filter(Sweet.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Sweet.price <= max_price)
        
        return query.all()
    
    @staticmethod
    def update_sweet(
        db: Session,
        sweet_id: int,
        sweet_data: SweetUpdate
    ) -> Optional[Sweet]:
        """
        Update an existing sweet
        
        Args:
            db: Database session
            sweet_id: Sweet ID to update
            sweet_data: Updated sweet data
        
        Returns:
            Updated sweet if found, None otherwise
        """
        sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
        
        if not sweet:
            return None
        
        # Update fields
        sweet.name = sweet_data.name
        sweet.category = sweet_data.category
        sweet.price = sweet_data.price
        sweet.quantity = sweet_data.quantity
        
        db.commit()
        db.refresh(sweet)
        
        return sweet
    
    @staticmethod
    def delete_sweet(db: Session, sweet_id: int) -> bool:
        """
        Delete a sweet
        
        Args:
            db: Database session
            sweet_id: Sweet ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
        
        if not sweet:
            return False
        
        db.delete(sweet)
        db.commit()
        
        return True
