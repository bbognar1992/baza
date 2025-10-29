"""
User API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from services.user_service import UserService
from core.security import create_access_token, get_current_active_user
from core.config import settings

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    return UserService(db)


@router.get("/", response_model=UserList)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None, description="Filter by role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users with pagination and filtering"""
    # Build filters
    filters = {}
    if role:
        filters['role'] = role
    if department:
        filters['department'] = department
    if status:
        filters['status'] = status
    
    # Use search if provided, otherwise use filters
    if search:
        users = user_service.search_users(search, skip, limit)
        total = len(users)  # For search, we'll return the actual count
    else:
        result = user_service.get_users_paginated(skip, limit, **filters)
        users = result['users']
        total = result['total']
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific user by ID"""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate, 
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new user"""
    db_user = user_service.create_user(user)
    return UserResponse.from_orm(db_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update a user"""
    user = user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a user"""
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.get("/role/{role}", response_model=UserList)
async def get_users_by_role(
    role: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get users by role"""
    users = user_service.get_users_by_role(role, skip, limit)
    total = user_service.count(role=role)
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/department/{department}", response_model=UserList)
async def get_users_by_department(
    department: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get users by department"""
    users = user_service.get_users_by_department(department, skip, limit)
    total = user_service.count(department=department)
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/active/", response_model=UserList)
async def get_active_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get active users only"""
    users = user_service.get_active_users(skip, limit)
    total = user_service.count(status='Active')
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/stats/")
async def get_user_statistics(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get user statistics"""
    return user_service.get_user_statistics()


@router.post("/authenticate/")
async def authenticate_user(
    email: str,
    password: str,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user with email and password"""
    user = user_service.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
        "message": "Authentication successful"
    }
