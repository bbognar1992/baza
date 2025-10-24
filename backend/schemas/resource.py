"""
Pydantic schemas for Resource model
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ResourceBase(BaseModel):
    """Base resource schema"""
    type: str
    name: str
    position: Optional[str] = None
    profession_type_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Decimal = 0
    availability: str = "Elérhető"
    experience_years: int = 0

    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['Alkalmazott', 'Alvállalkozó', 'Beszállító']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        return v

    @validator('availability')
    def validate_availability(cls, v):
        allowed_availabilities = ['Elérhető', 'Foglalt', 'Szabadságon', 'Betegszabadság']
        if v not in allowed_availabilities:
            raise ValueError(f'Availability must be one of: {allowed_availabilities}')
        return v


class ResourceCreate(ResourceBase):
    """Schema for creating a resource"""
    pass


class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    type: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    profession_type_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    availability: Optional[str] = None
    experience_years: Optional[int] = None


class ResourceResponse(ResourceBase):
    """Schema for resource response"""
    resource_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceList(BaseModel):
    """Schema for resource list response"""
    resources: list[ResourceResponse]
    total: int
    page: int
    size: int
