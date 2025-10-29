"""
Resource model for Pontum Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Resource(Base, TimestampMixin):
    """Human resources including employees, subcontractors, and suppliers"""
    __tablename__ = 'resources'
    
    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    position = Column(String(100))
    profession_type_id = Column(Integer, ForeignKey('profession_types.profession_type_id'))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    skills = Column(Text)
    hourly_rate = Column(Numeric(10, 2), default=0)
    availability = Column(String(50), default='Elérhető')
    experience_years = Column(Integer, default=0)
    
    # Relationships
    profession_type = relationship("ProfessionType", back_populates="resources")
    project_memberships = relationship("ProjectMember", back_populates="resource")
    task_assignments = relationship("TaskAssignment", back_populates="resource")
    materials = relationship("Material", back_populates="supplier_resource")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("type IN ('Alkalmazott', 'Alvállalkozó', 'Beszállító')", name='ck_resource_type'),
        CheckConstraint("availability IN ('Elérhető', 'Foglalt', 'Szabadságon', 'Betegszabadság')", name='ck_resource_availability'),
    )
    
    def __repr__(self):
        return f"<Resource(id={self.resource_id}, name='{self.name}', type='{self.type}')>"
    
    @property
    def is_available(self):
        """Check if resource is available"""
        return self.availability == 'Elérhető'
    
    @property
    def is_employee(self):
        """Check if resource is an employee"""
        return self.type == 'Alkalmazott'
    
    @property
    def is_subcontractor(self):
        """Check if resource is a subcontractor"""
        return self.type == 'Alvállalkozó'
    
    @property
    def is_supplier(self):
        """Check if resource is a supplier"""
        return self.type == 'Beszállító'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'resource_id': self.resource_id,
            'type': self.type,
            'name': self.name,
            'position': self.position,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'skills': self.skills,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else 0,
            'availability': self.availability,
            'experience_years': self.experience_years,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
