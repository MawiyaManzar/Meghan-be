"""
LangChain LLM Service for Gemini Integration
Handles LLM initialization and configuration for the Meghan chatbot.
"""
import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LangChain Gemini LLM instances."""
    
    def __init__(self):
        """Initialize the LLM service with API key validation."""
        self.api_key: Optional[str] = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY not set in environment variables. "
                "LLM functionality will not work until API key is configured."
            )
        self._llm_instance: Optional[ChatGoogleGenerativeAI] = None
    
    def get_llm(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> ChatGoogleGenerativeAI:
        """
        Get a configured ChatGoogleGenerativeAI instance.
        
        Args:
            model: Model name (default: from settings.GEMINI_MODEL)
            temperature: Sampling temperature (default: from settings.GEMINI_TEMPERATURE)
            top_p: Top-p sampling parameter (default: from settings.GEMINI_TOP_P)
            max_output_tokens: Maximum tokens in response (default: from settings.GEMINI_MAX_OUTPUT_TOKENS)
        
        Returns:
            Configured ChatGoogleGenerativeAI instance
        
        Raises:
            ValueError: If API key is not configured
        """
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please set GEMINI_API_KEY in your .env file."
            )
        
        # Use settings defaults if not provided
        if model is None:
            model = settings.GEMINI_MODEL
        if temperature is None:
            temperature = settings.GEMINI_TEMPERATURE
        if top_p is None:
            top_p = settings.GEMINI_TOP_P
        if max_output_tokens is None:
            max_output_tokens = settings.GEMINI_MAX_OUTPUT_TOKENS
        
        # Create new instance with specified parameters
        # Note: thinking_budget is a Gemini-specific parameter that may need
        # special handling depending on model version and LangChain support
        # For now, we rely on default model behavior
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=self.api_key,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
        )
        
        return llm
    
    def test_connection(self) -> dict:
        """
        Test the LLM connection by making a simple request.
        
        Returns:
            dict with 'success' (bool) and 'message' (str) or 'error' (str)
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "GEMINI_API_KEY is not configured"
                }
            
            llm = self.get_llm()
            
            # Make a simple test request
            response = llm.invoke("Say 'Hello' in one word.")
            
            return {
                "success": True,
                "message": "LLM connection successful",
                "test_response": response.content if hasattr(response, 'content') else str(response)
            }
        except Exception as e:
            logger.error(f"LLM connection test failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }


# Global LLM service instance
llm_service = LLMService()

