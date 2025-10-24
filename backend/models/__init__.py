# ÉpítAI Construction Management System - SQLAlchemy Models
# This module contains all database models for the construction management system

from .base import Base, db
from .user import User
from .profession_type import ProfessionType
from .resource import Resource
from .project_type import ProjectType
from .project import Project, ProjectLocation, ProjectMember
from .phase import Phase
from .task import Task
from .project_phase import ProjectPhase
from .project_task import ProjectTask
from .task_assignment import TaskAssignment
from .material import Material, ProjectMaterial
from .weather_data import WeatherData

# Export all models
__all__ = [
    'Base',
    'db',
    'User',
    'ProfessionType',
    'Resource',
    'ProjectType',
    'Project',
    'ProjectLocation',
    'ProjectMember',
    'Phase',
    'Task',
    'ProjectPhase',
    'ProjectTask',
    'TaskAssignment',
    'Material',
    'ProjectMaterial',
    'WeatherData'
]
