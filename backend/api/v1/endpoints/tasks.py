"""
Task API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.database import get_db
from models.task import Task
from models.project_task import ProjectTask
from models.task_assignment import TaskAssignment
from models.user import User
from schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskList,
    ProjectTaskCreate, ProjectTaskUpdate, ProjectTaskResponse,
    TaskAssignmentCreate, TaskAssignmentUpdate, TaskAssignmentResponse
)
from core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=TaskList)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    phase_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks with pagination and optional filtering"""
    query = db.query(Task)
    
    if phase_id:
        query = query.filter(Task.phase_id == phase_id)
    
    tasks = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return TaskList(
        tasks=[TaskResponse.from_orm(task) for task in tasks],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return TaskResponse.from_orm(db_task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a task"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse.from_orm(task)


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a task"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


# Project Tasks endpoints
@router.get("/projects/{project_phase_id}/tasks", response_model=List[ProjectTaskResponse])
async def get_project_tasks(project_phase_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all tasks for a project phase"""
    tasks = db.query(ProjectTask).filter(ProjectTask.project_phase_id == project_phase_id).all()
    return [ProjectTaskResponse.from_orm(task) for task in tasks]


@router.post("/projects/{project_phase_id}/tasks", response_model=ProjectTaskResponse)
async def create_project_task(
    project_phase_id: int, 
    task: ProjectTaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new project task"""
    db_task = ProjectTask(project_phase_id=project_phase_id, **task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return ProjectTaskResponse.from_orm(db_task)


@router.put("/projects/tasks/{project_task_id}", response_model=ProjectTaskResponse)
async def update_project_task(
    project_task_id: int, 
    task_update: ProjectTaskUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a project task"""
    task = db.query(ProjectTask).filter(ProjectTask.project_task_id == project_task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Project task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return ProjectTaskResponse.from_orm(task)


# Task Assignments endpoints
@router.get("/assignments/{project_task_id}", response_model=List[TaskAssignmentResponse])
async def get_task_assignments(project_task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all assignments for a project task"""
    assignments = db.query(TaskAssignment).filter(TaskAssignment.project_task_id == project_task_id).all()
    return [TaskAssignmentResponse.from_orm(assignment) for assignment in assignments]


@router.post("/assignments", response_model=TaskAssignmentResponse)
async def create_task_assignment(
    assignment: TaskAssignmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task assignment"""
    db_assignment = TaskAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    return TaskAssignmentResponse.from_orm(db_assignment)


@router.put("/assignments/{assignment_id}", response_model=TaskAssignmentResponse)
async def update_task_assignment(
    assignment_id: int, 
    assignment_update: TaskAssignmentUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task assignment"""
    assignment = db.query(TaskAssignment).filter(TaskAssignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    
    update_data = assignment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    
    return TaskAssignmentResponse.from_orm(assignment)
