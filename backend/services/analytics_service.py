"""
Analytics service with business logic for reporting and analytics
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.project import Project
from models.resource import Resource
from models.material import Material, ProjectMaterial
from models.task_assignment import TaskAssignment
from models.user import User


class AnalyticsService:
    """Service for analytics and reporting business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_project_analytics(self, project_id: int = None) -> Dict[str, Any]:
        """Get comprehensive project analytics"""
        query = self.db.query(Project)
        if project_id:
            query = query.filter(Project.project_id == project_id)
        
        projects = query.all()
        
        analytics = {
            'total_projects': len(projects),
            'active_projects': len([p for p in projects if p.status == 'Folyamatban']),
            'completed_projects': len([p for p in projects if p.status == 'Lezárt']),
            'overdue_projects': len([p for p in projects if p.end_date < date.today() and p.status != 'Lezárt']),
            'total_budget': sum(float(p.budget or 0) for p in projects),
            'average_project_duration': 0,
            'project_status_distribution': {}
        }
        
        # Calculate average duration
        durations = []
        for project in projects:
            if project.start_date and project.end_date:
                duration = (project.end_date - project.start_date).days
                durations.append(duration)
        
        if durations:
            analytics['average_project_duration'] = sum(durations) / len(durations)
        
        # Status distribution
        status_counts = {}
        for project in projects:
            status_counts[project.status] = status_counts.get(project.status, 0) + 1
        analytics['project_status_distribution'] = status_counts
        
        return analytics
    
    def get_resource_analytics(self) -> Dict[str, Any]:
        """Get resource utilization analytics"""
        resources = self.db.query(Resource).all()
        
        analytics = {
            'total_resources': len(resources),
            'available_resources': len([r for r in resources if r.availability == 'Elérhető']),
            'busy_resources': len([r for r in resources if r.availability == 'Foglalt']),
            'on_leave_resources': len([r for r in resources if r.availability in ['Szabadságon', 'Betegszabadság']]),
            'resource_types': {},
            'average_hourly_rate': 0,
            'total_earnings_potential': 0
        }
        
        # Resource type distribution
        type_counts = {}
        hourly_rates = []
        for resource in resources:
            type_counts[resource.type] = type_counts.get(resource.type, 0) + 1
            if resource.hourly_rate:
                hourly_rates.append(float(resource.hourly_rate))
        
        analytics['resource_types'] = type_counts
        
        if hourly_rates:
            analytics['average_hourly_rate'] = sum(hourly_rates) / len(hourly_rates)
            analytics['total_earnings_potential'] = sum(hourly_rates) * 8 * 30  # 8 hours/day, 30 days/month
        
        return analytics
    
    def get_material_analytics(self) -> Dict[str, Any]:
        """Get material usage and cost analytics"""
        materials = self.db.query(Material).all()
        project_materials = self.db.query(ProjectMaterial).all()
        
        analytics = {
            'total_materials': len(materials),
            'available_materials': len([m for m in materials if m.status == 'Available']),
            'out_of_stock': len([m for m in materials if m.status == 'Out of Stock']),
            'low_stock_materials': len([m for m in materials if m.current_stock <= m.reorder_level]),
            'total_material_value': sum(float(m.unit_cost or 0) * m.current_stock for m in materials),
            'categories': {},
            'suppliers': {},
            'project_material_costs': sum(float(pm.total_cost or 0) for pm in project_materials)
        }
        
        # Category distribution
        categories = {}
        suppliers = {}
        for material in materials:
            if material.category:
                categories[material.category] = categories.get(material.category, 0) + 1
            if material.supplier:
                suppliers[material.supplier] = suppliers.get(material.supplier, 0) + 1
        
        analytics['categories'] = categories
        analytics['suppliers'] = suppliers
        
        return analytics
    
    def get_financial_analytics(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get financial analytics for projects and resources"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Project budgets
        projects = self.db.query(Project).filter(
            Project.start_date >= start_date,
            Project.start_date <= end_date
        ).all()
        
        # Resource earnings
        assignments = self.db.query(TaskAssignment).filter(
            TaskAssignment.start_date >= start_date,
            TaskAssignment.end_date <= end_date
        ).all()
        
        # Material costs
        project_materials = self.db.query(ProjectMaterial).filter(
            ProjectMaterial.assigned_date >= start_date,
            ProjectMaterial.assigned_date <= end_date
        ).all()
        
        analytics = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'project_budgets': {
                'total_budget': sum(float(p.budget or 0) for p in projects),
                'projects_count': len(projects)
            },
            'labor_costs': {
                'total_hours': sum(float(a.hours_worked or 0) for a in assignments),
                'total_cost': sum(
                    float(a.resource.hourly_rate or 0) * float(a.hours_worked or 0)
                    for a in assignments if a.resource and a.resource.hourly_rate
                ),
                'assignments_count': len(assignments)
            },
            'material_costs': {
                'total_cost': sum(float(pm.total_cost or 0) for pm in project_materials),
                'materials_count': len(project_materials)
            }
        }
        
        # Calculate total costs
        total_costs = (
            analytics['labor_costs']['total_cost'] + 
            analytics['material_costs']['total_cost']
        )
        
        analytics['total_costs'] = total_costs
        analytics['profit_margin'] = (
            analytics['project_budgets']['total_budget'] - total_costs
        )
        
        return analytics
    
    def get_productivity_metrics(self, resource_id: int = None, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Get productivity metrics for resources or overall"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        query = self.db.query(TaskAssignment).filter(
            TaskAssignment.start_date >= start_date,
            TaskAssignment.end_date <= end_date
        )
        
        if resource_id:
            query = query.filter(TaskAssignment.resource_id == resource_id)
        
        assignments = query.all()
        
        metrics = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_hours_worked': sum(float(a.hours_worked or 0) for a in assignments),
            'completed_tasks': len([a for a in assignments if a.status == 'Completed']),
            'active_tasks': len([a for a in assignments if a.status == 'In Progress']),
            'total_assignments': len(assignments),
            'average_hours_per_assignment': 0,
            'completion_rate': 0
        }
        
        if assignments:
            metrics['average_hours_per_assignment'] = metrics['total_hours_worked'] / len(assignments)
            metrics['completion_rate'] = (metrics['completed_tasks'] / len(assignments)) * 100
        
        return metrics
    
    def get_project_performance(self, project_id: int) -> Dict[str, Any]:
        """Get detailed performance metrics for a specific project"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            return {}
        
        # Get project phases
        phases = self.db.query(ProjectPhase).filter(
            ProjectPhase.project_id == project_id
        ).all()
        
        # Get all tasks
        all_tasks = []
        for phase in phases:
            tasks = self.db.query(ProjectTask).filter(
                ProjectTask.project_phase_id == phase.project_phase_id
            ).all()
            all_tasks.extend(tasks)
        
        # Calculate metrics
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.is_completed])
        in_progress_tasks = len([t for t in all_tasks if t.status == 'In Progress'])
        
        # Calculate time metrics
        days_elapsed = 0
        if project.start_date:
            days_elapsed = (date.today() - project.start_date).days
        
        total_duration = 0
        if project.start_date and project.end_date:
            total_duration = (project.end_date - project.start_date).days
        
        performance = {
            'project_id': project_id,
            'project_name': project.project_name,
            'status': project.status,
            'progress_percent': project.progress_percent,
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            'timeline': {
                'days_elapsed': days_elapsed,
                'total_duration': total_duration,
                'time_completion_rate': (days_elapsed / total_duration * 100) if total_duration > 0 else 0,
                'is_overdue': project.end_date < date.today() if project.end_date else False
            },
            'budget': {
                'budget': float(project.budget or 0),
                'spent': 0,  # Would need to calculate from materials and labor
                'budget_utilization': 0
            }
        }
        
        return performance
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for dashboard"""
        projects = self.db.query(Project).all()
        resources = self.db.query(Resource).all()
        materials = self.db.query(Material).all()
        
        # Recent activity (last 7 days)
        recent_date = date.today() - timedelta(days=7)
        recent_assignments = self.db.query(TaskAssignment).filter(
            TaskAssignment.assigned_date >= recent_date
        ).count()
        
        summary = {
            'overview': {
                'total_projects': len(projects),
                'active_projects': len([p for p in projects if p.status == 'Folyamatban']),
                'total_resources': len(resources),
                'available_resources': len([r for r in resources if r.availability == 'Elérhető']),
                'total_materials': len(materials),
                'low_stock_materials': len([m for m in materials if m.current_stock <= m.reorder_level])
            },
            'recent_activity': {
                'new_assignments': recent_assignments,
                'completed_tasks': 0,  # Would need to query completed tasks
                'new_projects': len([p for p in projects if p.created_at and p.created_at.date() >= recent_date])
            },
            'alerts': {
                'overdue_projects': len([p for p in projects if p.end_date < date.today() and p.status != 'Lezárt']),
                'low_stock_count': len([m for m in materials if m.current_stock <= m.reorder_level]),
                'unavailable_resources': len([r for r in resources if r.availability != 'Elérhető'])
            }
        }
        
        return summary
