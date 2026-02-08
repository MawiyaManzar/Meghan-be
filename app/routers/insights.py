"""
Insights router for weekly wellbeing insights generation.
"""
import logging
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.core.dependencies import CurrentUser, DatabaseSession
from app.schemas.insights import WeeklyInsightsResponse
from app.services.wellbeing import wellbeing_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/weekly", response_model=WeeklyInsightsResponse)
async def get_weekly_insights(
    current_user: CurrentUser,
    db: DatabaseSession,
    week_start: Optional[date] = Query(
        None,
        description="Start date of the week (defaults to most recent Monday). Format: YYYY-MM-DD"
    )
):
    """
    Get weekly wellbeing insights for the current user.
    
    Aggregates data from:
    - Journal entries (mood trends, reflection patterns)
    - Chat conversations (stress sources, tier patterns)
    - Hearts transactions (engagement metrics)
    - User state snapshots (if available)
    
    Returns personalized insights including:
    - Mood trends over the week
    - Trigger pattern identification
    - Progress indicators
    - Personalized recommendations
    - Encouragement message
    
    Args:
        current_user: Current authenticated user
        db: Database session
        week_start: Optional start date of the week (defaults to most recent Monday)
    
    Returns:
        WeeklyInsightsResponse with all insights
    """
    try:
        insights = wellbeing_analyzer.generate_weekly_insights(
            db=db,
            user_id=current_user.id,
            week_start=week_start
        )
        
        logger.info(f"Generated weekly insights for user {current_user.id}, week {insights.week_starting}")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating weekly insights for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate weekly insights. Please try again later."
        )
