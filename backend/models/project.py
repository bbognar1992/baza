"""
Project models for Pontum Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Project(Base, TimestampMixin):
    """Individual construction projects"""
    __tablename__ = 'projects'
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(300), nullable=False)
    client_name = Column(String(200))
    project_type_id = Column(Integer, ForeignKey('project_types.project_type_id'))
    status = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Numeric(15, 2))
    project_manager_id = Column(Integer, ForeignKey('users.user_id'))
    location = Column(String(500))
    description = Column(Text)
    priority = Column(String(20))
    progress_percent = Column(Integer, default=0)
    size_sqm = Column(Integer)
    project_code = Column(String(100), unique=True)
    
    # Relationships
    project_type = relationship("ProjectType", back_populates="projects")
    project_manager = relationship("User", back_populates="managed_projects")
    locations = relationship("ProjectLocation", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    project_phases = relationship("ProjectPhase", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("ProjectMaterial", back_populates="project", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Tervezés alatt', 'Folyamatban', 'Késésben', 'Lezárt')", name='ck_project_status'),
        CheckConstraint("priority IN ('Alacsony', 'Közepes', 'Magas')", name='ck_project_priority'),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name='ck_project_progress'),
    )
    
    def __repr__(self):
        return f"<Project(id={self.project_id}, name='{self.project_name}', status='{self.status}')>"
    
    @property
    def is_active(self):
        """Check if project is active"""
        return self.status in ['Tervezés alatt', 'Folyamatban', 'Késésben']
    
    @property
    def is_completed(self):
        """Check if project is completed"""
        return self.status == 'Lezárt'
    
    @property
    def duration_days(self):
        """Calculate project duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def team_size(self):
        """Get team size"""
        return len(self.members) if self.members else 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'client_name': self.client_name,
            'project_type_id': self.project_type_id,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': float(self.budget) if self.budget else None,
            'project_manager_id': self.project_manager_id,
            'location': self.location,
            'description': self.description,
            'priority': self.priority,
            'progress_percent': self.progress_percent,
            'size_sqm': self.size_sqm,
            'project_code': self.project_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectLocation(Base, TimestampMixin):
    """Project locations (many-to-many)"""
    __tablename__ = 'project_locations'
    
    project_location_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    location_name = Column(String(200), nullable=False)
    address = Column(Text)
    coordinates_lat = Column(Numeric(10, 8))
    coordinates_lng = Column(Numeric(11, 8))
    
    # Relationships
    project = relationship("Project", back_populates="locations")
    
    def __repr__(self):
        return f"<ProjectLocation(id={self.project_location_id}, location='{self.location_name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_location_id': self.project_location_id,
            'project_id': self.project_id,
            'location_name': self.location_name,
            'address': self.address,
            'coordinates_lat': float(self.coordinates_lat) if self.coordinates_lat else None,
            'coordinates_lng': float(self.coordinates_lng) if self.coordinates_lng else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProjectMember(Base, TimestampMixin):
    """Project team members (many-to-many)"""
    __tablename__ = 'project_members'
    
    project_member_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.resource_id', ondelete='CASCADE'), nullable=False)
    role_in_project = Column(String(100))
    assigned_date = Column(Date, default='CURRENT_DATE')
    
    # Relationships
    project = relationship("Project", back_populates="members")
    resource = relationship("Resource", back_populates="project_memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('project_id', 'resource_id', name='uq_project_member'),
    )
    
    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, resource_id={self.resource_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_member_id': self.project_member_id,
            'project_id': self.project_id,
            'resource_id': self.resource_id,
            'role_in_project': self.role_in_project,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
