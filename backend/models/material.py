"""
Material models for ÉpítAI Construction Management System
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, CheckConstraint, Date
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Material(Base, TimestampMixin):
    """Construction materials and supplies"""
    __tablename__ = 'materials'
    
    material_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resources.resource_id'))
    name = Column(String(300), nullable=False)
    category = Column(String(100))
    unit = Column(String(50))
    unit_cost = Column(Numeric(10, 2))
    description = Column(Text)
    supplier = Column(String(200))
    vendor_contact = Column(String(255))
    lead_time_days = Column(Integer, default=0)
    minimum_order = Column(Integer, default=1)
    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    status = Column(String(50), default='Available')
    
    # Relationships
    supplier_resource = relationship("Resource", back_populates="materials")
    project_materials = relationship("ProjectMaterial", back_populates="material")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Available', 'Out of Stock', 'Discontinued')", name='ck_material_status'),
    )
    
    def __repr__(self):
        return f"<Material(id={self.material_id}, name='{self.name}', category='{self.category}')>"
    
    @property
    def is_available(self):
        """Check if material is available"""
        return self.status == 'Available'
    
    @property
    def is_low_stock(self):
        """Check if material is low in stock"""
        return self.current_stock <= self.reorder_level
    
    @property
    def needs_reorder(self):
        """Check if material needs reordering"""
        return self.current_stock <= self.reorder_level and self.status == 'Available'
    
    @property
    def total_value(self):
        """Calculate total value of current stock"""
        if self.unit_cost and self.current_stock:
            return float(self.unit_cost * self.current_stock)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'material_id': self.material_id,
            'resource_id': self.resource_id,
            'name': self.name,
            'category': self.category,
            'unit': self.unit,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'description': self.description,
            'supplier': self.supplier,
            'vendor_contact': self.vendor_contact,
            'lead_time_days': self.lead_time_days,
            'minimum_order': self.minimum_order,
            'current_stock': self.current_stock,
            'reorder_level': self.reorder_level,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectMaterial(Base, TimestampMixin):
    """Project material requirements (many-to-many)"""
    __tablename__ = 'project_materials'
    
    project_material_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    material_id = Column(Integer, ForeignKey('materials.material_id'), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(12, 2))  # Generated column: quantity * unit_cost
    assigned_date = Column(Date, default='CURRENT_DATE')
    status = Column(String(50), default='Planned')
    
    # Relationships
    project = relationship("Project", back_populates="materials")
    material = relationship("Material", back_populates="project_materials")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Planned', 'Ordered', 'Delivered', 'Used')", name='ck_project_material_status'),
    )
    
    def __repr__(self):
        return f"<ProjectMaterial(id={self.project_material_id}, project_id={self.project_id}, material_id={self.material_id})>"
    
    @property
    def is_ordered(self):
        """Check if material is ordered"""
        return self.status in ['Ordered', 'Delivered', 'Used']
    
    @property
    def is_delivered(self):
        """Check if material is delivered"""
        return self.status in ['Delivered', 'Used']
    
    @property
    def is_used(self):
        """Check if material is used"""
        return self.status == 'Used'
    
    def calculate_total_cost(self):
        """Calculate total cost for this material assignment"""
        if self.unit_cost and self.quantity:
            return float(self.unit_cost * self.quantity)
        return 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'project_material_id': self.project_material_id,
            'project_id': self.project_id,
            'material_id': self.material_id,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
