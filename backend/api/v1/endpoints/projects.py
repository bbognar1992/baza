"""
Project API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.project import Project, ProjectLocation, ProjectMember
from schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList,
    ProjectLocationCreate, ProjectLocationResponse,
    ProjectMemberCreate, ProjectMemberResponse
)

router = APIRouter()


@router.get("/", response_model=ProjectList)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all projects with pagination and optional filtering"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProjectList(
        projects=[ProjectResponse.from_orm(project) for project in projects],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.from_orm(project)


@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    # Check if project code already exists
    if project.project_code:
        existing_project = db.query(Project).filter(Project.project_code == project.project_code).first()
        if existing_project:
            raise HTTPException(status_code=400, detail="Project code already exists")
    
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return ProjectResponse.from_orm(db_project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.from_orm(project)


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


# Project Locations endpoints
@router.get("/{project_id}/locations", response_model=List[ProjectLocationResponse])
async def get_project_locations(project_id: int, db: Session = Depends(get_db)):
    """Get all locations for a project"""
    locations = db.query(ProjectLocation).filter(ProjectLocation.project_id == project_id).all()
    return [ProjectLocationResponse.from_orm(location) for location in locations]


@router.post("/{project_id}/locations", response_model=ProjectLocationResponse)
async def create_project_location(
    project_id: int, 
    location: ProjectLocationCreate, 
    db: Session = Depends(get_db)
):
    """Create a new project location"""
    db_location = ProjectLocation(project_id=project_id, **location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    return ProjectLocationResponse.from_orm(db_location)


# Project Members endpoints
@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(project_id: int, db: Session = Depends(get_db)):
    """Get all members for a project"""
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return [ProjectMemberResponse.from_orm(member) for member in members]


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def create_project_member(
    project_id: int, 
    member: ProjectMemberCreate, 
    db: Session = Depends(get_db)
):
    """Add a member to a project"""
    db_member = ProjectMember(project_id=project_id, **member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return ProjectMemberResponse.from_orm(db_member)
