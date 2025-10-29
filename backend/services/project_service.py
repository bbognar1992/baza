"""
Project service with business logic for project management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.project import Project, ProjectLocation, ProjectMember
from models.resource import Resource
from models.user import User
from services.base import BaseService


class ProjectService(BaseService):
    """Service for project-related business logic"""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)
    
    def create_project_with_details(
        self, 
        project_data: Dict[str, Any],
        locations: List[Dict[str, Any]] = None,
        members: List[Dict[str, Any]] = None
    ) -> Project:
        """Create a project with locations and members"""
        try:
            # Create the main project
            project = self.create(**project_data)
            
            # Add locations if provided
            if locations:
                for location_data in locations:
                    location_data['project_id'] = project.project_id
                    ProjectLocation(**location_data)
                    self.db.add(ProjectLocation(**location_data))
            
            # Add members if provided
            if members:
                for member_data in members:
                    member_data['project_id'] = project.project_id
                    self.db.add(ProjectMember(**member_data))
            
            self.db.commit()
            self.db.refresh(project)
            return project
            
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_project_with_details(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project with all related data"""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        return {
            'project': project,
            'locations': project.locations,
            'members': project.members,
            'phases': project.project_phases,
            'materials': project.materials
        }
    
    def update_project_progress(self, project_id: int, progress_percent: int) -> Optional[Project]:
        """Update project progress and status"""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        # Update progress
        project.progress_percent = max(0, min(100, progress_percent))
        
        # Update status based on progress
        if progress_percent == 100:
            project.status = 'Lezárt'
        elif progress_percent > 0:
            project.status = 'Folyamatban'
        
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_projects_by_manager(self, manager_id: int) -> List[Project]:
        """Get all projects managed by a specific user"""
        return self.get_all(project_manager_id=manager_id)
    
    def get_active_projects(self) -> List[Project]:
        """Get all active projects"""
        return self.get_all(status='Folyamatban')
    
    def get_overdue_projects(self) -> List[Project]:
        """Get projects that are overdue"""
        today = date.today()
        return self.db.query(Project).filter(
            Project.end_date < today,
            Project.status != 'Lezárt'
        ).all()
    
    def calculate_project_costs(self, project_id: int) -> Dict[str, Decimal]:
        """Calculate total costs for a project"""
        project = self.get_by_id(project_id)
        if not project:
            return {}
        
        # Calculate material costs
        material_costs = sum(
            float(pm.total_cost or 0) for pm in project.materials
        ) if project.materials else 0
        
        # Calculate labor costs (from task assignments)
        labor_costs = 0
        for phase in project.project_phases:
            for task in phase.project_tasks:
                for assignment in task.task_assignments:
                    if assignment.resource and assignment.resource.hourly_rate:
                        labor_costs += float(assignment.resource.hourly_rate * assignment.hours_worked)
        
        total_costs = material_costs + labor_costs
        
        return {
            'material_costs': Decimal(str(material_costs)),
            'labor_costs': Decimal(str(labor_costs)),
            'total_costs': Decimal(str(total_costs)),
            'budget': project.budget or 0,
            'budget_variance': (project.budget or 0) - Decimal(str(total_costs))
        }
    
    def get_project_timeline(self, project_id: int) -> Dict[str, Any]:
        """Get project timeline with phases and tasks"""
        project = self.get_by_id(project_id)
        if not project:
            return {}
        
        timeline = {
            'project': {
                'id': project.project_id,
                'name': project.project_name,
                'start_date': project.start_date,
                'end_date': project.end_date,
                'status': project.status
            },
            'phases': []
        }
        
        for phase in project.project_phases:
            phase_data = {
                'phase_id': phase.phase_id,
                'name': phase.phase.name if phase.phase else 'Unknown Phase',
                'start_date': phase.start_date,
                'end_date': phase.end_date,
                'status': phase.status,
                'progress': phase.progress_percent,
                'tasks': []
            }
            
            for task in phase.project_tasks:
                task_data = {
                    'task_id': task.task_id,
                    'name': task.task.name if task.task else 'Unknown Task',
                    'start_date': task.start_date,
                    'end_date': task.end_date,
                    'status': task.status,
                    'progress': task.progress_percent,
                    'is_completed': task.is_completed
                }
                phase_data['tasks'].append(task_data)
            
            timeline['phases'].append(phase_data)
        
        return timeline
