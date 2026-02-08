"""
Wellbeing Analyzer Service

Generates weekly insights by analyzing user activity data.
"""
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from collections import Counter
from app.models.user import (
    UserState,
    JournalEntry,
    Conversation,
    HeartsTransaction,
    User,
)
from app.schemas.insights import (
    WeeklyInsightsResponse,
    MoodTrend,
    TriggerPattern,
    ProgressIndicator,
    Recommendation,
)

logger = logging.getLogger(__name__)


class WellbeingAnalyzer:
    """
    Analyzes user wellbeing data and generates insights.
    """
    
    def __init__(self, llm_service=None):
        """
        Initialize the wellbeing analyzer.
        
        Args:
            llm_service: Optional LLM service for AI-generated insights
        """
        self.llm_service = llm_service
    
    def generate_weekly_insights(
        self,
        db: Session,
        user_id: int,
        week_start: Optional[date] = None
    ) -> WeeklyInsightsResponse:
        """
        Generate weekly wellbeing insights for a user.
        
        Args:
            db: Database session
            user_id: User ID
            week_start: Start date of the week (defaults to most recent Monday)
        
        Returns:
            WeeklyInsightsResponse with insights
        """
        # Calculate week range (default to most recent Monday)
        if week_start is None:
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
        
        week_end = week_start + timedelta(days=6)
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.max.time())
        
        logger.info(f"Generating weekly insights for user {user_id}, week {week_start} to {week_end}")
        
        # Aggregate data from various sources
        mood_trends = self._analyze_mood_trends(db, user_id, week_start_dt, week_end_dt)
        trigger_patterns = self._identify_trigger_patterns(db, user_id, week_start_dt, week_end_dt)
        progress_indicators = self._calculate_progress(db, user_id, week_start_dt, week_end_dt)
        recommendations = self._generate_recommendations(
            db, user_id, mood_trends, trigger_patterns, progress_indicators
        )
        encouragement_message = self._generate_encouragement_message(
            mood_trends, trigger_patterns, progress_indicators
        )
        
        # Summary statistics
        total_journal = self._count_journal_entries(db, user_id, week_start_dt, week_end_dt)
        total_chat = self._count_chat_sessions(db, user_id, week_start_dt, week_end_dt)
        hearts_earned = self._calculate_hearts_earned(db, user_id, week_start_dt, week_end_dt)
        most_common_mood = self._get_most_common_mood(mood_trends)
        most_common_tier = self._get_most_common_tier(mood_trends)
        
        return WeeklyInsightsResponse(
            week_starting=week_start,
            week_ending=week_end,
            mood_trends=mood_trends,
            trigger_patterns=trigger_patterns,
            positive_progress=progress_indicators,
            recommendations=recommendations,
            encouragement_message=encouragement_message,
            total_journal_entries=total_journal,
            total_chat_sessions=total_chat,
            hearts_earned=hearts_earned,
            most_common_mood=most_common_mood,
            most_common_tier=most_common_tier,
        )
    
    def _analyze_mood_trends(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> List[MoodTrend]:
        """Analyze mood trends from journal entries and conversations."""
        trends = []
        
        # Get journal entries with mood/tier data
        journal_entries = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.created_at >= week_start,
                JournalEntry.created_at <= week_end,
                JournalEntry.mood_at_time.isnot(None)
            )
            .order_by(JournalEntry.created_at.asc())
            .all()
        )
        
        for entry in journal_entries:
            trends.append(MoodTrend(
                date=entry.created_at.date(),
                mood=entry.mood_at_time,
                tier=entry.tier_at_time,
                source=None
            ))
        
        # Get conversations with mood/tier data
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.created_at >= week_start,
                Conversation.created_at <= week_end
            )
            .order_by(Conversation.created_at.asc())
            .all()
        )
        
        for conv in conversations:
            trends.append(MoodTrend(
                date=conv.created_at.date(),
                mood=conv.mood,
                tier=conv.tier,
                source=conv.source
            ))
        
        # Sort by date
        trends.sort(key=lambda x: x.date)
        
        return trends
    
    def _identify_trigger_patterns(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> List[TriggerPattern]:
        """Identify stress trigger patterns from conversations and journal entries."""
        triggers = []
        
        # Get stress sources from conversations
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.created_at >= week_start,
                Conversation.created_at <= week_end,
                Conversation.source.isnot(None)
            )
            .all()
        )
        
        # Count trigger frequencies
        trigger_counts = Counter()
        trigger_tiers = {}  # Track tier associated with each trigger
        
        for conv in conversations:
            trigger = conv.source
            trigger_counts[trigger] += 1
            # Track highest tier for this trigger
            if trigger not in trigger_tiers:
                trigger_tiers[trigger] = []
            trigger_tiers[trigger].append(conv.tier)
        
        # Build trigger patterns
        for trigger, frequency in trigger_counts.most_common():
            # Determine severity based on associated tiers
            tiers = trigger_tiers[trigger]
            if "Red" in tiers:
                severity = "high"
            elif "Yellow" in tiers:
                severity = "medium"
            else:
                severity = "low"
            
            # Generate description
            description = f"Appeared {frequency} time{'s' if frequency > 1 else ''} this week"
            if severity == "high":
                description += " with high concern levels"
            elif severity == "medium":
                description += " with moderate concern levels"
            
            triggers.append(TriggerPattern(
                trigger=trigger,
                frequency=frequency,
                severity=severity,
                description=description
            ))
        
        return triggers
    
    def _calculate_progress(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> List[ProgressIndicator]:
        """Calculate progress indicators for the week."""
        indicators = []
        
        # Journal entries progress
        journal_count = self._count_journal_entries(db, user_id, week_start, week_end)
        if journal_count > 0:
            indicators.append(ProgressIndicator(
                category="journaling",
                metric=f"{journal_count} journal entr{'ies' if journal_count > 1 else 'y'}",
                improvement="Great job reflecting on your thoughts and feelings!",
                comparison=None  # Could compare to previous week
            ))
        
        # Chat sessions progress
        chat_count = self._count_chat_sessions(db, user_id, week_start, week_end)
        if chat_count > 0:
            indicators.append(ProgressIndicator(
                category="chat_sessions",
                metric=f"{chat_count} chat session{'s' if chat_count > 1 else ''}",
                improvement="You've been actively engaging with support!",
                comparison=None
            ))
        
        # Hearts earned progress
        hearts = self._calculate_hearts_earned(db, user_id, week_start, week_end)
        if hearts > 0:
            indicators.append(ProgressIndicator(
                category="hearts_earned",
                metric=f"{hearts} hearts earned",
                improvement="You're building positive habits!",
                comparison=None
            ))
        
        return indicators
    
    def _generate_recommendations(
        self,
        db: Session,
        user_id: int,
        mood_trends: List[MoodTrend],
        trigger_patterns: List[TriggerPattern],
        progress_indicators: List[ProgressIndicator]
    ) -> List[Recommendation]:
        """Generate personalized recommendations based on insights."""
        recommendations = []
        
        # If no journal entries, recommend journaling
        if not any(p.category == "journaling" for p in progress_indicators):
            recommendations.append(Recommendation(
                type="reflection",
                title="Try Journaling",
                description="Journaling can help you process your thoughts and track your emotional journey.",
                action="Visit the journal section to get started"
            ))
        
        # If high frequency of triggers, recommend community support
        if trigger_patterns and any(tp.frequency >= 3 for tp in trigger_patterns):
            recommendations.append(Recommendation(
                type="community",
                title="Connect with Community",
                description="You've been dealing with some recurring challenges. Consider sharing with others who understand.",
                action="Explore communities that match your experiences"
            ))
        
        # If mostly positive trends, recommend maintaining habits
        if mood_trends and len([t for t in mood_trends if t.tier == "Green"]) > len(mood_trends) / 2:
            recommendations.append(Recommendation(
                type="self_care",
                title="Keep Up the Great Work",
                description="You've been maintaining positive wellbeing patterns. Continue the practices that are working for you.",
                action=None
            ))
        
        # Default recommendation if no specific ones
        if not recommendations:
            recommendations.append(Recommendation(
                type="self_care",
                title="Continue Your Journey",
                description="Every step forward matters. Keep engaging with the tools that help you feel supported.",
                action=None
            ))
        
        return recommendations
    
    def _generate_encouragement_message(
        self,
        mood_trends: List[MoodTrend],
        trigger_patterns: List[TriggerPattern],
        progress_indicators: List[ProgressIndicator]
    ) -> str:
        """Generate an encouraging message based on insights."""
        if not mood_trends and not progress_indicators:
            return "You're taking the first steps on your wellbeing journey. Every moment of self-reflection matters."
        
        # Count positive indicators
        positive_count = len(progress_indicators)
        
        if positive_count >= 3:
            return "You've had an incredibly active week! Your commitment to self-care and reflection is inspiring. Keep up the amazing work!"
        elif positive_count >= 2:
            return "You've been making great progress this week. Your efforts to engage with support and reflect on your experiences are making a difference."
        elif positive_count >= 1:
            return "You've taken positive steps this week. Remember, progress isn't always linear—every small action counts."
        else:
            return "This week has been part of your journey. Remember that seeking support and reflecting on your experiences are signs of strength."
    
    def _count_journal_entries(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> int:
        """Count journal entries in the week."""
        return (
            db.query(JournalEntry)
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.created_at >= week_start,
                JournalEntry.created_at <= week_end
            )
            .count()
        )
    
    def _count_chat_sessions(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> int:
        """Count chat sessions in the week."""
        return (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.created_at >= week_start,
                Conversation.created_at <= week_end
            )
            .count()
        )
    
    def _calculate_hearts_earned(
        self,
        db: Session,
        user_id: int,
        week_start: datetime,
        week_end: datetime
    ) -> int:
        """Calculate hearts earned in the week."""
        transactions = (
            db.query(HeartsTransaction)
            .filter(
                HeartsTransaction.user_id == user_id,
                HeartsTransaction.created_at >= week_start,
                HeartsTransaction.created_at <= week_end,
                HeartsTransaction.amount > 0  # Only count earnings
            )
            .all()
        )
        
        return sum(tx.amount for tx in transactions)
    
    def _get_most_common_mood(self, mood_trends: List[MoodTrend]) -> Optional[str]:
        """Get most common mood from trends."""
        if not mood_trends:
            return None
        
        moods = [t.mood for t in mood_trends if t.mood]
        if not moods:
            return None
        
        return Counter(moods).most_common(1)[0][0]
    
    def _get_most_common_tier(self, mood_trends: List[MoodTrend]) -> Optional[str]:
        """Get most common tier from trends."""
        if not mood_trends:
            return None
        
        tiers = [t.tier for t in mood_trends if t.tier]
        if not tiers:
            return None
        
        return Counter(tiers).most_common(1)[0][0]


# Global instance
wellbeing_analyzer = WellbeingAnalyzer()
