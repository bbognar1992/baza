"""
Profession Type model for Pontum Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ProfessionType(Base, TimestampMixin):
    """Job categories and skill levels"""
    __tablename__ = 'profession_types'
    
    profession_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    level = Column(String(50), nullable=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="profession_type")
    resources = relationship("Resource", back_populates="profession_type")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("level IN ('Szakmunkás', 'Vezető', 'Szakértő')", name='ck_profession_level'),
    )
    
    def __repr__(self):
        return f"<ProfessionType(id={self.profession_type_id}, name='{self.name}', level='{self.level}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'profession_type_id': self.profession_type_id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
