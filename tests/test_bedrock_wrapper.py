"""
TDD tests for the Bedrock wrapper service (A2.3).

These tests are expected to fail until `app/services/aws_bedrock.py` is implemented.
"""

import io
import json
import importlib

import pytest

from app.services.bedrock_contract import ChatMode, ChatPrompt, ChatResult


def _load_bedrock_module():
    """
    Import wrapper module at runtime so test collection still succeeds.
    We intentionally fail inside tests (not at import time) if the module is missing.
    """
    try:
        return importlib.import_module("app.services.aws_bedrock")
    except ModuleNotFoundError as exc:
        pytest.fail(
            "A2.3 expected failure: implement `app/services/aws_bedrock.py` "
            "with BedrockChatService and generate_chat_response(). "
            f"Original error: {exc}"
        )


class FakeBedrockClient:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls = []

    def invoke_model(self, **kwargs):
        self.calls.append(kwargs)
        return {"body": io.BytesIO(json.dumps(self.payload).encode("utf-8"))}


def test_generate_chat_response_parses_success_payload():
    module = _load_bedrock_module()
    service = module.BedrockChatService(
        client=FakeBedrockClient(
            payload={
                "output": {"message": {"content": [{"text": "You are doing great."}]}}
            }
        ),
        model_id="amazon.nova-micro-v1:0",
    )

    prompt = ChatPrompt(
        user_message="I feel stuck today",
        mode=ChatMode.TALK,
        temperature=0.7,
        max_tokens=300,
    )
    result = service.generate_chat_response(prompt)

    assert isinstance(result, ChatResult)
    assert result.success is True
    assert result.content == "You are doing great."
    assert result.model_id == "amazon.nova-micro-v1:0"


def test_generate_chat_response_invalid_payload_returns_fallback():
    module = _load_bedrock_module()
    service = module.BedrockChatService(
        client=FakeBedrockClient(payload={"unexpected": "shape"}),
        model_id="amazon.nova-micro-v1:0",
    )

    result = service.generate_chat_response(
        ChatPrompt(user_message="hello", mode=ChatMode.PLAN)
    )

    assert isinstance(result, ChatResult)
    assert result.success is False
    assert result.error is not None
    assert isinstance(result.content, str)
    assert len(result.content) > 0


@pytest.mark.parametrize(
    ("mode", "expected_keyword"),
    [
        (ChatMode.TALK, "support"),
        (ChatMode.PLAN, "plan"),
        (ChatMode.CALM, "calm"),
        (ChatMode.REFLECT, "reflect"),
    ],
)
def test_mode_to_system_prompt_mapping(mode, expected_keyword):
    module = _load_bedrock_module()
    service = module.BedrockChatService(client=FakeBedrockClient(payload={}))

    system_prompt = service.build_system_prompt(mode)

    assert isinstance(system_prompt, str)
    assert expected_keyword in system_prompt.lower()
    assert len(system_prompt.strip()) > 0

