"""
Documents API
Download and manage generated documents
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import os

from backend.database import get_db, User, Project, ProjectStatus
from backend.clerk_auth import get_current_user

router = APIRouter()


@router.get("/{project_id}/download")
async def download_document(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download generated document"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Document is not ready yet"
        )
    
    if not project.output_path or not os.path.exists(project.output_path):
        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )
    
    # Determine media type
    media_types = {
        "html": "text/html",
        "markdown": "text/markdown",
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }
    
    media_type = media_types.get(project.output_format, "application/octet-stream")
    filename = f"{project.title}.{project.output_format}"
    
    return FileResponse(
        path=project.output_path,
        media_type=media_type,
        filename=filename
    )


@router.get("/{project_id}/preview")
async def preview_document(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview document content"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Document is not ready yet"
        )
    
    if not project.output_path or not os.path.exists(project.output_path):
        raise HTTPException(
            status_code=404,
            detail="Document file not found"
        )
    
    # Read file content
    with open(project.output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        "project_id": project.id,
        "title": project.title,
        "format": project.output_format,
        "content": content,
        "size": project.output_size
    }


@router.get("/{project_id}/metadata")
async def get_document_metadata(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document metadata and statistics"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project.id,
        "title": project.title,
        "document_type": project.document_type,
        "format": project.output_format,
        "size": project.output_size,
        "search_results_count": project.search_results_count,
        "processing_time": project.processing_time,
        "created_at": project.created_at,
        "completed_at": project.completed_at
    }

