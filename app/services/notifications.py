"""
Therapist notification service (stub implementation).
"""
import logging
from typing import Optional
from app.models.user import CrisisEvent

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Handles therapist notifications for crisis events.
    
    MVP: Logs notifications (can be enhanced with email/SMS/webhooks later).
    """
    
    def notify_therapist_crisis(
        self,
        crisis_event: CrisisEvent,
        user_context: Optional[dict] = None,
    ) -> bool:
        """
        Notify therapist of a new crisis event.
        
        Args:
            crisis_event: The crisis event that triggered the notification
            user_context: Optional user context (respecting privacy settings)
        
        Returns:
            True if notification sent successfully
        """
        logger.warning(
            f"CRISIS ALERT: User {crisis_event.user_id} - "
            f"Source: {crisis_event.source}, "
            f"Risk Level: {crisis_event.risk_level}, "
            f"Excerpt: {crisis_event.message_excerpt[:100]}"
        )
        
        # TODO: In production, implement:
        # - Email notification to therapist
        # - SMS alert for high-risk cases
        # - Webhook to therapist dashboard
        # - Push notification to therapist app
        
        # For now, just log (therapist can see via /api/therapist/crisis-events)
        return True


# Global instance
notification_service = NotificationService()