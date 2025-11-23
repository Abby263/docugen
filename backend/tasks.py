"""
Background Tasks
Handles async document generation and processing
"""

import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path
import os
import time
import json
from loguru import logger

from backend.database import SessionLocal, Project, ProjectStatus, DocumentType
from backend.websocket_manager import manager
from backend.config import settings

# Import content generation components
from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMManager


async def generate_document_task(project_id: int, user_id: int):
    """
    Background task to generate document
    This runs asynchronously after a project is created
    """
    db = SessionLocal()
    
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"❌ Project {project_id} not found")
            return
        
        logger.info(f"Starting document generation task for project {project_id} (User: {user_id})")
        
        # Update status to processing
        project.status = ProjectStatus.PROCESSING
        project.progress = 0
        db.commit()
        
        # Send initial progress update
        await manager.send_progress_update(
            client_id=str(user_id),
            project_id=project_id,
            progress=0,
            status="processing",
            message="Starting document generation..."
        )
        
        start_time = time.time()
        
        # Initialize LLM Manager and Deep Search Agent
        llm_manager = LLMManager()
        search_agent = DeepSearchAgent(llm_manager=llm_manager)
        
        # Update progress
        project.progress = 10
        db.commit()
        await manager.send_progress_update(
            client_id=str(user_id),
            project_id=project_id,
            progress=10,
            status="processing",
            message="Initialized search agent..."
        )
        
        # Prepare context based on document type
        context = {
            "document_type": project.document_type.value,
            "output_format": project.output_format,
            "document_type": project.document_type.value,
            "output_format": project.output_format,
            "title": project.title,
            "generate_images": project.generate_images
        }
        
        # Execute deep search
        project.progress = 20
        db.commit()
        await manager.send_progress_update(
            client_id=str(user_id),
            project_id=project_id,
            progress=20,
            status="processing",
            message="Executing deep search..."
        )
        
        result = await search_agent.search(query=project.query, context=context)
        
        # Update progress
        project.progress = 60
        db.commit()
        await manager.send_progress_update(
            client_id=str(user_id),
            project_id=project_id,
            progress=60,
            status="processing",
            message="Search completed, generating document..."
        )
        
        # Check if search was successful
        if result.get("status") != "success":
            raise Exception(result.get("error", "Unknown error during search"))
        
        # Store search metadata
        project.search_results_count = result.get("search_results_count", 0)
        project.project_metadata = json.dumps({
            "sources": result.get("sources", []),
            "subtasks": result.get("subtasks", [])
        })
        
        # Update progress
        project.progress = 80
        db.commit()
        await manager.send_progress_update(
            client_id=str(user_id),
            project_id=project_id,
            progress=80,
            status="processing",
            message="Finalizing document..."
        )
        
        # Get output path from result
        output_path = result.get("output_path")
        
        # If output_path is missing, try to find it in project_dir
        if not output_path:
            project_dir = result.get("project_dir")
            if project_dir:
                # Check for HTML report first
                html_path = os.path.join(project_dir, "reports", "FINAL_REPORT.html")
                if os.path.exists(html_path):
                    output_path = html_path
                else:
                    # Check for Markdown report
                    md_path = os.path.join(project_dir, "reports", "FINAL_REPORT.md")
                    if os.path.exists(md_path):
                        output_path = md_path
        
        if not output_path or not os.path.exists(output_path):
            raise Exception(f"Generated document not found. Project dir: {result.get('project_dir')}")
        
        # Calculate file size
        file_size = os.path.getsize(output_path)
        
        # Update project with completion info
        processing_time = time.time() - start_time
        
        project.status = ProjectStatus.COMPLETED
        project.progress = 100
        project.output_path = output_path
        project.output_size = file_size
        project.processing_time = processing_time
        project.completed_at = datetime.utcnow()
        db.commit()
        
        # Send completion notification
        await manager.send_completion_notification(
            client_id=str(user_id),
            project_id=project_id,
            output_path=output_path
        )
        
        logger.info(f"✅ Document generated successfully for project {project_id}")
        logger.info(f"   Output: {output_path}")
        logger.info(f"   Time: {processing_time:.2f}s")
        logger.info(f"   Size: {file_size} bytes")
        
    except Exception as e:
        logger.error(f"❌ Error generating document for project {project_id}: {str(e)}")
        
        # Update project with error
        project.status = ProjectStatus.FAILED
        project.error_message = str(e)
        project.updated_at = datetime.utcnow()
        db.commit()
        
        # Send error notification
        await manager.send_error_notification(
            client_id=str(user_id),
            project_id=project_id,
            error=str(e)
        )
    
    finally:
        db.close()


def schedule_periodic_cleanup():
    """
    Cleanup old projects and files
    Can be called periodically by a scheduler (e.g., celery beat)
    """
    db = SessionLocal()
    
    try:
        # Delete projects older than 30 days (configurable)
        # Add your cleanup logic here
        pass
    finally:
        db.close()

