"""
Pytest configuration and fixtures for testing
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from app.database import get_db, Base
from models.user import User
from schemas.user import UserCreate

# Test database URL (using SQLite in memory for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
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


@pytest.fixture
def sample_user_update_data():
    """Sample user update data for testing"""
    return {
        "first_name": "John Updated",
        "phone": "+9876543210",
        "department": "Engineering"
    }


@pytest.fixture
def created_user(client, sample_user_data):
    """Create a user and return the response"""
    response = client.post("/api/v1/users/", json=sample_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def multiple_users(client, db_session):
    """Create multiple users for testing"""
    users_data = [
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com",
            "password": "password123",
            "role": "Engineer",
            "department": "Engineering",
            "hire_date": "2024-01-01",
            "status": "Active",
            "phone": "+1111111111"
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "password": "password123",
            "role": "Worker",
            "department": "Construction",
            "hire_date": "2024-02-01",
            "status": "Active",
            "phone": "+2222222222"
        },
        {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@example.com",
            "password": "password123",
            "role": "Manager",
            "department": "Management",
            "hire_date": "2024-03-01",
            "status": "Inactive",
            "phone": "+3333333333"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        created_users.append(response.json())
    
    return created_users
