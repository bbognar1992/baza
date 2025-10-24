"""
Base service class with common functionality
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService:
    """Base service class with common CRUD operations"""
    
    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class
    
    def create(self, **kwargs) -> T:
        """Create a new record"""
        try:
            instance = self.model_class(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID"""
        try:
            return self.db.query(self.model_class).filter(
                getattr(self.model_class, f"{self.model_class.__tablename__.rstrip('s')}_id") == id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {e}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Get all records with pagination and filtering"""
        try:
            query = self.db.query(self.model_class)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field) and value is not None:
                    query = query.filter(getattr(self.model_class, field) == value)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} list: {e}")
            raise
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            for field, value in kwargs.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model_class.__name__} {id}: {e}")
            raise
    
    def delete(self, id: int) -> bool:
        """Delete a record"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} {id}: {e}")
            raise
    
    def count(self, **filters) -> int:
        """Count records with optional filters"""
        try:
            query = self.db.query(self.model_class)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field) and value is not None:
                    query = query.filter(getattr(self.model_class, field) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise
