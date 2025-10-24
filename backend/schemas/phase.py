"""
Pydantic schemas for Phase models
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime


class PhaseBase(BaseModel):
    """Base phase schema"""
    project_type_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    order_sequence: int
    total_duration_days: int = 0


class PhaseCreate(PhaseBase):
    """Schema for creating a phase"""
    pass


class PhaseUpdate(BaseModel):
    """Schema for updating a phase"""
    project_type_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    order_sequence: Optional[int] = None
    total_duration_days: Optional[int] = None


class PhaseResponse(PhaseBase):
    """Schema for phase response"""
    phase_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectPhaseBase(BaseModel):
    """Base project phase schema"""
    phase_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Not Started"
    progress_percent: int = 0

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


class ProjectPhaseCreate(ProjectPhaseBase):
    """Schema for creating a project phase"""
    pass


class ProjectPhaseUpdate(BaseModel):
    """Schema for updating a project phase"""
    phase_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None


class ProjectPhaseResponse(ProjectPhaseBase):
    """Schema for project phase response"""
    project_phase_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PhaseList(BaseModel):
    """Schema for phase list response"""
    phases: List[PhaseResponse]
    total: int
    page: int
    size: int
