"""
Database Configuration and Models
SQLAlchemy setup with models for the SaaS application
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from backend.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentType(str, enum.Enum):
    REPORT = "report"
    PPT = "ppt"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    DAILY = "daily"


# Models
class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for Clerk users
    full_name = Column(String(200))
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=True)  # Clerk user ID
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires = Column(DateTime, nullable=True)
    documents_created_this_month = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model - represents a document generation project"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    query = Column(Text, nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    generate_images = Column(Boolean, default=False)
    
    # Status
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    
    # Output
    output_path = Column(String(1000), nullable=True)
    output_format = Column(String(50), nullable=True)  # markdown, html, pdf, pptx
    output_size = Column(Integer, nullable=True)  # in bytes
    
    # Metadata (renamed to avoid SQLAlchemy reserved word conflict)
    project_metadata = Column(Text, nullable=True)  # JSON string
    search_results_count = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")


class APIKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    key = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class UsageLog(Base):
    """Usage tracking for analytics and billing"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    action = Column(String(100), nullable=False)  # create_document, search, etc.
    resource_type = Column(String(50), nullable=False)
    credits_used = Column(Integer, default=0)
    
    usage_metadata = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database session dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

