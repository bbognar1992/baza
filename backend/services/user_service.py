"""
User service for ÉpítAI Construction Management System
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
import logging

from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from .base import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Service class for user management operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with validation"""
        try:
            # Check if email already exists
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="Email already registered"
                )
            
            # Create user data dict
            user_dict = user_data.dict()
            password = user_dict.pop('password')
            
            # Create user instance
            user = User(**user_dict)
            user.set_password(password)
            
            # Save to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created user: {user.email}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating user {user_data.email}: {e}")
            raise HTTPException(
                status_code=400,
                detail="User creation failed due to data constraints"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating user {user_data.email}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during user creation"
            )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db.query(User).filter(User.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving user"
            )
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving user"
            )
    
    def get_users_paginated(
        self, 
        skip: int = 0, 
        limit: int = 20,
        **filters
    ) -> Dict[str, Any]:
        """Get paginated list of users with optional filtering"""
        try:
            # Build query
            query = self.db.query(User)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(User, field) and value is not None:
                    query = query.filter(getattr(User, field) == value)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            users = query.offset(skip).limit(limit).all()
            
            return {
                'users': users,
                'total': total,
                'page': skip // limit + 1,
                'size': limit
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting paginated users: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving users"
            )
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user with validation"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Check if email is being changed and if it already exists
            if user_data.email and user_data.email != user.email:
                existing_user = self.get_user_by_email(user_data.email)
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail="Email already registered"
                    )
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            
            # Handle password update
            if 'password' in update_data:
                user.set_password(update_data.pop('password'))
            
            # Update other fields
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user: {user.email}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=400,
                detail="User update failed due to data constraints"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during user update"
            )
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Deleted user: {user.email}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting user {user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during user deletion"
            )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = self.get_user_by_email(email)
            if user and user.check_password(password):
                return user
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error authenticating user {email}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during authentication"
            )
    
    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        try:
            return self.get_all(skip=skip, limit=limit, role=role)
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving users by role"
            )
    
    def get_users_by_department(self, department: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by department"""
        try:
            return self.get_all(skip=skip, limit=limit, department=department)
        except SQLAlchemyError as e:
            logger.error(f"Error getting users by department {department}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving users by department"
            )
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users only"""
        try:
            return self.get_all(skip=skip, limit=limit, status='Active')
        except SQLAlchemyError as e:
            logger.error(f"Error getting active users: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving active users"
            )
    
    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name or email"""
        try:
            query = self.db.query(User).filter(
                (User.first_name.ilike(f"%{search_term}%")) |
                (User.last_name.ilike(f"%{search_term}%")) |
                (User.email.ilike(f"%{search_term}%"))
            )
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching users with term '{search_term}': {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during user search"
            )
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            total_users = self.count()
            active_users = self.count(status='Active')
            inactive_users = self.count(status='Inactive')
            terminated_users = self.count(status='Terminated')
            
            # Get role distribution
            role_stats = {}
            roles = self.db.query(User.role).distinct().all()
            for role_tuple in roles:
                role = role_tuple[0]
                count = self.count(role=role)
                role_stats[role] = count
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'terminated_users': terminated_users,
                'role_distribution': role_stats
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting user statistics: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error retrieving user statistics"
            )
