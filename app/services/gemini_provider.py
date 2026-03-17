"""
Gemini chat provider implementation for Meghan.

This module adapts the LangChain Gemini client to the `ChatService` provider
contract (`ChatPrompt` -> `ChatResult`).
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.services.chat_contract import ChatPrompt, ChatResult
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class GeminiChatService:
    """Gemini-backed provider used by ChatService in production."""

    def generate_chat_response(self, prompt: ChatPrompt) -> ChatResult:
        try:
            llm = llm_service.get_llm(
                model=settings.GEMINI_MODEL,
                temperature=prompt.temperature,
                max_output_tokens=prompt.max_tokens,
            )

            messages: list[Any] = []
            if prompt.system_prompt:
                messages.append(SystemMessage(content=prompt.system_prompt))
            messages.append(HumanMessage(content=prompt.user_message))

            response = llm.invoke(messages)
            content = getattr(response, "content", None) or str(response)
            content = content.strip()

            if not content:
                return ChatResult(
                    success=False,
                    content="I am sorry, I am having trouble responding right now. Please try again shortly.",
                    error="Gemini response was empty.",
                    model_id=settings.GEMINI_MODEL,
                )

            return ChatResult(
                success=True,
                content=content,
                error=None,
                model_id=settings.GEMINI_MODEL,
            )
        except Exception as exc:
            logger.error("Gemini invocation failed: %s", exc, exc_info=True)
            return ChatResult(
                success=False,
                content="I am sorry, I am having trouble responding right now. Please try again shortly.",
                error=str(exc),
                model_id=settings.GEMINI_MODEL,
            )

