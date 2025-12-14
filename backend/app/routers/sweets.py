"""
Sweet management router with role-based access control
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.sweet import SweetCreate, SweetUpdate, SweetResponse
from app.services.sweet_service import SweetService
from app.auth.dependencies import require_admin


router = APIRouter(prefix="/api/sweets", tags=["sweets"])


@router.post("", response_model=SweetResponse, status_code=status.HTTP_201_CREATED)
def create_sweet(
    sweet_data: SweetCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new sweet (Admin only)
    
    Args:
        sweet_data: Sweet creation data
        db: Database session
        admin: Current admin user (from dependency)
    
    Returns:
        Created sweet
    """
    return SweetService.create_sweet(db, sweet_data)


@router.get("", response_model=List[SweetResponse])
def list_sweets(db: Session = Depends(get_db)):
    """
    Get all sweets (Public endpoint)
    
    Args:
        db: Database session
    
    Returns:
        List of all sweets
    """
    return SweetService.get_all_sweets(db)


@router.get("/search", response_model=List[SweetResponse])
def search_sweets(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    category: Optional[str] = Query(None, description="Filter by category (exact match)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    db: Session = Depends(get_db)
):
    """
    Search sweets with optional filters (Public endpoint)
    
    Args:
        name: Optional name filter
        category: Optional category filter
        min_price: Optional minimum price
        max_price: Optional maximum price
        db: Database session
    
    Returns:
        List of matching sweets
    """
    return SweetService.search_sweets(
        db=db,
        name=name,
        category=category,
        min_price=min_price,
        max_price=max_price
    )


@router.put("/{sweet_id}", response_model=SweetResponse)
def update_sweet(
    sweet_id: int,
    sweet_data: SweetUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update an existing sweet (Admin only)
    
    Args:
        sweet_id: ID of sweet to update
        sweet_data: Updated sweet data
        db: Database session
        admin: Current admin user (from dependency)
    
    Returns:
        Updated sweet
    
    Raises:
        HTTPException: If sweet not found
    """
    updated_sweet = SweetService.update_sweet(db, sweet_id, sweet_data)
    
    if not updated_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sweet with id {sweet_id} not found"
        )
    
    return updated_sweet


@router.delete("/{sweet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete a sweet (Admin only)
    
    Args:
        sweet_id: ID of sweet to delete
        db: Database session
        admin: Current admin user (from dependency)
    
    Raises:
        HTTPException: If sweet not found
    """
    deleted = SweetService.delete_sweet(db, sweet_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sweet with id {sweet_id} not found"
        )
    
    return None
