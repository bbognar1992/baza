"""
User model for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """System users and employees"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    department = Column(String(100))
    hire_date = Column(Date)
    status = Column(String(20), default='Active', nullable=False)
    phone = Column(String(20))
    
    # Relationships
    managed_projects = relationship("Project", back_populates="project_manager")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Active', 'Inactive', 'Terminated')", name='ck_user_status'),
    )
    
    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
