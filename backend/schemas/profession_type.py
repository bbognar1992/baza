"""
Pydantic schemas for ProfessionType model
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProfessionTypeBase(BaseModel):
    """Base profession type schema"""
    name: str
    description: Optional[str] = None
    level: str

    @validator('level')
    def validate_level(cls, v):
        allowed_levels = ['Szakmunkás', 'Vezető', 'Szakértő']
        if v not in allowed_levels:
            raise ValueError(f'Level must be one of: {allowed_levels}')
        return v


class ProfessionTypeCreate(ProfessionTypeBase):
    """Schema for creating a profession type"""
    pass


class ProfessionTypeUpdate(BaseModel):
    """Schema for updating a profession type"""
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None


class ProfessionTypeResponse(ProfessionTypeBase):
    """Schema for profession type response"""
    profession_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfessionTypeList(BaseModel):
    """Schema for profession type list response"""
    profession_types: list[ProfessionTypeResponse]
    total: int
    page: int
    size: int
