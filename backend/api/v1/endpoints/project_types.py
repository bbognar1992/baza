"""
Project Type API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.project_type import ProjectType
from models.user import User
from schemas.project_type import ProjectTypeCreate, ProjectTypeUpdate, ProjectTypeResponse, ProjectTypeList
from core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=ProjectTypeList)
async def get_project_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all project types with pagination"""
    project_types = db.query(ProjectType).offset(skip).limit(limit).all()
    total = db.query(ProjectType).count()
    
    return ProjectTypeList(
        project_types=[ProjectTypeResponse.from_orm(pt) for pt in project_types],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{project_type_id}", response_model=ProjectTypeResponse)
async def get_project_type(project_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a specific project type by ID"""
    project_type = db.query(ProjectType).filter(ProjectType.project_type_id == project_type_id).first()
    if not project_type:
        raise HTTPException(status_code=404, detail="Project type not found")
    return ProjectTypeResponse.from_orm(project_type)


@router.post("/", response_model=ProjectTypeResponse)
async def create_project_type(project_type: ProjectTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new project type"""
    # Check if name already exists
    existing = db.query(ProjectType).filter(ProjectType.name == project_type.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project type name already exists")
    
    db_project_type = ProjectType(**project_type.dict())
    db.add(db_project_type)
    db.commit()
    db.refresh(db_project_type)
    
    return ProjectTypeResponse.from_orm(db_project_type)


@router.put("/{project_type_id}", response_model=ProjectTypeResponse)
async def update_project_type(project_type_id: int, project_type_update: ProjectTypeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a project type"""
    project_type = db.query(ProjectType).filter(ProjectType.project_type_id == project_type_id).first()
    if not project_type:
        raise HTTPException(status_code=404, detail="Project type not found")
    
    update_data = project_type_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project_type, field, value)
    
    db.commit()
    db.refresh(project_type)
    
    return ProjectTypeResponse.from_orm(project_type)


@router.delete("/{project_type_id}")
async def delete_project_type(project_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a project type"""
    project_type = db.query(ProjectType).filter(ProjectType.project_type_id == project_type_id).first()
    if not project_type:
        raise HTTPException(status_code=404, detail="Project type not found")
    
    db.delete(project_type)
    db.commit()
    
    return {"message": "Project type deleted successfully"}
