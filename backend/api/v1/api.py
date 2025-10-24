"""
Main API router for v1
"""

from fastapi import APIRouter
from api.v1.endpoints import users, projects, resources, materials, tasks, phases, profession_types, project_types, weather

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])
api_router.include_router(profession_types.router, prefix="/profession-types", tags=["profession-types"])
api_router.include_router(project_types.router, prefix="/project-types", tags=["project-types"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
