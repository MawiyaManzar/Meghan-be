"""
Crisis detection and emergency resources router.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List

from app.core.dependencies import CurrentUser, DatabaseSession
from app.services.safety import safety_service
from app.schemas.crisis import (
    CrisisDetectionRequest,
    CrisisDetectionResponse,
    EmergencyResource,
    EmergencyResourcesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crisis", tags=["crisis"])


@router.post("/detect", response_model=CrisisDetectionResponse)
async def detect_crisis(
    payload: CrisisDetectionRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Manually assess text for crisis indicators.
    
    Can be called by frontend or used for testing.
    Returns risk assessment and recommended actions.
    """
    safety = safety_service.assess_user_message(payload.text)

    return CrisisDetectionResponse(
        risk_level=safety.risk_level,
        allowed=safety.allowed,
        matched_phrases=safety.matched_phrases,
        recommended_action=_get_recommended_action(safety.risk_level),
        safe_reply=safety.safe_reply,
    )


@router.get("/resources", response_model=EmergencyResourcesResponse)
async def get_emergency_resources(
    country: Optional[str] = None,
):
    """
    Get emergency resources and crisis hotlines.
    
    Args:
        country: Optional country code (e.g., "US", "CA", "GB") for localized resources
    
    Returns:
        List of emergency resources
    """
    resources = _get_resources_for_country(country)

    return EmergencyResourcesResponse(
        resources=resources,
        country=country or "International",
    )


def _get_recommended_action(risk_level: str) -> str:
    """Get recommended action based on risk level."""
    actions = {
        "high": "Immediate professional intervention required. Contact emergency services or crisis hotline.",
        "medium": "Consider reaching out to a mental health professional or trusted support person.",
        "low": "Continue monitoring. Consider self-care activities.",
    }
    return actions.get(risk_level, actions["low"])


def _get_resources_for_country(country: Optional[str]) -> List[EmergencyResource]:
    """Get emergency resources for a country (hardcoded for MVP)."""
    # Default international resources
    default_resources = [
        EmergencyResource(
            name="International Crisis Text Line",
            phone="Text HOME to 741741",
            website="https://www.crisistextline.org",
            available_24_7=True,
        ),
        EmergencyResource(
            name="International Association for Suicide Prevention",
            phone=None,
            website="https://www.iasp.info/resources/Crisis_Centres/",
            available_24_7=True,
        ),
    ]
    
    # Country-specific resources (can be expanded)
    country_resources = {
        "US": [
            EmergencyResource(
                name="National Suicide Prevention Lifeline",
                phone="988",
                website="https://988lifeline.org",
                available_24_7=True,
            ),
            EmergencyResource(
                name="Crisis Text Line",
                phone="Text HOME to 741741",
                website="https://www.crisistextline.org",
                available_24_7=True,
            ),
        ],
        "CA": [
            EmergencyResource(
                name="Crisis Services Canada",
                phone="1-833-456-4566",
                website="https://www.crisisservicescanada.ca",
                available_24_7=True,
            ),
        ],
        "IN": [
            EmergencyResource(
                name="Kiran Mental Health Rehabilitation Helpline (Govt. of India)",
                phone="1800-599-0019",
                website="https://www.mohfw.gov.in/",
                available_24_7=True,
            ),
            EmergencyResource(
                name="AASRA",
                phone="+91-9820466726",
                website="https://aasra.info/",
                available_24_7=True,
            ),
            EmergencyResource(
                name="iCALL (TISS)",
                phone="+91-9152987821",
                website="https://icallhelpline.org/",
                available_24_7=False,
            ),
        ]

        # Add more countries as needed
    }
    
    if country and country.upper() in country_resources:
        return country_resources[country.upper()] + default_resources
    
    return default_resources