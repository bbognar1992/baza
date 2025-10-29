"""
Test helper utilities
"""

import json
from typing import Dict, Any, List
from datetime import date, datetime


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user_data(
        first_name: str = "John",
        last_name: str = "Doe",
        email: str = "john.doe@example.com",
        password: str = "testpassword123",
        role: str = "Manager",
        department: str = "Construction",
        hire_date: str = "2024-01-01",
        status: str = "Active",
        phone: str = "+1234567890"
    ) -> Dict[str, Any]:
        """Create user data for testing"""
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "role": role,
            "department": department,
            "hire_date": hire_date,
            "status": status,
            "phone": phone
        }
    
    @staticmethod
    def create_user_update_data(
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        role: str = None,
        department: str = None,
        hire_date: str = None,
        status: str = None,
        phone: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Create user update data for testing"""
        data = {}
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if email is not None:
            data["email"] = email
        if role is not None:
            data["role"] = role
        if department is not None:
            data["department"] = department
        if hire_date is not None:
            data["hire_date"] = hire_date
        if status is not None:
            data["status"] = status
        if phone is not None:
            data["phone"] = phone
        if password is not None:
            data["password"] = password
        return data
    
    @staticmethod
    def create_multiple_users_data(count: int = 3) -> List[Dict[str, Any]]:
        """Create multiple user data for testing"""
        users = []
        for i in range(count):
            user_data = TestDataFactory.create_user_data(
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
                role="Worker" if i % 2 == 0 else "Manager"
            )
            users.append(user_data)
        return users


class AssertionHelpers:
    """Helper methods for test assertions"""
    
    @staticmethod
    def assert_user_response_structure(response_data: Dict[str, Any]) -> None:
        """Assert that user response has correct structure"""
        required_fields = [
            "user_id", "first_name", "last_name", "email", "role",
            "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(response_data["user_id"], int)
        assert isinstance(response_data["first_name"], str)
        assert isinstance(response_data["last_name"], str)
        assert isinstance(response_data["email"], str)
        assert isinstance(response_data["role"], str)
    
    @staticmethod
    def assert_user_list_response_structure(response_data: Dict[str, Any]) -> None:
        """Assert that user list response has correct structure"""
        required_fields = ["users", "total", "page", "size"]
        
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
        
        assert isinstance(response_data["users"], list)
        assert isinstance(response_data["total"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["size"], int)
        
        # If there are users, check their structure
        if response_data["users"]:
            AssertionHelpers.assert_user_response_structure(response_data["users"][0])
    
    @staticmethod
    def assert_error_response_structure(response_data: Dict[str, Any]) -> None:
        """Assert that error response has correct structure"""
        assert "detail" in response_data, "Error response missing 'detail' field"
        assert isinstance(response_data["detail"], str)
        assert len(response_data["detail"]) > 0, "Error detail should not be empty"


class DatabaseHelpers:
    """Helper methods for database operations in tests"""
    
    @staticmethod
    def count_users_in_db(db_session) -> int:
        """Count users in database"""
        from models.user import User
        return db_session.query(User).count()
    
    @staticmethod
    def get_user_by_email_from_db(db_session, email: str):
        """Get user by email from database"""
        from models.user import User
        return db_session.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id_from_db(db_session, user_id: int):
        """Get user by ID from database"""
        from models.user import User
        return db_session.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def clear_all_users(db_session) -> None:
        """Clear all users from database"""
        from models.user import User
        db_session.query(User).delete()
        db_session.commit()


class MockData:
    """Mock data for testing"""
    
    VALID_USER_DATA = {
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
    
    INVALID_USER_DATA = {
        "first_name": "John",
        # Missing required fields: last_name, email, password, role
    }
    
    SHORT_PASSWORD_DATA = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "123",  # Too short
        "role": "Manager"
    }
    
    DUPLICATE_EMAIL_DATA = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "john.doe@example.com",  # Same as VALID_USER_DATA
        "password": "testpassword123",
        "role": "Worker"
    }
