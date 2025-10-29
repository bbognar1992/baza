"""
Task model for Pontum Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Task(Base, TimestampMixin):
    """Individual tasks within phases"""
    __tablename__ = 'tasks'
    
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    phase_id = Column(Integer, ForeignKey('phases.phase_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    profession_type_id = Column(Integer, ForeignKey('profession_types.profession_type_id'))
    duration_days = Column(Integer, default=1)
    required_people = Column(Integer, default=1)
    order_sequence = Column(Integer, nullable=False)
    
    # Relationships
    phase = relationship("Phase", back_populates="tasks")
    profession_type = relationship("ProfessionType", back_populates="tasks")
    project_tasks = relationship("ProjectTask", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id={self.task_id}, name='{self.name}', phase_id={self.phase_id})>"
    
    @property
    def is_ai_task(self):
        """Check if this is an AI-assisted task"""
        return self.name.startswith('[AI]')
    
    @property
    def total_hours(self):
        """Calculate total hours needed (assuming 8 hours per day)"""
        return self.duration_days * 8
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'phase_id': self.phase_id,
            'name': self.name,
            'description': self.description,
            'profession_type_id': self.profession_type_id,
            'duration_days': self.duration_days,
            'required_people': self.required_people,
            'order_sequence': self.order_sequence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
