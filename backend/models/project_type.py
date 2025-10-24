"""
Project Type model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ProjectType(Base, TimestampMixin):
    """Types of construction projects"""
    __tablename__ = 'project_types'
    
    project_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    projects = relationship("Project", back_populates="project_type")
    phases = relationship("Phase", back_populates="project_type")
    
    def __repr__(self):
        return f"<ProjectType(id={self.project_type_id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_type_id': self.project_type_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
