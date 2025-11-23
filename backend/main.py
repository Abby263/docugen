"""
DocuGen AI - Main FastAPI Application
Full-stack web application for document and PPT generation
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api import auth, projects, documents, analytics
from backend.database import engine, Base, get_db
from backend.config import settings
from backend.websocket_manager import manager

# Import core modules
from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting DocuGen AI Application...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Initialize LLM Manager
    app.state.llm_manager = LLMManager()
    print("✅ LLM Manager initialized")
    
    # Initialize Deep Search Agent
    app.state.search_agent = DeepSearchAgent(llm_manager=app.state.llm_manager)
    print("✅ Deep Search Agent initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down DocuGen AI Application...")


# Create FastAPI app
app = FastAPI(
    title="DocuGen AI API",
    description="AI-powered document and presentation generation platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DocuGen AI API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "llm": "operational"
        }
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Echo back for now (can be extended for bidirectional communication)
            await manager.send_personal_message(f"Message received: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

