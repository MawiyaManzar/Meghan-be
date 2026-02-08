"""
Insights Schemas for Project Meghan

Handles weekly wellbeing insights and analysis.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import List, Optional


class MoodTrend(BaseModel):
    """Mood trend data point."""
    date: date
    mood: Optional[str] = None  # "Heavy", "Pulse", "Grounded"
    tier: Optional[str] = None  # "Green", "Yellow", "Red"
    source: Optional[str] = None  # Stress source if available


class TriggerPattern(BaseModel):
    """Identified trigger pattern."""
    trigger: str  # e.g., "Career/Academics", "Family", "Relationship"
    frequency: int  # Number of times this trigger appeared
    severity: str  # "low", "medium", "high" based on associated tier
    description: str  # Human-readable description


class ProgressIndicator(BaseModel):
    """Progress indicator showing positive change."""
    category: str  # e.g., "journaling", "chat_sessions", "hearts_earned"
    metric: str  # e.g., "5 journal entries", "3 chat sessions"
    improvement: str  # Description of improvement
    comparison: Optional[str] = None  # Comparison to previous week


class Recommendation(BaseModel):
    """Personalized recommendation."""
    type: str  # e.g., "self_care", "community", "reflection", "support"
    title: str
    description: str
    action: Optional[str] = None  # Suggested action


class WeeklyInsightsResponse(BaseModel):
    """Weekly wellbeing insights response."""
    week_starting: date
    week_ending: date
    
    # Mood trends
    mood_trends: List[MoodTrend] = []
    
    # Trigger patterns
    trigger_patterns: List[TriggerPattern] = []
    
    # Progress indicators
    positive_progress: List[ProgressIndicator] = []
    
    # Recommendations
    recommendations: List[Recommendation] = []
    
    # Encouragement message
    encouragement_message: str
    
    # Summary statistics
    total_journal_entries: int = 0
    total_chat_sessions: int = 0
    hearts_earned: int = 0
    most_common_mood: Optional[str] = None
    most_common_tier: Optional[str] = None
