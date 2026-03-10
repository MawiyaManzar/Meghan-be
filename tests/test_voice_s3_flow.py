"""
Integration tests for voice endpoint S3 wiring (A3.6).
"""

from fastapi import status


class TestVoiceS3Flow:
    def test_voice_endpoint_persists_s3_key_and_returns_presigned_url(
        self, client, auth_headers, monkeypatch
    ):
        from app.routers import voice as voice_router
        from app.core.config import settings

        class FakeStorage:
            def __init__(self):
                self.upload_calls = []
                self.presign_calls = []

            def upload_media_bytes(
                self,
                data_bytes,
                content_type,
                owner_user_id,
                entity_type,
                entity_id=None,
            ):
                self.upload_calls.append(
                    {
                        "size": len(data_bytes),
                        "content_type": content_type,
                        "owner_user_id": owner_user_id,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                    }
                )
                return type("UploadResult", (), {"s3_key": "media/chat_voice/u1/fake.webm"})()

            def generate_presigned_get_url(self, s3_key, expires_in_seconds):
                self.presign_calls.append(
                    {"s3_key": s3_key, "expires_in_seconds": expires_in_seconds}
                )
                return "https://example.com/private/fake.webm"

        async def fake_transcribe(audio_bytes, filename, timeout_seconds=60):
            return "voice transcript from test"

        async def fake_generate_response(**kwargs):
            return {"success": True, "content": "assistant reply from test"}

        fake_storage = FakeStorage()
        monkeypatch.setattr(voice_router, "s3_storage_service", fake_storage)
        monkeypatch.setattr(voice_router, "transcribe_audio_assemblyai", fake_transcribe)
        monkeypatch.setattr(
            voice_router.chat_service, "generate_response", fake_generate_response
        )

        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        assert conv_response.status_code == status.HTTP_201_CREATED
        conv_id = conv_response.json()["id"]

        response = client.post(
            f"/api/chat/conversations/{conv_id}/voice",
            headers=auth_headers,
            params={"include_audio": "true"},
            files={"audio": ("note.webm", b"fake-audio-bytes", "audio/webm")},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["user_message"]["content"] == "voice transcript from test"
        assert data["user_message"]["s3_key"] == "media/chat_voice/u1/fake.webm"
        assert data["ai_response"]["content"] == "assistant reply from test"
        assert data["audio_url"] == "https://example.com/private/fake.webm"

        assert len(fake_storage.upload_calls) == 1
        assert fake_storage.upload_calls[0]["entity_type"] == "chat_voice"
        assert fake_storage.upload_calls[0]["entity_id"] == conv_id
        assert len(fake_storage.presign_calls) == 1
        assert (
            fake_storage.presign_calls[0]["expires_in_seconds"]
            == settings.S3_PRESIGNED_URL_TTL_SECONDS
        )

        messages_response = client.get(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers,
        )
        assert messages_response.status_code == status.HTTP_200_OK
        messages = messages_response.json()["messages"]
        assert len(messages) >= 2
        assert messages[0]["role"] == "user"
        assert messages[0]["s3_key"] == "media/chat_voice/u1/fake.webm"

    def test_voice_endpoint_continues_when_s3_upload_fails(
        self, client, auth_headers, monkeypatch
    ):
        from app.routers import voice as voice_router
        from app.services.s3_storage import S3StorageError

        class FailingStorage:
            def upload_media_bytes(self, *args, **kwargs):
                raise S3StorageError("simulated upload failure")

            def generate_presigned_get_url(self, s3_key, expires_in_seconds):
                return "https://example.com/unused"

        async def fake_transcribe(audio_bytes, filename, timeout_seconds=60):
            return "fallback transcript"

        async def fake_generate_response(**kwargs):
            return {"success": True, "content": "fallback assistant reply"}

        monkeypatch.setattr(voice_router, "s3_storage_service", FailingStorage())
        monkeypatch.setattr(voice_router, "transcribe_audio_assemblyai", fake_transcribe)
        monkeypatch.setattr(
            voice_router.chat_service, "generate_response", fake_generate_response
        )

        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        assert conv_response.status_code == status.HTTP_201_CREATED
        conv_id = conv_response.json()["id"]

        response = client.post(
            f"/api/chat/conversations/{conv_id}/voice",
            headers=auth_headers,
            params={"include_audio": "true"},
            files={"audio": ("note.webm", b"fake-audio-bytes", "audio/webm")},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["user_message"]["content"] == "fallback transcript"
        assert data["user_message"]["s3_key"] is None
        assert data["ai_response"]["content"] == "fallback assistant reply"
        assert data["audio_url"] is None

    def test_voice_endpoint_forbids_other_user_conversation_access(
        self, client, auth_headers, monkeypatch
    ):
        from app.routers import voice as voice_router

        class TrackingStorage:
            def __init__(self):
                self.upload_calls = 0

            def upload_media_bytes(self, *args, **kwargs):
                self.upload_calls += 1
                return type("UploadResult", (), {"s3_key": "media/chat_voice/u1/fake.webm"})()

            def generate_presigned_get_url(self, s3_key, expires_in_seconds):
                return "https://example.com/private/fake.webm"

        async def fake_transcribe(audio_bytes, filename, timeout_seconds=60):
            return "voice transcript from test"

        async def fake_generate_response(**kwargs):
            return {"success": True, "content": "assistant reply from test"}

        storage = TrackingStorage()
        monkeypatch.setattr(voice_router, "s3_storage_service", storage)
        monkeypatch.setattr(voice_router, "transcribe_audio_assemblyai", fake_transcribe)
        monkeypatch.setattr(
            voice_router.chat_service, "generate_response", fake_generate_response
        )

        # User A creates conversation
        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        assert conv_response.status_code == status.HTTP_201_CREATED
        conv_id = conv_response.json()["id"]

        # Register/login user B and try to upload to user A's conversation
        reg = client.post(
            "/api/auth/register",
            json={"email": "other@example.com", "password": "testpass123"},
        )
        assert reg.status_code == status.HTTP_201_CREATED
        login = client.post(
            "/api/auth/login-json",
            json={"email": "other@example.com", "password": "testpass123"},
        )
        assert login.status_code == status.HTTP_200_OK
        other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        forbidden = client.post(
            f"/api/chat/conversations/{conv_id}/voice",
            headers=other_headers,
            files={"audio": ("note.webm", b"fake-audio-bytes", "audio/webm")},
        )
        assert forbidden.status_code == status.HTTP_403_FORBIDDEN
        # Security behavior: reject before touching S3 upload path.
        assert storage.upload_calls == 0
