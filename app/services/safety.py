import re
from dataclasses import dataclass
from typing import List, Optional
from langchain_core.messages import HumanMessage
import logging
from app.services.llm import llm_service

# Global instance (initialized with LLM service)


@dataclass
class SafetyResult:
    allowed: bool
    risk_level: str  # "low" | "medium" | "high"
    matched_phrases: List[str]
    user_message: str
    safe_reply: Optional[str] = None
    llm_assessment: Optional[str] = None  # LLM's risk assessment if used



class SafetyService:
    """
    Enhanced Safety Gate:
    - Keyword/phrase based crisis detection (fast path)
    - LLM-based risk assessment for nuanced detection (fallback)
    - Returns SafetyResult
    """
    

    # very small starter list (you can expand later)
    HIGH_RISK_PATTERNS = [
        r"\bkill myself\b",
        r"\bsuicide\b",
        r"\bend my life\b",
        r"\bdon't want to live\b",
        r"\bwant to die\b",
        r"\bself harm\b",
        r"\bhurt myself\b",
    ]

    MEDIUM_RISK_PATTERNS = [
        r"\bhopeless\b",
        r"\bworthless\b",
        r"\bno point\b",
        r"\bcan't go on\b",
    ]

    def __init__(self,llm_service=None):
        """
        Initialize safety service.
        
        Args:
            llm_service: Optional LLM service for enhanced risk assessment
        """
        self.llm_service=llm_service

    def assess_user_message(self, text: str) -> SafetyResult:
        """
        Assess user message for crisis indicators.
        Uses keyword matching first, then LLM if available and needed.
        """
        normalized = (text or "").lower().strip()
        matches = []

        for pat in self.HIGH_RISK_PATTERNS:
            if re.search(pat, normalized):
                matches.append(pat)

        if matches:
            # Block normal flow, return safe crisis response
            safe_reply = (
                "I’m really sorry you’re feeling this way. You don’t have to go through this alone.\n\n"
                "If you are in immediate danger or might act on these thoughts, please contact local emergency services now.\n\n"
                "If you can, reach out to someone you trust right now (friend/family/mentor).\n\n"
                "If you tell me your country, I can share crisis hotline resources for your area. "
                "Are you safe right now?"
            )
            return SafetyResult(
                allowed=False,
                risk_level="high",
                matched_phrases=matches,
                user_message=text,
                safe_reply=safe_reply,
            )
        
        # check for medium-risk patterns
        medium_matches=[]
        for pat in self.MEDIUM_RISK_PATTERNS:
            if re.search(pat,normalized):
                medium_matches.append(pat)
        
        if medium_matches and self.llm_service:
            try:
                llm_assessment = self._assess_with_llm(text)
                if llm_assessment and llm_assessment.get("risk_level") in ["medium", "high"]:
                    return SafetyResult(
                        allowed=False,
                        risk_level=llm_assessment["risk_level"],
                        matched_phrases=medium_matches,
                        user_message=text,
                        safe_reply=llm_assessment.get("safe_reply", self._get_default_safe_reply()),
                        llm_assessment=llm_assessment.get("reasoning"),
                    )
            except Exception as e:
                logger.error(f"LLM assessment failed: {e}")

        return SafetyResult(
            allowed=True,
            risk_level="low",
            matched_phrases=[],
            user_message=text,
        )
    def _assess_with_llm(self, text: str) -> Optional[dict]:
        """
        Use LLM to assess risk level with nuanced understanding.
        
        Returns:
            dict with 'risk_level', 'safe_reply', 'reasoning' or None if LLM unavailable
        """
        if not self.llm_service:
            return None
        try:
            prompt = f"""Analyse the following message for mental health. 
            Message: "{text}"

            Assess the risk level:
            - "high": Clear self-harm or suicide ideation, immediate danger
            - "medium": Concerning distress, hopelessness, but not immediate crisis
            - "low": Normal emotional expression, no crisis indicators

            Respond in JSON format:
            {{
                "risk_level": "high|medium|low",
                "reasoning": "brief explanation",
                "safe_reply": "supportive, non-clinical response to offer help"
            }}"""
            llm = self.llm_service.get_llm(temperature=0.1)
            response = llm.invoke([HumanMessage(content=prompt)])

            # Parse LLM response (simplified - in production, use structured output)
            # For now, return structured response
            content = response.content if hasattr(response, 'content') else str(response)
            # Simple parsing (in production, use JSON mode or structured output)
            if "high" in content.lower():
                return {
                    "risk_level": "high",
                    "reasoning": content,
                    "safe_reply": self._get_default_safe_reply()
                }
            elif "medium" in content.lower():
                return {
                    "risk_level": "medium",
                    "reasoning": content,
                    "safe_reply": "I'm concerned about how you're feeling. Would you like to talk about what's going on?"
                }
            
            return {"risk_level": "low", "reasoning": content}
            
        except Exception as e:
            logger.error(f"LLM risk assessment failed: {e}")
            return None
        
    def _get_default_safe_reply(self) -> str:
        """Get default safe reply for crisis situations."""
        return (
            "I'm really sorry you're feeling this way. You don't have to go through this alone.\n\n"
            "If you are in immediate danger, please contact local emergency services now.\n\n"
            "Please reach out to someone you trust, or contact a crisis helpline. "
            "You can find resources at /api/crisis/resources"
        )

            





logger = logging.getLogger(__name__)
safety_service = SafetyService(llm_service=llm_service)