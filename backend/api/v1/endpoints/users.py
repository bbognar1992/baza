"""
User API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserList

router = APIRouter()


@router.get("/", response_model=UserList)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return UserList(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        department=user.department,
        hire_date=user.hire_date,
        status=user.status,
        phone=user.phone
    )
    db_user.set_password(user.password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data:
        user.set_password(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
