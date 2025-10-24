"""
Scheduling service with business logic for project scheduling and task management
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.project import Project
from models.project_phase import ProjectPhase
from models.project_task import ProjectTask
from models.task_assignment import TaskAssignment
from models.resource import Resource
from models.weather_data import WeatherData
from services.base import BaseService


class SchedulingService:
    """Service for scheduling-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_project_schedule(self, project_id: int, start_date: date) -> Dict[str, Any]:
        """Create a complete schedule for a project"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            return {}
        
        # Get project phases in order
        phases = self.db.query(ProjectPhase).filter(
            ProjectPhase.project_id == project_id
        ).order_by(ProjectPhase.phase_id).all()
        
        current_date = start_date
        schedule = {
            'project_id': project_id,
            'project_name': project.project_name,
            'start_date': start_date,
            'phases': []
        }
        
        for phase in phases:
            phase_start = current_date
            phase_duration = phase.phase.total_duration_days if phase.phase else 7
            phase_end = phase_start + timedelta(days=phase_duration)
            
            # Update phase dates
            phase.start_date = phase_start
            phase.end_date = phase_end
            phase.status = 'Not Started'
            
            # Get tasks for this phase
            tasks = self.db.query(ProjectTask).filter(
                ProjectTask.project_phase_id == phase.project_phase_id
            ).order_by(ProjectTask.task_id).all()
            
            phase_tasks = []
            task_current_date = phase_start
            
            for task in tasks:
                task_duration = task.task.duration_days if task.task else 1
                task_start = task_current_date
                task_end = task_start + timedelta(days=task_duration)
                
                # Update task dates
                task.start_date = task_start
                task.end_date = task_end
                task.status = 'Not Started'
                
                phase_tasks.append({
                    'task_id': task.task_id,
                    'name': task.task.name if task.task else 'Unknown Task',
                    'start_date': task_start,
                    'end_date': task_end,
                    'duration_days': task_duration
                })
                
                task_current_date = task_end
            
            schedule['phases'].append({
                'phase_id': phase.phase_id,
                'name': phase.phase.name if phase.phase else 'Unknown Phase',
                'start_date': phase_start,
                'end_date': phase_end,
                'duration_days': phase_duration,
                'tasks': phase_tasks
            })
            
            current_date = phase_end
        
        # Update project end date
        project.end_date = current_date
        
        self.db.commit()
        return schedule
    
    def get_resource_schedule(self, resource_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get resource schedule for a date range"""
        assignments = self.db.query(TaskAssignment).filter(
            TaskAssignment.resource_id == resource_id,
            TaskAssignment.start_date >= start_date,
            TaskAssignment.end_date <= end_date
        ).all()
        
        schedule = {
            'resource_id': resource_id,
            'resource_name': assignments[0].resource.name if assignments else 'Unknown',
            'start_date': start_date,
            'end_date': end_date,
            'assignments': []
        }
        
        for assignment in assignments:
            schedule['assignments'].append({
                'assignment_id': assignment.assignment_id,
                'project_task_id': assignment.project_task_id,
                'start_date': assignment.start_date,
                'end_date': assignment.end_date,
                'status': assignment.status,
                'hours_worked': float(assignment.hours_worked or 0)
            })
        
        return schedule
    
    def check_weather_impact(self, location: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Check weather impact on scheduling"""
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.location == location,
            WeatherData.date >= start_date,
            WeatherData.date <= end_date
        ).all()
        
        impact = {
            'location': location,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': (end_date - start_date).days + 1,
            'suitable_days': 0,
            'unsuitable_days': 0,
            'weather_details': []
        }
        
        for weather in weather_data:
            suitable = weather.is_suitable_for_outdoor_work
            if suitable:
                impact['suitable_days'] += 1
            else:
                impact['unsuitable_days'] += 1
            
            impact['weather_details'].append({
                'date': weather.date,
                'precipitation_probability': weather.precipitation_probability,
                'temperature_range': weather.temperature_range,
                'suitable_for_work': suitable,
                'recommendation': weather.work_recommendation
            })
        
        impact['suitability_percentage'] = (impact['suitable_days'] / impact['total_days'] * 100) if impact['total_days'] > 0 else 0
        
        return impact
    
    def optimize_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        """Optimize resource allocation for a project"""
        # Get all project tasks
        project_phases = self.db.query(ProjectPhase).filter(
            ProjectPhase.project_id == project_id
        ).all()
        
        all_tasks = []
        for phase in project_phases:
            tasks = self.db.query(ProjectTask).filter(
                ProjectTask.project_phase_id == phase.project_phase_id
            ).all()
            all_tasks.extend(tasks)
        
        # Get available resources
        available_resources = self.db.query(Resource).filter(
            Resource.availability == 'Elérhető'
        ).all()
        
        optimization = {
            'project_id': project_id,
            'total_tasks': len(all_tasks),
            'available_resources': len(available_resources),
            'recommendations': []
        }
        
        for task in all_tasks:
            if not task.task:
                continue
                
            # Find suitable resources
            suitable_resources = []
            for resource in available_resources:
                if (resource.profession_type_id == task.task.profession_type_id or 
                    task.task.profession_type_id is None):
                    suitable_resources.append(resource)
            
            optimization['recommendations'].append({
                'task_id': task.task_id,
                'task_name': task.task.name,
                'required_people': task.task.required_people,
                'suitable_resources': [
                    {
                        'resource_id': r.resource_id,
                        'name': r.name,
                        'hourly_rate': float(r.hourly_rate or 0),
                        'experience_years': r.experience_years
                    }
                    for r in suitable_resources
                ]
            })
        
        return optimization
    
    def get_project_timeline(self, project_id: int) -> Dict[str, Any]:
        """Get detailed project timeline"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            return {}
        
        phases = self.db.query(ProjectPhase).filter(
            ProjectPhase.project_id == project_id
        ).order_by(ProjectPhase.phase_id).all()
        
        timeline = {
            'project': {
                'id': project.project_id,
                'name': project.project_name,
                'start_date': project.start_date,
                'end_date': project.end_date,
                'status': project.status,
                'progress': project.progress_percent
            },
            'phases': []
        }
        
        for phase in phases:
            phase_tasks = self.db.query(ProjectTask).filter(
                ProjectTask.project_phase_id == phase.project_phase_id
            ).all()
            
            phase_data = {
                'phase_id': phase.phase_id,
                'name': phase.phase.name if phase.phase else 'Unknown Phase',
                'start_date': phase.start_date,
                'end_date': phase.end_date,
                'status': phase.status,
                'progress': phase.progress_percent,
                'tasks': []
            }
            
            for task in phase_tasks:
                task_assignments = self.db.query(TaskAssignment).filter(
                    TaskAssignment.project_task_id == task.project_task_id
                ).all()
                
                task_data = {
                    'task_id': task.task_id,
                    'name': task.task.name if task.task else 'Unknown Task',
                    'start_date': task.start_date,
                    'end_date': task.end_date,
                    'status': task.status,
                    'progress': task.progress_percent,
                    'is_completed': task.is_completed,
                    'assignments': [
                        {
                            'assignment_id': a.assignment_id,
                            'resource_name': a.resource.name if a.resource else 'Unknown',
                            'status': a.status,
                            'hours_worked': float(a.hours_worked or 0)
                        }
                        for a in task_assignments
                    ]
                }
                phase_data['tasks'].append(task_data)
            
            timeline['phases'].append(phase_data)
        
        return timeline
    
    def calculate_project_duration(self, project_id: int) -> Dict[str, Any]:
        """Calculate project duration and critical path"""
        timeline = self.get_project_timeline(project_id)
        if not timeline:
            return {}
        
        total_duration = 0
        critical_path = []
        
        for phase in timeline['phases']:
            phase_duration = 0
            if phase['start_date'] and phase['end_date']:
                phase_duration = (phase['end_date'] - phase['start_date']).days
            
            total_duration += phase_duration
            
            # Find critical tasks (longest duration)
            max_task_duration = 0
            critical_task = None
            
            for task in phase['tasks']:
                if task['start_date'] and task['end_date']:
                    task_duration = (task['end_date'] - task['start_date']).days
                    if task_duration > max_task_duration:
                        max_task_duration = task_duration
                        critical_task = task
            
            if critical_task:
                critical_path.append({
                    'phase': phase['name'],
                    'task': critical_task['name'],
                    'duration': max_task_duration
                })
        
        return {
            'project_id': project_id,
            'total_duration_days': total_duration,
            'critical_path': critical_path,
            'phases_count': len(timeline['phases']),
            'tasks_count': sum(len(phase['tasks']) for phase in timeline['phases'])
        }
