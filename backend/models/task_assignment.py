"""
Task Assignment model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class TaskAssignment(Base, TimestampMixin):
    """Resource assignments to specific tasks"""
    __tablename__ = 'task_assignments'
    
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    project_task_id = Column(Integer, ForeignKey('project_tasks.project_task_id', ondelete='CASCADE'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.resource_id', ondelete='CASCADE'), nullable=False)
    assigned_date = Column(Date, default='CURRENT_DATE')
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default='Assigned')
    hours_worked = Column(Numeric(8, 2), default=0)
    notes = Column(Text)
    
    # Relationships
    project_task = relationship("ProjectTask", back_populates="task_assignments")
    resource = relationship("Resource", back_populates="task_assignments")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Assigned', 'In Progress', 'Completed', 'Cancelled')", name='ck_task_assignment_status'),
        UniqueConstraint('project_task_id', 'resource_id', name='uq_task_assignment'),
    )
    
    def __repr__(self):
        return f"<TaskAssignment(id={self.assignment_id}, project_task_id={self.project_task_id}, resource_id={self.resource_id})>"
    
    @property
    def is_active(self):
        """Check if assignment is active"""
        return self.status in ['Assigned', 'In Progress']
    
    @property
    def is_completed(self):
        """Check if assignment is completed"""
        return self.status == 'Completed'
    
    @property
    def duration_days(self):
        """Calculate assignment duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def total_cost(self):
        """Calculate total cost for this assignment"""
        if self.resource and self.resource.hourly_rate and self.hours_worked:
            return float(self.resource.hourly_rate * self.hours_worked)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'assignment_id': self.assignment_id,
            'project_task_id': self.project_task_id,
            'resource_id': self.resource_id,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'hours_worked': float(self.hours_worked) if self.hours_worked else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
