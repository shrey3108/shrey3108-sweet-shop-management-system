"""
SQLAlchemy Sweet model
"""
from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class Sweet(Base):
    """
    Sweet model for sweet shop inventory
    """
    __tablename__ = "sweets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Sweet(id={self.id}, name={self.name}, category={self.category}, price={self.price})>"
