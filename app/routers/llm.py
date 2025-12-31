"""
LLM test and management endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.llm import llm_service
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/llm", tags=["LLM"])


@router.get("/test")
async def test_llm_connection(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Test endpoint to verify LLM connection works.
    Requires authentication.
    
    Returns:
        dict with connection test results
    """
    result = llm_service.test_connection()
    
    if not result["success"]:
        raise HTTPException(
            status_code=503,
            detail=result.get("error", "LLM service unavailable")
        )
    
    return result


@router.get("/health")
async def llm_health():
    """
    Health check for LLM service (no authentication required).
    Only checks if API key is configured, doesn't make actual API call.
    
    Returns:
        dict with health status
    """
    if not llm_service.api_key:
        return {
            "status": "unhealthy",
            "message": "GEMINI_API_KEY is not configured"
        }
    
    return {
        "status": "healthy",
        "message": "API key is configured"
    }

