"""
Profession Type API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.profession_type import ProfessionType
from models.user import User
from schemas.profession_type import ProfessionTypeCreate, ProfessionTypeUpdate, ProfessionTypeResponse, ProfessionTypeList
from core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=ProfessionTypeList)
async def get_profession_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all profession types with pagination and optional filtering"""
    query = db.query(ProfessionType)
    
    if level:
        query = query.filter(ProfessionType.level == level)
    
    profession_types = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProfessionTypeList(
        profession_types=[ProfessionTypeResponse.from_orm(pt) for pt in profession_types],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{profession_type_id}", response_model=ProfessionTypeResponse)
async def get_profession_type(profession_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a specific profession type by ID"""
    profession_type = db.query(ProfessionType).filter(ProfessionType.profession_type_id == profession_type_id).first()
    if not profession_type:
        raise HTTPException(status_code=404, detail="Profession type not found")
    return ProfessionTypeResponse.from_orm(profession_type)


@router.post("/", response_model=ProfessionTypeResponse)
async def create_profession_type(profession_type: ProfessionTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new profession type"""
    # Check if name already exists
    existing = db.query(ProfessionType).filter(ProfessionType.name == profession_type.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profession type name already exists")
    
    db_profession_type = ProfessionType(**profession_type.dict())
    db.add(db_profession_type)
    db.commit()
    db.refresh(db_profession_type)
    
    return ProfessionTypeResponse.from_orm(db_profession_type)


@router.put("/{profession_type_id}", response_model=ProfessionTypeResponse)
async def update_profession_type(profession_type_id: int, profession_type_update: ProfessionTypeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a profession type"""
    profession_type = db.query(ProfessionType).filter(ProfessionType.profession_type_id == profession_type_id).first()
    if not profession_type:
        raise HTTPException(status_code=404, detail="Profession type not found")
    
    update_data = profession_type_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profession_type, field, value)
    
    db.commit()
    db.refresh(profession_type)
    
    return ProfessionTypeResponse.from_orm(profession_type)


@router.delete("/{profession_type_id}")
async def delete_profession_type(profession_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a profession type"""
    profession_type = db.query(ProfessionType).filter(ProfessionType.profession_type_id == profession_type_id).first()
    if not profession_type:
        raise HTTPException(status_code=404, detail="Profession type not found")
    
    db.delete(profession_type)
    db.commit()
    
    return {"message": "Profession type deleted successfully"}
