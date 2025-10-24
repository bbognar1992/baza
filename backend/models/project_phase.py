"""
Project Phase model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ProjectPhase(Base, TimestampMixin):
    """Project-specific phase instances"""
    __tablename__ = 'project_phases'
    
    project_phase_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    phase_id = Column(Integer, ForeignKey('phases.phase_id'), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default='Not Started')
    progress_percent = Column(Integer, default=0)
    
    # Relationships
    project = relationship("Project", back_populates="project_phases")
    phase = relationship("Phase", back_populates="project_phases")
    project_tasks = relationship("ProjectTask", back_populates="project_phase", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')", name='ck_project_phase_status'),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name='ck_project_phase_progress'),
    )
    
    def __repr__(self):
        return f"<ProjectPhase(id={self.project_phase_id}, project_id={self.project_id}, phase_id={self.phase_id})>"
    
    @property
    def is_started(self):
        """Check if phase is started"""
        return self.status in ['In Progress', 'Completed']
    
    @property
    def is_completed(self):
        """Check if phase is completed"""
        return self.status == 'Completed'
    
    @property
    def duration_days(self):
        """Calculate phase duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def task_count(self):
        """Get number of tasks in this project phase"""
        return len(self.project_tasks) if self.project_tasks else 0
    
    @property
    def completed_task_count(self):
        """Get number of completed tasks"""
        if self.project_tasks:
            return sum(1 for task in self.project_tasks if task.is_completed)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_phase_id': self.project_phase_id,
            'project_id': self.project_id,
            'phase_id': self.phase_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'progress_percent': self.progress_percent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
