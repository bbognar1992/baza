"""
Material API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.material import Material, ProjectMaterial
from models.user import User
from schemas.material import (
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialList,
    ProjectMaterialCreate, ProjectMaterialUpdate, ProjectMaterialResponse
)
from core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=MaterialList)
async def get_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all materials with pagination and optional filtering"""
    query = db.query(Material)
    
    if category:
        query = query.filter(Material.category == category)
    if status:
        query = query.filter(Material.status == status)
    
    materials = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return MaterialList(
        materials=[MaterialResponse.from_orm(material) for material in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a specific material by ID"""
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialResponse.from_orm(material)


@router.post("/", response_model=MaterialResponse)
async def create_material(material: MaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new material"""
    db_material = Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    return MaterialResponse.from_orm(db_material)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(material_id: int, material_update: MaterialUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a material"""
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    update_data = material_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    
    return MaterialResponse.from_orm(material)


@router.delete("/{material_id}")
async def delete_material(material_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a material"""
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    db.delete(material)
    db.commit()
    
    return {"message": "Material deleted successfully"}


# Project Materials endpoints
@router.get("/projects/{project_id}/materials", response_model=List[ProjectMaterialResponse])
async def get_project_materials(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all materials for a project"""
    materials = db.query(ProjectMaterial).filter(ProjectMaterial.project_id == project_id).all()
    return [ProjectMaterialResponse.from_orm(material) for material in materials]


@router.post("/projects/{project_id}/materials", response_model=ProjectMaterialResponse)
async def create_project_material(
    project_id: int, 
    material: ProjectMaterialCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a material to a project"""
    db_material = ProjectMaterial(project_id=project_id, **material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    return ProjectMaterialResponse.from_orm(db_material)


@router.put("/projects/materials/{project_material_id}", response_model=ProjectMaterialResponse)
async def update_project_material(
    project_material_id: int, 
    material_update: ProjectMaterialUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a project material"""
    material = db.query(ProjectMaterial).filter(ProjectMaterial.project_material_id == project_material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Project material not found")
    
    update_data = material_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)
    
    db.commit()
    db.refresh(material)
    
    return ProjectMaterialResponse.from_orm(material)
