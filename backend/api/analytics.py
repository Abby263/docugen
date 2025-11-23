"""
Analytics API
Usage statistics and insights
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.database import get_db, User, Project, ProjectStatus
from backend.clerk_auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics for current user"""
    
    # Total projects
    total_projects = db.query(func.count(Project.id)).filter(
        Project.user_id == current_user.id
    ).scalar()
    
    # Completed projects
    completed_projects = db.query(func.count(Project.id)).filter(
        Project.user_id == current_user.id,
        Project.status == ProjectStatus.COMPLETED
    ).scalar()
    
    # Projects this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    projects_this_month = db.query(func.count(Project.id)).filter(
        Project.user_id == current_user.id,
        Project.created_at >= first_day_of_month
    ).scalar()
    
    # Average processing time
    avg_processing_time = db.query(func.avg(Project.processing_time)).filter(
        Project.user_id == current_user.id,
        Project.status == ProjectStatus.COMPLETED
    ).scalar() or 0
    
    # Projects by status
    projects_by_status = {}
    for status in ProjectStatus:
        count = db.query(func.count(Project.id)).filter(
            Project.user_id == current_user.id,
            Project.status == status
        ).scalar()
        projects_by_status[status.value] = count
    
    # Projects by type
    projects_by_type = db.query(
        Project.document_type,
        func.count(Project.id).label('count')
    ).filter(
        Project.user_id == current_user.id
    ).group_by(Project.document_type).all()
    
    projects_by_type_dict = {item[0].value: item[1] for item in projects_by_type}
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(
        func.date(Project.created_at).label('date'),
        func.count(Project.id).label('count')
    ).filter(
        Project.user_id == current_user.id,
        Project.created_at >= seven_days_ago
    ).group_by(func.date(Project.created_at)).all()
    
    activity_by_date = {str(item[0]): item[1] for item in recent_activity}
    
    return {
        "summary": {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "projects_this_month": projects_this_month,
            "monthly_limit": get_monthly_limit(current_user.subscription_tier.value),
            "avg_processing_time": round(avg_processing_time, 2) if avg_processing_time else 0
        },
        "projects_by_status": projects_by_status,
        "projects_by_type": projects_by_type_dict,
        "recent_activity": activity_by_date,
        "subscription": {
            "tier": current_user.subscription_tier.value,
            "documents_used": current_user.documents_created_this_month,
            "documents_remaining": max(0, get_monthly_limit(current_user.subscription_tier.value) - current_user.documents_created_this_month)
        }
    }


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed usage statistics"""
    
    # Monthly breakdown (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    monthly_usage = db.query(
        func.strftime('%Y-%m', Project.created_at).label('month'),
        func.count(Project.id).label('count')
    ).filter(
        Project.user_id == current_user.id,
        Project.created_at >= six_months_ago
    ).group_by(func.strftime('%Y-%m', Project.created_at)).all()
    
    usage_by_month = [
        {"month": item[0], "count": item[1]}
        for item in monthly_usage
    ]
    
    # Total search results
    total_search_results = db.query(func.sum(Project.search_results_count)).filter(
        Project.user_id == current_user.id
    ).scalar() or 0
    
    # Total processing time
    total_processing_time = db.query(func.sum(Project.processing_time)).filter(
        Project.user_id == current_user.id,
        Project.status == ProjectStatus.COMPLETED
    ).scalar() or 0
    
    return {
        "usage_by_month": usage_by_month,
        "total_search_results": total_search_results,
        "total_processing_time": round(total_processing_time, 2),
        "account_age_days": (datetime.utcnow() - current_user.created_at).days
    }


def get_monthly_limit(tier: str) -> int:
    """Get monthly document limit for subscription tier"""
    limits = {
        "free": 5,
        "pro": 50,
        "enterprise": 999999
    }
    return limits.get(tier, 5)

