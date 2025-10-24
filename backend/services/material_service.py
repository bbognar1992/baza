"""
Material service with business logic for material management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.material import Material, ProjectMaterial
from models.project import Project
from services.base import BaseService


class MaterialService(BaseService):
    """Service for material-related business logic"""
    
    def __init__(self, db: Session):
        super().__init__(db, Material)
    
    def get_low_stock_materials(self) -> List[Material]:
        """Get materials that are low in stock"""
        return self.db.query(Material).filter(
            Material.current_stock <= Material.reorder_level,
            Material.status == 'Available'
        ).all()
    
    def get_materials_by_category(self, category: str) -> List[Material]:
        """Get materials by category"""
        return self.get_all(category=category)
    
    def get_materials_needing_reorder(self) -> List[Material]:
        """Get materials that need to be reordered"""
        return self.db.query(Material).filter(
            Material.current_stock <= Material.reorder_level,
            Material.status == 'Available'
        ).all()
    
    def update_material_stock(self, material_id: int, quantity_change: int, operation: str = 'add') -> Optional[Material]:
        """Update material stock levels"""
        material = self.get_by_id(material_id)
        if not material:
            return None
        
        if operation == 'add':
            material.current_stock += quantity_change
        elif operation == 'subtract':
            material.current_stock = max(0, material.current_stock - quantity_change)
        elif operation == 'set':
            material.current_stock = quantity_change
        
        # Update status based on stock level
        if material.current_stock <= 0:
            material.status = 'Out of Stock'
        elif material.current_stock <= material.reorder_level:
            material.status = 'Available'  # Keep as available but flag for reorder
        
        self.db.commit()
        self.db.refresh(material)
        return material
    
    def get_material_usage_by_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Get material usage for a specific project"""
        project_materials = self.db.query(ProjectMaterial).filter(
            ProjectMaterial.project_id == project_id
        ).all()
        
        usage = []
        for pm in project_materials:
            usage.append({
                'material_id': pm.material_id,
                'material_name': pm.material.name if pm.material else 'Unknown',
                'quantity': float(pm.quantity or 0),
                'unit_cost': float(pm.unit_cost or 0),
                'total_cost': float(pm.total_cost or 0),
                'status': pm.status,
                'assigned_date': pm.assigned_date
            })
        
        return usage
    
    def calculate_material_costs(self, project_id: int) -> Dict[str, Any]:
        """Calculate total material costs for a project"""
        usage = self.get_material_usage_by_project(project_id)
        
        total_cost = sum(item['total_cost'] for item in usage)
        planned_cost = sum(item['total_cost'] for item in usage if item['status'] == 'Planned')
        ordered_cost = sum(item['total_cost'] for item in usage if item['status'] == 'Ordered')
        delivered_cost = sum(item['total_cost'] for item in usage if item['status'] in ['Delivered', 'Used'])
        
        return {
            'total_cost': total_cost,
            'planned_cost': planned_cost,
            'ordered_cost': ordered_cost,
            'delivered_cost': delivered_cost,
            'material_count': len(usage),
            'materials': usage
        }
    
    def get_material_suppliers(self) -> List[Dict[str, Any]]:
        """Get all material suppliers"""
        suppliers = self.db.query(Material.supplier).filter(
            Material.supplier.isnot(None),
            Material.supplier != ''
        ).distinct().all()
        
        supplier_data = []
        for supplier in suppliers:
            materials = self.get_all(supplier=supplier[0])
            supplier_data.append({
                'supplier_name': supplier[0],
                'material_count': len(materials),
                'materials': [m.name for m in materials]
            })
        
        return supplier_data
    
    def get_materials_by_supplier(self, supplier_name: str) -> List[Material]:
        """Get materials by supplier"""
        return self.get_all(supplier=supplier_name)
    
    def create_material_order(self, material_id: int, quantity: int, project_id: int = None) -> Optional[ProjectMaterial]:
        """Create a material order for a project"""
        try:
            material = self.get_by_id(material_id)
            if not material:
                return None
            
            # Create project material entry
            project_material = ProjectMaterial(
                project_id=project_id,
                material_id=material_id,
                quantity=quantity,
                unit_cost=material.unit_cost,
                total_cost=quantity * (material.unit_cost or 0),
                status='Ordered'
            )
            
            self.db.add(project_material)
            self.db.commit()
            self.db.refresh(project_material)
            
            return project_material
            
        except Exception as e:
            self.db.rollback()
            raise
    
    def update_material_status(self, project_material_id: int, status: str) -> Optional[ProjectMaterial]:
        """Update material status in a project"""
        project_material = self.db.query(ProjectMaterial).filter(
            ProjectMaterial.project_material_id == project_material_id
        ).first()
        
        if not project_material:
            return None
        
        project_material.status = status
        
        # If delivered, update stock
        if status == 'Delivered':
            self.update_material_stock(
                project_material.material_id,
                int(project_material.quantity),
                'add'
            )
        
        self.db.commit()
        self.db.refresh(project_material)
        return project_material
    
    def get_material_availability(self, material_id: int) -> Dict[str, Any]:
        """Get material availability information"""
        material = self.get_by_id(material_id)
        if not material:
            return {}
        
        return {
            'material_id': material_id,
            'name': material.name,
            'current_stock': material.current_stock,
            'reorder_level': material.reorder_level,
            'minimum_order': material.minimum_order,
            'lead_time_days': material.lead_time_days,
            'status': material.status,
            'is_low_stock': material.current_stock <= material.reorder_level,
            'needs_reorder': material.current_stock <= material.reorder_level and material.status == 'Available',
            'total_value': float(material.unit_cost or 0) * material.current_stock
        }
    
    def search_materials(self, query: str, category: str = None) -> List[Material]:
        """Search materials by name or description"""
        search_query = self.db.query(Material).filter(
            Material.name.ilike(f"%{query}%") |
            Material.description.ilike(f"%{query}%")
        )
        
        if category:
            search_query = search_query.filter(Material.category == category)
        
        return search_query.all()
    
    def get_material_categories(self) -> List[str]:
        """Get all material categories"""
        categories = self.db.query(Material.category).filter(
            Material.category.isnot(None),
            Material.category != ''
        ).distinct().all()
        
        return [cat[0] for cat in categories]
