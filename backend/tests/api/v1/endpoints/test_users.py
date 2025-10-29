"""
Comprehensive unit tests for User API endpoints
"""

import unittest
import json
import os
import sys
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from main import app
from app.database import get_db, Base
from models.user import User
from schemas.user import UserCreate, UserUpdate


class TestUserAPI(unittest.TestCase):
    """Test cases for User API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with database"""
        # Import here to avoid circular imports
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create test database
        cls.engine = create_engine("sqlite:///./test_users.db", connect_args={"check_same_thread": False})
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        # Create tables
        Base.metadata.create_all(bind=cls.engine)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Drop tables
        Base.metadata.drop_all(bind=cls.engine)
    
    def setUp(self):
        """Set up for each test"""
        # Create fresh database session
        self.db = self.TestingSessionLocal()
        
        # Override database dependency
        def override_get_db():
            try:
                yield self.db
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Create test client
        self.client = TestClient(app)
        
        # Clear any existing users
        self.db.query(User).delete()
        self.db.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
        app.dependency_overrides.clear()
    
    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager",
            "department": "Construction",
            "hire_date": "2024-01-01",
            "status": "Active",
            "phone": "+1234567890"
        }
        
        response = self.client.post("/api/v1/users/", json=user_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("user_id", data)
        self.assertEqual(data["first_name"], user_data["first_name"])
        self.assertEqual(data["last_name"], user_data["last_name"])
        self.assertEqual(data["email"], user_data["email"])
        self.assertEqual(data["role"], user_data["role"])
        self.assertEqual(data["department"], user_data["department"])
        self.assertEqual(data["status"], user_data["status"])
        self.assertEqual(data["phone"], user_data["phone"])
        
        # Verify user was created in database
        db_user = self.db.query(User).filter(User.email == user_data["email"]).first()
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.first_name, user_data["first_name"])
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager"
        }
        
        # Create first user
        response1 = self.client.post("/api/v1/users/", json=user_data)
        self.assertEqual(response1.status_code, 200)
        
        # Try to create user with same email
        response2 = self.client.post("/api/v1/users/", json=user_data)
        self.assertEqual(response2.status_code, 400)
        self.assertIn("Email already registered", response2.json()["detail"])
    
    def test_create_user_invalid_data(self):
        """Test user creation with invalid data"""
        # Test missing required fields
        invalid_data = {
            "first_name": "John",
            # Missing last_name, email, password, role
        }
        
        response = self.client.post("/api/v1/users/", json=invalid_data)
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_create_user_short_password(self):
        """Test user creation with short password"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "123",  # Too short
            "role": "Manager"
        }
        
        response = self.client.post("/api/v1/users/", json=user_data)
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_get_users_empty(self):
        """Test getting users when none exist"""
        response = self.client.get("/api/v1/users/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["total"], 0)
        self.assertEqual(len(data["users"]), 0)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["size"], 20)
    
    def test_get_users_with_data(self):
        """Test getting users with data"""
        # Create test users
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Engineer",
                "department": "Engineering"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker",
                "department": "Construction"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        response = self.client.get("/api/v1/users/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["users"]), 2)
    
    def test_get_users_pagination(self):
        """Test user pagination"""
        # Create 5 test users
        for i in range(5):
            user_data = {
                "first_name": f"User{i}",
                "last_name": "Test",
                "email": f"user{i}@example.com",
                "password": "password123",
                "role": "Worker"
            }
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test first page
        response = self.client.get("/api/v1/users/?skip=0&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["users"]), 2)
        self.assertEqual(data["page"], 1)
        
        # Test second page
        response = self.client.get("/api/v1/users/?skip=2&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["users"]), 2)
        self.assertEqual(data["page"], 2)
    
    def test_get_users_filtering(self):
        """Test user filtering by role and department"""
        # Create users with different roles and departments
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Manager",
                "department": "Engineering"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker",
                "department": "Construction"
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "role": "Manager",
                "department": "Construction"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test filtering by role
        response = self.client.get("/api/v1/users/?role=Manager")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        for user in data["users"]:
            self.assertEqual(user["role"], "Manager")
        
        # Test filtering by department
        response = self.client.get("/api/v1/users/?department=Construction")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        for user in data["users"]:
            self.assertEqual(user["department"], "Construction")
    
    def test_get_users_search(self):
        """Test user search functionality"""
        # Create test users
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice.smith@example.com",
                "password": "password123",
                "role": "Engineer"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob.johnson@example.com",
                "password": "password123",
                "role": "Worker"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test search by first name
        response = self.client.get("/api/v1/users/?search=Alice")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["users"]), 1)
        self.assertEqual(data["users"][0]["first_name"], "Alice")
        
        # Test search by email
        response = self.client.get("/api/v1/users/?search=bob.johnson")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["users"]), 1)
        self.assertEqual(data["users"][0]["email"], "bob.johnson@example.com")
    
    def test_get_user_by_id_success(self):
        """Test getting user by ID"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager"
        }
        
        create_response = self.client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["user_id"]
        
        # Get user by ID
        response = self.client.get(f"/api/v1/users/{user_id}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], user_id)
        self.assertEqual(data["first_name"], user_data["first_name"])
        self.assertEqual(data["email"], user_data["email"])
    
    def test_get_user_by_id_not_found(self):
        """Test getting non-existent user by ID"""
        response = self.client.get("/api/v1/users/99999")
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json()["detail"])
    
    def test_update_user_success(self):
        """Test successful user update"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager",
            "department": "Construction"
        }
        
        create_response = self.client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["user_id"]
        
        # Update user
        update_data = {
            "first_name": "John Updated",
            "phone": "+9876543210",
            "department": "Engineering"
        }
        
        response = self.client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "John Updated")
        self.assertEqual(data["phone"], "+9876543210")
        self.assertEqual(data["department"], "Engineering")
        # Unchanged fields should remain the same
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["email"], "john.doe@example.com")
    
    def test_update_user_password(self):
        """Test updating user password"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "oldpassword123",
            "role": "Manager"
        }
        
        create_response = self.client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["user_id"]
        
        # Update password
        update_data = {
            "password": "newpassword123"
        }
        
        response = self.client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify password was updated by checking authentication
        auth_response = self.client.post(
            "/api/v1/users/authenticate/",
            params={"email": "john.doe@example.com", "password": "newpassword123"}
        )
        self.assertEqual(auth_response.status_code, 200)
    
    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        update_data = {
            "first_name": "Updated"
        }
        
        response = self.client.put("/api/v1/users/99999", json=update_data)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json()["detail"])
    
    def test_update_user_duplicate_email(self):
        """Test updating user with duplicate email"""
        # Create two users
        user1_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "role": "Manager"
        }
        
        user2_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "password": "password123",
            "role": "Worker"
        }
        
        create_response1 = self.client.post("/api/v1/users/", json=user1_data)
        create_response2 = self.client.post("/api/v1/users/", json=user2_data)
        
        user1_id = create_response1.json()["user_id"]
        
        # Try to update user1 with user2's email
        update_data = {
            "email": "jane.smith@example.com"
        }
        
        response = self.client.put(f"/api/v1/users/{user1_id}", json=update_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email already registered", response.json()["detail"])
    
    def test_delete_user_success(self):
        """Test successful user deletion"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager"
        }
        
        create_response = self.client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["user_id"]
        
        # Delete user
        response = self.client.delete(f"/api/v1/users/{user_id}")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted successfully", response.json()["message"])
        
        # Verify user was deleted
        get_response = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        response = self.client.delete("/api/v1/users/99999")
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json()["detail"])
    
    def test_get_users_by_role(self):
        """Test getting users by role"""
        # Create users with different roles
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Manager"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker"
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "role": "Manager"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test getting managers
        response = self.client.get("/api/v1/users/role/Manager")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        for user in data["users"]:
            self.assertEqual(user["role"], "Manager")
    
    def test_get_users_by_department(self):
        """Test getting users by department"""
        # Create users with different departments
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Engineer",
                "department": "Engineering"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker",
                "department": "Construction"
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "role": "Manager",
                "department": "Engineering"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test getting engineering department users
        response = self.client.get("/api/v1/users/department/Engineering")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        for user in data["users"]:
            self.assertEqual(user["department"], "Engineering")
    
    def test_get_active_users(self):
        """Test getting active users only"""
        # Create users with different statuses
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Engineer",
                "status": "Active"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker",
                "status": "Inactive"
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "role": "Manager",
                "status": "Active"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test getting active users
        response = self.client.get("/api/v1/users/active/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        for user in data["users"]:
            self.assertEqual(user["status"], "Active")
    
    def test_get_user_statistics(self):
        """Test getting user statistics"""
        # Create users with different roles and statuses
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "password": "password123",
                "role": "Manager",
                "status": "Active"
            },
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob@example.com",
                "password": "password123",
                "role": "Worker",
                "status": "Active"
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie@example.com",
                "password": "password123",
                "role": "Manager",
                "status": "Inactive"
            }
        ]
        
        for user_data in users_data:
            self.client.post("/api/v1/users/", json=user_data)
        
        # Test getting statistics
        response = self.client.get("/api/v1/users/stats/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["total_users"], 3)
        self.assertEqual(data["active_users"], 2)
        self.assertEqual(data["inactive_users"], 1)
        self.assertEqual(data["terminated_users"], 0)
        self.assertIn("role_distribution", data)
        self.assertEqual(data["role_distribution"]["Manager"], 2)
        self.assertEqual(data["role_distribution"]["Worker"], 1)
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager"
        }
        
        self.client.post("/api/v1/users/", json=user_data)
        
        # Authenticate user
        response = self.client.post(
            "/api/v1/users/authenticate/",
            params={"email": "john.doe@example.com", "password": "testpassword123"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], "john.doe@example.com")
        self.assertIn("Authentication successful", data["message"])
    
    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        # Create a user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "testpassword123",
            "role": "Manager"
        }
        
        self.client.post("/api/v1/users/", json=user_data)
        
        # Try to authenticate with wrong password
        response = self.client.post(
            "/api/v1/users/authenticate/",
            params={"email": "john.doe@example.com", "password": "wrongpassword"}
        )
        
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json()["detail"])
    
    def test_authenticate_user_nonexistent_email(self):
        """Test authentication with non-existent email"""
        response = self.client.post(
            "/api/v1/users/authenticate/",
            params={"email": "nonexistent@example.com", "password": "password123"}
        )
        
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json()["detail"])


if __name__ == '__main__':
    unittest.main()
