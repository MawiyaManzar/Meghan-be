"""
AWS Bedrock chat wrapper for Meghan.

This module keeps Bedrock-specific request/response handling in one place so
the chat service can swap providers without changing endpoint contracts.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.core.config import settings
from app.services.bedrock_contract import ChatMode, ChatPrompt, ChatResult

logger = logging.getLogger(__name__)


class BedrockChatService:
    """Small wrapper around Bedrock Runtime for chat generation."""

    def __init__(
        self,
        client: Any | None = None,
        model_id: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        self.model_id = model_id or settings.BEDROCK_MODEL_ID
        self.region_name = region_name or settings.AWS_REGION
        self.client = client or self._build_default_client()

    def _build_default_client(self) -> Any:
        # Lazy import to keep module import lightweight in test environments.
        import boto3

        return boto3.client("bedrock-runtime", region_name=self.region_name)

    def build_system_prompt(self, mode: ChatMode | str) -> str:
        mode_value = ChatMode(mode).value if isinstance(mode, str) else mode.value
        prompts = {
            ChatMode.TALK.value: (
                "You are a supportive wellbeing assistant. "
                "Respond with empathy and practical support."
            ),
            ChatMode.PLAN.value: (
                "You are a planning-focused wellbeing assistant. "
                "Help the user make a clear, step-by-step plan."
            ),
            ChatMode.CALM.value: (
                "You are a calming wellbeing assistant. "
                "Guide the user toward calm breathing and grounding."
            ),
            ChatMode.REFLECT.value: (
                "You are a reflective wellbeing assistant. "
                "Help the user reflect gently and gain perspective."
            ),
        }
        return prompts.get(mode_value, prompts[ChatMode.TALK.value])

    def generate_chat_response(self, prompt: ChatPrompt) -> ChatResult:
        system_prompt = prompt.system_prompt or self.build_system_prompt(prompt.mode)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt.user_message}],
                }
            ],
            "system": [{"text": system_prompt}],
        }

        if prompt.temperature is not None:
            body["inferenceConfig"] = {
                **body.get("inferenceConfig", {}),
                "temperature": prompt.temperature,
            }
        if prompt.max_tokens is not None:
            body["inferenceConfig"] = {
                **body.get("inferenceConfig", {}),
                "maxTokens": prompt.max_tokens,
            }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
            raw = self._parse_response_body(response)
            content = self._extract_text_content(raw)
            if not content:
                return ChatResult(
                    success=False,
                    content=self._fallback_message(),
                    error="Bedrock response did not include text content.",
                    model_id=self.model_id,
                    raw_response=raw,
                )

            return ChatResult(
                success=True,
                content=content,
                error=None,
                model_id=self.model_id,
                raw_response=raw,
            )
        except Exception as exc:
            logger.error("Bedrock invocation failed: %s", exc, exc_info=True)
            return ChatResult(
                success=False,
                content=self._fallback_message(),
                error=str(exc),
                model_id=self.model_id,
            )

    def _parse_response_body(self, response: dict[str, Any]) -> dict[str, Any]:
        body = response.get("body")
        if body is None:
            return {}

        if hasattr(body, "read"):
            raw_text = body.read().decode("utf-8")
        elif isinstance(body, (bytes, bytearray)):
            raw_text = body.decode("utf-8")
        else:
            raw_text = str(body)

        if not raw_text.strip():
            return {}

        return json.loads(raw_text)

    def _extract_text_content(self, payload: dict[str, Any]) -> Optional[str]:
        # Nova-style nested output format:
        # {"output": {"message": {"content": [{"text": "..."}]}}}
        try:
            nested = payload["output"]["message"]["content"]
            if isinstance(nested, list):
                for item in nested:
                    text = item.get("text") if isinstance(item, dict) else None
                    if text:
                        return str(text)
        except Exception:
            pass

        # Alternate direct content format:
        # {"content": [{"text": "..."}]}
        top_level = payload.get("content")
        if isinstance(top_level, list):
            for item in top_level:
                text = item.get("text") if isinstance(item, dict) else None
                if text:
                    return str(text)

        return None

    def _fallback_message(self) -> str:
        return "I am sorry, I am having trouble responding right now. Please try again shortly."

