"""
Phase API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.phase import Phase
from models.project_phase import ProjectPhase
from schemas.phase import (
    PhaseCreate, PhaseUpdate, PhaseResponse, PhaseList,
    ProjectPhaseCreate, ProjectPhaseUpdate, ProjectPhaseResponse
)

router = APIRouter()


@router.get("/", response_model=PhaseList)
async def get_phases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    project_type_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all phases with pagination and optional filtering"""
    query = db.query(Phase)
    
    if project_type_id:
        query = query.filter(Phase.project_type_id == project_type_id)
    
    phases = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return PhaseList(
        phases=[PhaseResponse.from_orm(phase) for phase in phases],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{phase_id}", response_model=PhaseResponse)
async def get_phase(phase_id: int, db: Session = Depends(get_db)):
    """Get a specific phase by ID"""
    phase = db.query(Phase).filter(Phase.phase_id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    return PhaseResponse.from_orm(phase)


@router.post("/", response_model=PhaseResponse)
async def create_phase(phase: PhaseCreate, db: Session = Depends(get_db)):
    """Create a new phase"""
    db_phase = Phase(**phase.dict())
    db.add(db_phase)
    db.commit()
    db.refresh(db_phase)
    
    return PhaseResponse.from_orm(db_phase)


@router.put("/{phase_id}", response_model=PhaseResponse)
async def update_phase(phase_id: int, phase_update: PhaseUpdate, db: Session = Depends(get_db)):
    """Update a phase"""
    phase = db.query(Phase).filter(Phase.phase_id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    update_data = phase_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phase, field, value)
    
    db.commit()
    db.refresh(phase)
    
    return PhaseResponse.from_orm(phase)


@router.delete("/{phase_id}")
async def delete_phase(phase_id: int, db: Session = Depends(get_db)):
    """Delete a phase"""
    phase = db.query(Phase).filter(Phase.phase_id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    db.delete(phase)
    db.commit()
    
    return {"message": "Phase deleted successfully"}


# Project Phases endpoints
@router.get("/projects/{project_id}/phases", response_model=List[ProjectPhaseResponse])
async def get_project_phases(project_id: int, db: Session = Depends(get_db)):
    """Get all phases for a project"""
    phases = db.query(ProjectPhase).filter(ProjectPhase.project_id == project_id).all()
    return [ProjectPhaseResponse.from_orm(phase) for phase in phases]


@router.post("/projects/{project_id}/phases", response_model=ProjectPhaseResponse)
async def create_project_phase(
    project_id: int, 
    phase: ProjectPhaseCreate, 
    db: Session = Depends(get_db)
):
    """Create a new project phase"""
    db_phase = ProjectPhase(project_id=project_id, **phase.dict())
    db.add(db_phase)
    db.commit()
    db.refresh(db_phase)
    
    return ProjectPhaseResponse.from_orm(db_phase)


@router.put("/projects/phases/{project_phase_id}", response_model=ProjectPhaseResponse)
async def update_project_phase(
    project_phase_id: int, 
    phase_update: ProjectPhaseUpdate, 
    db: Session = Depends(get_db)
):
    """Update a project phase"""
    phase = db.query(ProjectPhase).filter(ProjectPhase.project_phase_id == project_phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Project phase not found")
    
    update_data = phase_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phase, field, value)
    
    db.commit()
    db.refresh(phase)
    
    return ProjectPhaseResponse.from_orm(phase)
