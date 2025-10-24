"""
Pydantic schemas for Project models
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class ProjectLocationBase(BaseModel):
    """Base project location schema"""
    location_name: str
    address: Optional[str] = None
    coordinates_lat: Optional[float] = None
    coordinates_lng: Optional[float] = None


class ProjectLocationCreate(ProjectLocationBase):
    """Schema for creating a project location"""
    pass


class ProjectLocationResponse(ProjectLocationBase):
    """Schema for project location response"""
    project_location_id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberBase(BaseModel):
    """Base project member schema"""
    resource_id: int
    role_in_project: Optional[str] = None
    assigned_date: Optional[date] = None


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for creating a project member"""
    pass


class ProjectMemberResponse(ProjectMemberBase):
    """Schema for project member response"""
    project_member_id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema"""
    project_name: str
    client_name: Optional[str] = None
    project_type_id: Optional[int] = None
    status: str
    start_date: date
    end_date: date
    budget: Optional[Decimal] = None
    project_manager_id: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    progress_percent: int = 0
    size_sqm: Optional[int] = None
    project_code: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['Tervezés alatt', 'Folyamatban', 'Késésben', 'Lezárt']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['Alacsony', 'Közepes', 'Magas']
            if v not in allowed_priorities:
                raise ValueError(f'Priority must be one of: {allowed_priorities}')
        return v

    @validator('progress_percent')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Progress must be between 0 and 100')
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    project_type_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    project_manager_id: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    progress_percent: Optional[int] = None
    size_sqm: Optional[int] = None
    project_code: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    """Schema for detailed project response with relationships"""
    locations: List[ProjectLocationResponse] = []
    members: List[ProjectMemberResponse] = []


class ProjectList(BaseModel):
    """Schema for project list response"""
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int
