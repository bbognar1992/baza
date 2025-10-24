"""
Pydantic schemas for Task models
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime


class TaskBase(BaseModel):
    """Base task schema"""
    phase_id: int
    name: str
    description: Optional[str] = None
    profession_type_id: Optional[int] = None
    duration_days: int = 1
    required_people: int = 1
    order_sequence: int


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    phase_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    profession_type_id: Optional[int] = None
    duration_days: Optional[int] = None
    required_people: Optional[int] = None
    order_sequence: Optional[int] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    task_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectTaskBase(BaseModel):
    """Base project task schema"""
    task_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Not Started"
    progress_percent: int = 0
    is_completed: bool = False
    completed_date: Optional[date] = None

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v

    @validator('progress_percent')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Progress must be between 0 and 100')
        return v


class ProjectTaskCreate(ProjectTaskBase):
    """Schema for creating a project task"""
    pass


class ProjectTaskUpdate(BaseModel):
    """Schema for updating a project task"""
    task_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None
    is_completed: Optional[bool] = None
    completed_date: Optional[date] = None


class ProjectTaskResponse(ProjectTaskBase):
    """Schema for project task response"""
    project_task_id: int
    project_phase_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskAssignmentBase(BaseModel):
    """Base task assignment schema"""
    resource_id: int
    assigned_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Assigned"
    hours_worked: float = 0
    notes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['Assigned', 'In Progress', 'Completed', 'Cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v


class TaskAssignmentCreate(TaskAssignmentBase):
    """Schema for creating a task assignment"""
    pass


class TaskAssignmentUpdate(BaseModel):
    """Schema for updating a task assignment"""
    resource_id: Optional[int] = None
    assigned_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    hours_worked: Optional[float] = None
    notes: Optional[str] = None


class TaskAssignmentResponse(TaskAssignmentBase):
    """Schema for task assignment response"""
    assignment_id: int
    project_task_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskList(BaseModel):
    """Schema for task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    size: int
