"""
Phase model for Pontum Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Phase(Base, TimestampMixin):
    """Project phases with their characteristics"""
    __tablename__ = 'phases'
    
    phase_id = Column(Integer, primary_key=True, autoincrement=True)
    project_type_id = Column(Integer, ForeignKey('project_types.project_type_id'))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    order_sequence = Column(Integer, nullable=False)
    total_duration_days = Column(Integer, default=0)
    
    # Relationships
    project_type = relationship("ProjectType", back_populates="phases")
    tasks = relationship("Task", back_populates="phase", cascade="all, delete-orphan")
    project_phases = relationship("ProjectPhase", back_populates="phase")
    
    def __repr__(self):
        return f"<Phase(id={self.phase_id}, name='{self.name}', sequence={self.order_sequence})>"
    
    @property
    def task_count(self):
        """Get number of tasks in this phase"""
        return len(self.tasks) if self.tasks else 0
    
    @property
    def total_required_people(self):
        """Get total required people for this phase"""
        if self.tasks:
            return sum(task.required_people for task in self.tasks)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'phase_id': self.phase_id,
            'project_type_id': self.project_type_id,
            'name': self.name,
            'description': self.description,
            'order_sequence': self.order_sequence,
            'total_duration_days': self.total_duration_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
