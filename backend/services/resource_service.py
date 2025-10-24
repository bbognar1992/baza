"""
Resource service with business logic for resource management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.resource import Resource
from models.task_assignment import TaskAssignment
from models.project_member import ProjectMember
from services.base import BaseService


class ResourceService(BaseService):
    """Service for resource-related business logic"""
    
    def __init__(self, db: Session):
        super().__init__(db, Resource)
    
    def get_available_resources(self, resource_type: str = None) -> List[Resource]:
        """Get all available resources, optionally filtered by type"""
        filters = {'availability': 'Elérhető'}
        if resource_type:
            filters['type'] = resource_type
        return self.get_all(**filters)
    
    def get_resources_by_skill(self, profession_type_id: int) -> List[Resource]:
        """Get resources by profession type"""
        return self.get_all(profession_type_id=profession_type_id)
    
    def get_resource_workload(self, resource_id: int, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Calculate resource workload for a given period"""
        resource = self.get_by_id(resource_id)
        if not resource:
            return {}
        
        # Get all task assignments for this resource
        query = self.db.query(TaskAssignment).filter(TaskAssignment.resource_id == resource_id)
        
        if start_date:
            query = query.filter(TaskAssignment.start_date >= start_date)
        if end_date:
            query = query.filter(TaskAssignment.end_date <= end_date)
        
        assignments = query.all()
        
        total_hours = sum(float(a.hours_worked or 0) for a in assignments)
        active_assignments = [a for a in assignments if a.is_active]
        
        return {
            'resource_id': resource_id,
            'resource_name': resource.name,
            'total_hours_worked': total_hours,
            'active_assignments_count': len(active_assignments),
            'assignments': [
                {
                    'assignment_id': a.assignment_id,
                    'project_task_id': a.project_task_id,
                    'start_date': a.start_date,
                    'end_date': a.end_date,
                    'status': a.status,
                    'hours_worked': float(a.hours_worked or 0)
                }
                for a in assignments
            ]
        }
    
    def get_resource_utilization(self, resource_id: int, days: int = 30) -> Dict[str, Any]:
        """Calculate resource utilization over the last N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        workload = self.get_resource_workload(resource_id, start_date, end_date)
        
        # Calculate utilization percentage (assuming 8 hours per day)
        max_possible_hours = days * 8
        utilization_percent = (workload['total_hours_worked'] / max_possible_hours * 100) if max_possible_hours > 0 else 0
        
        return {
            **workload,
            'utilization_percent': round(utilization_percent, 2),
            'max_possible_hours': max_possible_hours,
            'period_days': days
        }
    
    def assign_resource_to_project(self, resource_id: int, project_id: int, role: str = None) -> bool:
        """Assign a resource to a project"""
        try:
            # Check if already assigned
            existing = self.db.query(ProjectMember).filter(
                ProjectMember.resource_id == resource_id,
                ProjectMember.project_id == project_id
            ).first()
            
            if existing:
                return False
            
            # Create new assignment
            assignment = ProjectMember(
                project_id=project_id,
                resource_id=resource_id,
                role_in_project=role
            )
            
            self.db.add(assignment)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_resource_projects(self, resource_id: int) -> List[Dict[str, Any]]:
        """Get all projects a resource is assigned to"""
        assignments = self.db.query(ProjectMember).filter(
            ProjectMember.resource_id == resource_id
        ).all()
        
        projects = []
        for assignment in assignments:
            project = assignment.project
            projects.append({
                'project_id': project.project_id,
                'project_name': project.project_name,
                'role_in_project': assignment.role_in_project,
                'assigned_date': assignment.assigned_date,
                'project_status': project.status,
                'project_start_date': project.start_date,
                'project_end_date': project.end_date
            })
        
        return projects
    
    def get_resource_earnings(self, resource_id: int, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Calculate resource earnings for a period"""
        resource = self.get_by_id(resource_id)
        if not resource:
            return {}
        
        workload = self.get_resource_workload(resource_id, start_date, end_date)
        
        # Calculate earnings based on hourly rate
        hourly_rate = float(resource.hourly_rate or 0)
        total_earnings = workload['total_hours_worked'] * hourly_rate
        
        return {
            'resource_id': resource_id,
            'resource_name': resource.name,
            'hourly_rate': hourly_rate,
            'total_hours': workload['total_hours_worked'],
            'total_earnings': total_earnings,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    def update_resource_availability(self, resource_id: int, availability: str) -> Optional[Resource]:
        """Update resource availability status"""
        resource = self.get_by_id(resource_id)
        if not resource:
            return None
        
        resource.availability = availability
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def get_resources_by_availability(self, availability: str) -> List[Resource]:
        """Get resources by availability status"""
        return self.get_all(availability=availability)
    
    def search_resources(self, query: str, resource_type: str = None) -> List[Resource]:
        """Search resources by name, skills, or position"""
        search_query = self.db.query(Resource).filter(
            Resource.name.ilike(f"%{query}%") |
            Resource.skills.ilike(f"%{query}%") |
            Resource.position.ilike(f"%{query}%")
        )
        
        if resource_type:
            search_query = search_query.filter(Resource.type == resource_type)
        
        return search_query.all()
