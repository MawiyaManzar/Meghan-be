"""
Chat Service for handling conversations with the LLM.
Manages chat history, context, and LLM interactions.
"""
import logging
from typing import List, Dict, Any, Optional, Protocol
from app.services.chat_contract import ChatPrompt, ChatMode
from app.services.gemini_provider import GeminiChatService
from app.services.prompts import (
    generate_system_instructions
)

logger = logging.getLogger(__name__)


class ChatProvider(Protocol):
    """Minimal provider contract so ChatService can swap AI backends."""

    def generate_chat_response(self, prompt: ChatPrompt): ...


class ChatService:
    """Service for managing chat conversations with the LLM."""
    
    def __init__(self, provider: Optional[ChatProvider] = None):
        """Initialize chat service with an injectable AI provider."""
        self.provider = provider or GeminiChatService()
    
    async def generate_response(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        tier: str,
        mood: str,
        source: str,
        bio: Optional[Dict[str, Any]] = None,
        other_text: Optional[str] = None,
        mode: ChatMode | str = ChatMode.TALK,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM based on user message and context.
        
        Args:
            user_message: The current user message
            chat_history: List of previous messages (each with 'role' and 'content')
            tier: Risk tier ('Green', 'Yellow', 'Red')
            mood: Current mood ('Heavy', 'Pulse', 'Grounded')
            source: Stress source ('Family', 'Relationship', 'Career/Academics', 'Others')
            bio: Optional dict with user bio info (name, major, hobbies, values, bio)
            other_text: Optional text when source is 'Others'
            mode: Chat mode ('talk' or 'plan')
            model: Optional model name override
            temperature: Optional temperature override
            top_p: Optional top_p override
            max_output_tokens: Optional max_output_tokens override
        
        Returns:
            dict with 'content' (str) and 'success' (bool), optionally 'error' (str)
        
        Raises:
            ValueError: If required parameters are missing
        """
        try:
            mode_value = ChatMode(mode)
            prompt_contract = ChatPrompt(
                user_message=user_message,
                mode=mode_value,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )

            # Generate system instructions
            system_instructions = generate_system_instructions(
                tier=tier,
                mood=mood,
                source=source,
                bio=bio,
                other_text=other_text,
                mode=prompt_contract.mode.value
            )
            
            logger.debug(
                "Generated system instructions for tier=%s, mood=%s, source=%s, mode=%s",
                tier,
                mood,
                source,
                mode_value.value,
            )

            history_block = self._render_history(chat_history)
            merged_user_message = (
                f"{history_block}\n\nCurrent user message:\n{prompt_contract.user_message}"
                if history_block
                else prompt_contract.user_message
            )

            provider_prompt = ChatPrompt(
                system_prompt=system_instructions,
                user_message=merged_user_message,
                mode=prompt_contract.mode,
                temperature=prompt_contract.temperature,
                max_tokens=prompt_contract.max_tokens,
            )

            provider_result = self.provider.generate_chat_response(provider_prompt)
            content = provider_result.content or self._get_fallback_response(tier)
            if not provider_result.success:
                logger.warning(
                    "Provider returned unsuccessful result (mode=%s, tier=%s, source=%s, error=%s)",
                    mode_value.value,
                    tier,
                    source,
                    provider_result.error,
                )
            
            logger.info("AI response generated (success=%s, length=%s)", provider_result.success, len(content))
            
            return {
                "success": provider_result.success,
                "content": content,
                "error": provider_result.error,
            }
            
        except ValueError as e:
            # Configuration errors
            logger.error(f"Configuration error in chat service: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
        except Exception as e:
            # General errors - provide fallback response
            logger.error(f"Error generating chat response: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to generate response ({type(e).__name__}): {str(e)}",
                "content": self._get_fallback_response(tier)
            }

    def _render_history(self, chat_history: List[Dict[str, str]]) -> str:
        if not chat_history:
            return ""
        history_lines = []
        for message in chat_history:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            history_lines.append(f"{role}: {content}")
        return "Previous conversation context:\n" + "\n".join(history_lines)
    
    def _get_fallback_response(self, tier: str) -> str:
        """
        Get a fallback response when LLM fails.
        
        Args:
            tier: Risk tier to determine appropriate fallback message
        
        Returns:
            Fallback message string
        """
        fallback_messages = {
            "Red": (
                "I'm sorry, I'm having technical difficulties right now. "
                "Please know that your feelings are valid, and if you need immediate support, "
                "please reach out to a trusted friend, family member, or a mental health professional. "
                "You can also contact a crisis helpline for immediate support."
            ),
            "Yellow": (
                "I'm experiencing some technical difficulties, but I'm here for you. "
                "Take a moment to breathe. If you need support, consider reaching out to someone you trust, "
                "or try a brief wellness activity like taking a walk or doing some deep breathing."
            ),
            "Green": (
                "I'm having some technical difficulties at the moment. "
                "Please try again in a moment, or feel free to continue our conversation when I'm back up."
            )
        }
        
        return fallback_messages.get(tier, fallback_messages["Yellow"])
    
    def validate_context(
        self,
        tier: str,
        mood: str,
        source: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate user context parameters.
        
        Args:
            tier: Risk tier
            mood: Mood
            source: Stress source
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_tiers = {"Green", "Yellow", "Red"}
        valid_moods = {"Heavy", "Pulse", "Grounded"}
        valid_sources = {"Family", "Relationship", "Career/Academics", "Others"}
        
        if tier not in valid_tiers:
            return False, f"Invalid tier: {tier}. Must be one of {valid_tiers}"
        if mood not in valid_moods:
            return False, f"Invalid mood: {mood}. Must be one of {valid_moods}"
        if source not in valid_sources:
            return False, f"Invalid source: {source}. Must be one of {valid_sources}"
        
        return True, None


# Global chat service instance
chat_service = ChatService()

