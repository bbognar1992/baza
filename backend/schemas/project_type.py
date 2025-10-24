"""
Pydantic schemas for ProjectType model
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectTypeBase(BaseModel):
    """Base project type schema"""
    name: str
    description: Optional[str] = None


class ProjectTypeCreate(ProjectTypeBase):
    """Schema for creating a project type"""
    pass


class ProjectTypeUpdate(BaseModel):
    """Schema for updating a project type"""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectTypeResponse(ProjectTypeBase):
    """Schema for project type response"""
    project_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectTypeList(BaseModel):
    """Schema for project type list response"""
    project_types: list[ProjectTypeResponse]
    total: int
    page: int
    size: int
