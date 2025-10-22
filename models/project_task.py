"""
Project Task model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base, db, TimestampMixin

class ProjectTask(Base, TimestampMixin):
    """Project-specific task instances"""
    __tablename__ = 'project_tasks'
    
    project_task_id = db(Integer, primary_key=True, autoincrement=True)
    project_phase_id = db(Integer, ForeignKey('project_phases.project_phase_id', ondelete='CASCADE'), nullable=False)
    task_id = db(Integer, ForeignKey('tasks.task_id'), nullable=False)
    start_date = db(Date)
    end_date = db(Date)
    status = db(String(50), default='Not Started')
    progress_percent = db(Integer, default=0)
    is_completed = db(Boolean, default=False)
    completed_date = db(Date)
    
    # Relationships
    project_phase = relationship("ProjectPhase", back_populates="project_tasks")
    task = relationship("Task", back_populates="project_tasks")
    task_assignments = relationship("TaskAssignment", back_populates="project_task", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')", name='ck_project_task_status'),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name='ck_project_task_progress'),
    )
    
    def __repr__(self):
        return f"<ProjectTask(id={self.project_task_id}, project_phase_id={self.project_phase_id}, task_id={self.task_id})>"
    
    @property
    def is_started(self):
        """Check if task is started"""
        return self.status in ['In Progress', 'Completed']
    
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == 'Completed' or self.is_completed
    
    @property
    def duration_days(self):
        """Calculate task duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def assigned_resources_count(self):
        """Get number of assigned resources"""
        return len(self.task_assignments) if self.task_assignments else 0
    
    @property
    def total_hours_worked(self):
        """Get total hours worked on this task"""
        if self.task_assignments:
            return sum(assignment.hours_worked for assignment in self.task_assignments)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_task_id': self.project_task_id,
            'project_phase_id': self.project_phase_id,
            'task_id': self.task_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'progress_percent': self.progress_percent,
            'is_completed': self.is_completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
