"""
Notification service for sending alerts and notifications
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.project import Project
from models.resource import Resource
from models.material import Material
from models.task_assignment import TaskAssignment
from models.user import User


class NotificationType(Enum):
    """Types of notifications"""
    PROJECT_OVERDUE = "project_overdue"
    TASK_OVERDUE = "task_overdue"
    LOW_STOCK = "low_stock"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    PROJECT_COMPLETED = "project_completed"


class NotificationService:
    """Service for managing notifications and alerts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_project_overdue(self) -> List[Dict[str, Any]]:
        """Check for overdue projects and generate notifications"""
        overdue_projects = self.db.query(Project).filter(
            Project.end_date < date.today(),
            Project.status != 'Lezárt'
        ).all()
        
        notifications = []
        for project in overdue_projects:
            notifications.append({
                'type': NotificationType.PROJECT_OVERDUE.value,
                'title': f'Project Overdue: {project.project_name}',
                'message': f'Project "{project.project_name}" was due on {project.end_date} but is still {project.status}',
                'project_id': project.project_id,
                'project_name': project.project_name,
                'due_date': project.end_date,
                'days_overdue': (date.today() - project.end_date).days,
                'priority': 'high'
            })
        
        return notifications
    
    def check_low_stock_materials(self) -> List[Dict[str, Any]]:
        """Check for low stock materials and generate notifications"""
        low_stock_materials = self.db.query(Material).filter(
            Material.current_stock <= Material.reorder_level,
            Material.status == 'Available'
        ).all()
        
        notifications = []
        for material in low_stock_materials:
            notifications.append({
                'type': NotificationType.LOW_STOCK.value,
                'title': f'Low Stock Alert: {material.name}',
                'message': f'Material "{material.name}" is low in stock ({material.current_stock} units). Reorder level: {material.reorder_level}',
                'material_id': material.material_id,
                'material_name': material.name,
                'current_stock': material.current_stock,
                'reorder_level': material.reorder_level,
                'priority': 'medium'
            })
        
        return notifications
    
    def check_resource_availability(self) -> List[Dict[str, Any]]:
        """Check for unavailable resources and generate notifications"""
        unavailable_resources = self.db.query(Resource).filter(
            Resource.availability != 'Elérhető'
        ).all()
        
        notifications = []
        for resource in unavailable_resources:
            notifications.append({
                'type': NotificationType.RESOURCE_UNAVAILABLE.value,
                'title': f'Resource Unavailable: {resource.name}',
                'message': f'Resource "{resource.name}" is currently {resource.availability}',
                'resource_id': resource.resource_id,
                'resource_name': resource.name,
                'availability': resource.availability,
                'priority': 'low'
            })
        
        return notifications
    
    def check_task_deadlines(self) -> List[Dict[str, Any]]:
        """Check for tasks approaching deadlines"""
        # Get tasks due in the next 3 days
        upcoming_date = date.today() + timedelta(days=3)
        
        upcoming_tasks = self.db.query(ProjectTask).filter(
            ProjectTask.end_date <= upcoming_date,
            ProjectTask.end_date >= date.today(),
            ProjectTask.status != 'Completed'
        ).all()
        
        notifications = []
        for task in upcoming_tasks:
            days_until_due = (task.end_date - date.today()).days
            priority = 'high' if days_until_due <= 1 else 'medium'
            
            notifications.append({
                'type': NotificationType.TASK_OVERDUE.value,
                'title': f'Task Due Soon: {task.task.name if task.task else "Unknown Task"}',
                'message': f'Task "{task.task.name if task.task else "Unknown Task"}" is due in {days_until_due} days',
                'task_id': task.task_id,
                'project_task_id': task.project_task_id,
                'task_name': task.task.name if task.task else 'Unknown Task',
                'due_date': task.end_date,
                'days_until_due': days_until_due,
                'priority': priority
            })
        
        return notifications
    
    def get_all_notifications(self) -> Dict[str, Any]:
        """Get all active notifications"""
        notifications = {
            'project_overdue': self.check_project_overdue(),
            'low_stock': self.check_low_stock_materials(),
            'resource_unavailable': self.check_resource_availability(),
            'task_deadlines': self.check_task_deadlines()
        }
        
        # Count total notifications
        total_count = sum(len(notif_list) for notif_list in notifications.values())
        
        return {
            'notifications': notifications,
            'total_count': total_count,
            'high_priority_count': len([
                n for notif_list in notifications.values() 
                for n in notif_list if n.get('priority') == 'high'
            ]),
            'medium_priority_count': len([
                n for notif_list in notifications.values() 
                for n in notif_list if n.get('priority') == 'medium'
            ]),
            'low_priority_count': len([
                n for notif_list in notifications.values() 
                for n in notif_list if n.get('priority') == 'low'
            ])
        }
    
    def create_task_assignment_notification(self, assignment: TaskAssignment) -> Dict[str, Any]:
        """Create notification for new task assignment"""
        return {
            'type': NotificationType.TASK_ASSIGNED.value,
            'title': f'New Task Assignment',
            'message': f'You have been assigned to task "{assignment.project_task.task.name if assignment.project_task and assignment.project_task.task else "Unknown Task"}"',
            'assignment_id': assignment.assignment_id,
            'resource_id': assignment.resource_id,
            'resource_name': assignment.resource.name if assignment.resource else 'Unknown',
            'task_name': assignment.project_task.task.name if assignment.project_task and assignment.project_task.task else 'Unknown Task',
            'project_name': assignment.project_task.project_phase.project.project_name if assignment.project_task and assignment.project_task.project_phase and assignment.project_task.project_phase.project else 'Unknown Project',
            'priority': 'medium'
        }
    
    def create_task_completion_notification(self, assignment: TaskAssignment) -> Dict[str, Any]:
        """Create notification for task completion"""
        return {
            'type': NotificationType.TASK_COMPLETED.value,
            'title': f'Task Completed',
            'message': f'Task "{assignment.project_task.task.name if assignment.project_task and assignment.project_task.task else "Unknown Task"}" has been completed',
            'assignment_id': assignment.assignment_id,
            'resource_id': assignment.resource_id,
            'resource_name': assignment.resource.name if assignment.resource else 'Unknown',
            'task_name': assignment.project_task.task.name if assignment.project_task and assignment.project_task.task else 'Unknown Task',
            'project_name': assignment.project_task.project_phase.project.project_name if assignment.project_task and assignment.project_task.project_phase and assignment.project_task.project_phase.project else 'Unknown Project',
            'completion_date': assignment.end_date,
            'hours_worked': float(assignment.hours_worked or 0),
            'priority': 'low'
        }
    
    def create_project_completion_notification(self, project: Project) -> Dict[str, Any]:
        """Create notification for project completion"""
        return {
            'type': NotificationType.PROJECT_COMPLETED.value,
            'title': f'Project Completed',
            'message': f'Project "{project.project_name}" has been completed',
            'project_id': project.project_id,
            'project_name': project.project_name,
            'completion_date': project.end_date,
            'project_manager': project.project_manager.full_name if project.project_manager else 'Unknown',
            'priority': 'medium'
        }
    
    def get_user_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get notifications for a specific user"""
        # Get user's projects
        user_projects = self.db.query(Project).filter(
            Project.project_manager_id == user_id
        ).all()
        
        notifications = []
        
        # Check for overdue projects managed by user
        for project in user_projects:
            if project.end_date < date.today() and project.status != 'Lezárt':
                notifications.append({
                    'type': NotificationType.PROJECT_OVERDUE.value,
                    'title': f'Your Project is Overdue',
                    'message': f'Project "{project.project_name}" is overdue',
                    'project_id': project.project_id,
                    'priority': 'high'
                })
        
        return notifications
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read (placeholder for future implementation)"""
        # This would typically update a notifications table
        # For now, just return True
        return True
    
    def send_email_notification(self, notification: Dict[str, Any], recipient_email: str) -> bool:
        """Send email notification (placeholder for future implementation)"""
        # This would integrate with an email service like SendGrid, AWS SES, etc.
        # For now, just return True
        return True
    
    def send_sms_notification(self, notification: Dict[str, Any], phone_number: str) -> bool:
        """Send SMS notification (placeholder for future implementation)"""
        # This would integrate with an SMS service like Twilio, AWS SNS, etc.
        # For now, just return True
        return True
