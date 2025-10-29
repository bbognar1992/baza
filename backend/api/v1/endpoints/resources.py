"""
Resource API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.resource import Resource
from models.user import User
from schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceList
from core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=ResourceList)
async def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    availability: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all resources with pagination and optional filtering"""
    query = db.query(Resource)
    
    if type:
        query = query.filter(Resource.type == type)
    if availability:
        query = query.filter(Resource.availability == availability)
    
    resources = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ResourceList(
        resources=[ResourceResponse.from_orm(resource) for resource in resources],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a specific resource by ID"""
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse.from_orm(resource)


@router.post("/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new resource"""
    db_resource = Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    return ResourceResponse.from_orm(db_resource)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(resource_id: int, resource_update: ResourceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a resource"""
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    update_data = resource_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    
    return ResourceResponse.from_orm(resource)


@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a resource"""
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    
    return {"message": "Resource deleted successfully"}
