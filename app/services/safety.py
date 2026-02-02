import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SafetyResult:
    allowed: bool
    risk_level: str  # "low" | "medium" | "high"
    matched_phrases: List[str]
    user_message: str
    safe_reply: Optional[str] = None


class SafetyService:
    """
    V1 Safety Gate:
    - keyword/phrase based crisis detection
    - returns SafetyResult
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

    def assess_user_message(self, text: str) -> SafetyResult:
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

        return SafetyResult(
            allowed=True,
            risk_level="low",
            matched_phrases=[],
            user_message=text,
        )


# global instance (simple pattern like your chat_service)
safety_service = SafetyService()