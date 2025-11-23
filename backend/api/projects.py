"""
Projects API
Create and manage document generation projects
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from backend.database import get_db, User, Project, ProjectStatus, DocumentType
from backend.clerk_auth import get_current_user
from backend.tasks import generate_document_task
from backend.websocket_manager import manager

router = APIRouter()


# Pydantic models
class ProjectCreate(BaseModel):
    title: str
    query: str
    document_type: DocumentType
    description: Optional[str] = None
    output_format: Optional[str] = "html"  # html, markdown, pdf, pptx
    generate_images: bool = False


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    query: str
    document_type: str
    generate_images: bool
    status: str
    progress: int
    output_path: Optional[str]
    output_format: Optional[str]
    search_results_count: int
    processing_time: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


# API Endpoints
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document generation project"""
    
    # Check subscription limits
    if current_user.subscription_tier == "free" and current_user.documents_created_this_month >= 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free tier monthly limit reached. Please upgrade to Pro."
        )
    
    # Create project
    new_project = Project(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        query=project_data.query,
        document_type=project_data.document_type,
        output_format=project_data.output_format,
        generate_images=project_data.generate_images,
        status=ProjectStatus.PENDING
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Update user's monthly count
    current_user.documents_created_this_month += 1
    db.commit()
    
    # Queue background task for document generation
    background_tasks.add_task(
        generate_document_task,
        project_id=new_project.id,
        user_id=current_user.id
    )
    
    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    status: Optional[ProjectStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects for current user"""
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return None


@router.post("/{project_id}/cancel")
async def cancel_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a running project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status not in [ProjectStatus.PENDING, ProjectStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail="Can only cancel pending or processing projects"
        )
    
    project.status = ProjectStatus.CANCELLED
    project.updated_at = datetime.utcnow()
    db.commit()
    
    # Notify via WebSocket
    await manager.send_personal_message(
        json.dumps({
            "type": "project_cancelled",
            "project_id": project_id
        }),
        str(current_user.id)
    )
    
    return {"message": "Project cancelled successfully"}


@router.get("/{project_id}/status")
async def get_project_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time project status"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "id": project.id,
        "status": project.status,
        "progress": project.progress,
        "error_message": project.error_message
    }

