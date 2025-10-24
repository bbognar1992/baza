"""
Pydantic schemas for Material models
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class MaterialBase(BaseModel):
    """Base material schema"""
    resource_id: Optional[int] = None
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    description: Optional[str] = None
    supplier: Optional[str] = None
    vendor_contact: Optional[str] = None
    lead_time_days: int = 0
    minimum_order: int = 1
    current_stock: int = 0
    reorder_level: int = 0
    status: str = "Available"

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['Available', 'Out of Stock', 'Discontinued']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v


class MaterialCreate(MaterialBase):
    """Schema for creating a material"""
    pass


class MaterialUpdate(BaseModel):
    """Schema for updating a material"""
    resource_id: Optional[int] = None
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    description: Optional[str] = None
    supplier: Optional[str] = None
    vendor_contact: Optional[str] = None
    lead_time_days: Optional[int] = None
    minimum_order: Optional[int] = None
    current_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    status: Optional[str] = None


class MaterialResponse(MaterialBase):
    """Schema for material response"""
    material_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectMaterialBase(BaseModel):
    """Base project material schema"""
    material_id: int
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    assigned_date: Optional[date] = None
    status: str = "Planned"

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['Planned', 'Ordered', 'Delivered', 'Used']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v


class ProjectMaterialCreate(ProjectMaterialBase):
    """Schema for creating a project material"""
    pass


class ProjectMaterialUpdate(BaseModel):
    """Schema for updating a project material"""
    material_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    assigned_date: Optional[date] = None
    status: Optional[str] = None


class ProjectMaterialResponse(ProjectMaterialBase):
    """Schema for project material response"""
    project_material_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialList(BaseModel):
    """Schema for material list response"""
    materials: list[MaterialResponse]
    total: int
    page: int
    size: int
