#!/usr/bin/env python3
"""
Service layer tests for UserService
"""

import unittest
import os
import sys
from datetime import date

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.user import User
from schemas.user import UserCreate, UserUpdate
from services.user_service import UserService


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with database"""
        # Create test database
        cls.engine = create_engine("sqlite:///./test_user_service.db", connect_args={"check_same_thread": False})
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        # Create tables
        Base.metadata.create_all(bind=cls.engine)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Drop tables
        Base.metadata.drop_all(bind=cls.engine)
        # Clean up test database file
        try:
            os.remove("test_user_service.db")
        except OSError:
            pass
    
    def setUp(self):
        """Set up for each test"""
        # Create fresh database session
        self.db = self.TestingSessionLocal()
        self.user_service = UserService(self.db)
        
        # Clear any existing users
        self.db.query(User).delete()
        self.db.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
    
    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager",
            department="Construction",
            hire_date=date(2024, 1, 1),
            status="Active",
            phone="+1234567890"
        )
        
        user = self.user_service.create_user(user_data)
        
        # Check user was created
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertEqual(user.role, "Manager")
        self.assertEqual(user.department, "Construction")
        self.assertEqual(user.status, "Active")
        self.assertEqual(user.phone, "+1234567890")
        
        # Check password was hashed
        self.assertNotEqual(user.password_hash, "testpassword123")
        self.assertTrue(user.check_password("testpassword123"))
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        # Create first user
        self.user_service.create_user(user_data)
        
        # Try to create user with same email
        with self.assertRaises(Exception):  # Should raise HTTPException
            self.user_service.create_user(user_data)
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        created_user = self.user_service.create_user(user_data)
        
        # Get user by ID
        retrieved_user = self.user_service.get_user_by_id(created_user.user_id)
        
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, created_user.user_id)
        self.assertEqual(retrieved_user.email, "john.doe@example.com")
    
    def test_get_user_by_id_not_found(self):
        """Test getting non-existent user by ID"""
        retrieved_user = self.user_service.get_user_by_id(99999)
        self.assertIsNone(retrieved_user)
    
    def test_get_user_by_email(self):
        """Test getting user by email"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        self.user_service.create_user(user_data)
        
        # Get user by email
        retrieved_user = self.user_service.get_user_by_email("john.doe@example.com")
        
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, "john.doe@example.com")
        self.assertEqual(retrieved_user.first_name, "John")
    
    def test_update_user(self):
        """Test updating user"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager",
            department="Construction"
        )
        
        created_user = self.user_service.create_user(user_data)
        
        # Update user
        update_data = UserUpdate(
            first_name="John Updated",
            phone="+9876543210",
            department="Engineering"
        )
        
        updated_user = self.user_service.update_user(created_user.user_id, update_data)
        
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.first_name, "John Updated")
        self.assertEqual(updated_user.phone, "+9876543210")
        self.assertEqual(updated_user.department, "Engineering")
        # Unchanged fields should remain the same
        self.assertEqual(updated_user.last_name, "Doe")
        self.assertEqual(updated_user.email, "john.doe@example.com")
    
    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        update_data = UserUpdate(first_name="Updated")
        result = self.user_service.update_user(99999, update_data)
        self.assertIsNone(result)
    
    def test_delete_user(self):
        """Test deleting user"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        created_user = self.user_service.create_user(user_data)
        user_id = created_user.user_id
        
        # Delete user
        success = self.user_service.delete_user(user_id)
        
        self.assertTrue(success)
        
        # Verify user was deleted
        deleted_user = self.user_service.get_user_by_id(user_id)
        self.assertIsNone(deleted_user)
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        success = self.user_service.delete_user(99999)
        self.assertFalse(success)
    
    def test_get_users_paginated(self):
        """Test getting paginated users"""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
                password="password123",
                role="Worker"
            )
            self.user_service.create_user(user_data)
        
        # Get paginated users
        result = self.user_service.get_users_paginated(skip=0, limit=3)
        
        self.assertEqual(len(result['users']), 3)
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['size'], 3)
    
    def test_get_users_paginated_with_filters(self):
        """Test getting paginated users with filters"""
        # Create users with different roles
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Manager"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Get users filtered by role
        result = self.user_service.get_users_paginated(skip=0, limit=10, role="Manager")
        
        self.assertEqual(len(result['users']), 2)
        self.assertEqual(result['total'], 2)
        for user in result['users']:
            self.assertEqual(user.role, "Manager")
    
    def test_search_users(self):
        """Test searching users"""
        # Create users
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Engineer"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Search by first name
        results = self.user_service.search_users("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].first_name, "Alice")
        
        # Search by email
        results = self.user_service.search_users("bob@example.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].email, "bob@example.com")
        
        # Search by last name
        results = self.user_service.search_users("Brown")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].last_name, "Brown")
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        self.user_service.create_user(user_data)
        
        # Test correct authentication
        user = self.user_service.authenticate_user("john.doe@example.com", "testpassword123")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "john.doe@example.com")
    
    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password"""
        # Create a user
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="testpassword123",
            role="Manager"
        )
        
        self.user_service.create_user(user_data)
        
        # Test incorrect password
        user = self.user_service.authenticate_user("john.doe@example.com", "wrongpassword")
        self.assertIsNone(user)
    
    def test_authenticate_user_nonexistent_email(self):
        """Test authentication with non-existent email"""
        user = self.user_service.authenticate_user("nonexistent@example.com", "password123")
        self.assertIsNone(user)
    
    def test_get_users_by_role(self):
        """Test getting users by role"""
        # Create users with different roles
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Manager"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Get managers
        managers = self.user_service.get_users_by_role("Manager")
        self.assertEqual(len(managers), 2)
        for user in managers:
            self.assertEqual(user.role, "Manager")
    
    def test_get_users_by_department(self):
        """Test getting users by department"""
        # Create users with different departments
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Engineer", department="Engineering"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker", department="Construction"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager", department="Engineering")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Get engineering department users
        engineers = self.user_service.get_users_by_department("Engineering")
        self.assertEqual(len(engineers), 2)
        for user in engineers:
            self.assertEqual(user.department, "Engineering")
    
    def test_get_active_users(self):
        """Test getting active users only"""
        # Create users with different statuses
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Engineer", status="Active"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker", status="Inactive"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager", status="Active")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Get active users
        active_users = self.user_service.get_active_users()
        self.assertEqual(len(active_users), 2)
        for user in active_users:
            self.assertEqual(user.status, "Active")
    
    def test_get_user_statistics(self):
        """Test getting user statistics"""
        # Create users with different roles and statuses
        users_data = [
            UserCreate(first_name="Alice", last_name="Smith", email="alice@example.com", password="password123", role="Manager", status="Active"),
            UserCreate(first_name="Bob", last_name="Johnson", email="bob@example.com", password="password123", role="Worker", status="Active"),
            UserCreate(first_name="Charlie", last_name="Brown", email="charlie@example.com", password="password123", role="Manager", status="Inactive")
        ]
        
        for user_data in users_data:
            self.user_service.create_user(user_data)
        
        # Get statistics
        stats = self.user_service.get_user_statistics()
        
        self.assertEqual(stats['total_users'], 3)
        self.assertEqual(stats['active_users'], 2)
        self.assertEqual(stats['inactive_users'], 1)
        self.assertEqual(stats['terminated_users'], 0)
        self.assertIn('role_distribution', stats)
        self.assertEqual(stats['role_distribution']['Manager'], 2)
        self.assertEqual(stats['role_distribution']['Worker'], 1)


if __name__ == '__main__':
    unittest.main()
