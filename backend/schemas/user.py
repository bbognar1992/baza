"""
Pydantic schemas for User model
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, datetime


class UserBase(BaseModel):
    """Base user schema"""
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    hire_date: Optional[date] = None
    status: str = "Active"
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema for user list response"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
