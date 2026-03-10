"""
Unit tests for S3 media storage service (A3.3).

All tests use mocked clients and never call real AWS services.
"""

import re

import pytest

from app.services.s3_storage import S3StorageError, S3StorageService, UploadResult


class FakeS3Client:
    def __init__(self):
        self.put_calls = []
        self.presign_calls = []
        self.raise_on_put = None
        self.raise_on_presign = None

    def put_object(self, **kwargs):
        if self.raise_on_put:
            raise self.raise_on_put
        self.put_calls.append(kwargs)
        return {"ETag": "fake-etag"}

    def generate_presigned_url(self, operation, Params, ExpiresIn):
        if self.raise_on_presign:
            raise self.raise_on_presign
        self.presign_calls.append(
            {
                "operation": operation,
                "params": Params,
                "expires_in": ExpiresIn,
            }
        )
        return "https://example.com/presigned-url"


def test_build_media_key_has_expected_structure_and_no_raw_pii():
    service = S3StorageService(
        bucket="meghan-media",
        region_name="us-east-1",
        prefix="media",
        client=FakeS3Client(),
    )

    key = service.build_media_key(
        owner_user_id=42,
        entity_type="chat_voice",
        content_type="audio/webm",
        entity_id=99,
    )

    # Expected pattern:
    # media/chat_voice/YYYY/MM/DD/u42/e99/<uuid>.webm
    assert re.match(
        r"^media/chat_voice/\d{4}/\d{2}/\d{2}/u42/e99/[0-9a-f]{32}\.webm$",
        key,
    )
    assert "@" not in key
    assert " " not in key


def test_upload_media_bytes_calls_put_object_with_expected_args():
    client = FakeS3Client()
    service = S3StorageService(bucket="meghan-media", client=client, prefix="media")

    result = service.upload_media_bytes(
        data_bytes=b"fake-audio-bytes",
        content_type="audio/mp3",
        owner_user_id=7,
        entity_type="chat_voice",
        entity_id=123,
    )

    assert isinstance(result, UploadResult)
    assert result.bucket == "meghan-media"
    assert len(client.put_calls) == 1

    call = client.put_calls[0]
    assert call["Bucket"] == "meghan-media"
    assert call["Body"] == b"fake-audio-bytes"
    assert call["ContentType"] == "audio/mp3"
    assert call["ServerSideEncryption"] == "AES256"
    assert re.match(
        r"^media/chat_voice/\d{4}/\d{2}/\d{2}/u7/e123/[0-9a-f]{32}\.mp3$",
        call["Key"],
    )


def test_generate_presigned_get_url_uses_bucket_key_and_ttl():
    client = FakeS3Client()
    service = S3StorageService(bucket="meghan-media", client=client)

    url = service.generate_presigned_get_url(
        s3_key="media/chat_voice/2026/03/05/u7/e123/file.webm",
        expires_in_seconds=1200,
    )

    assert url == "https://example.com/presigned-url"
    assert len(client.presign_calls) == 1
    call = client.presign_calls[0]
    assert call["operation"] == "get_object"
    assert call["params"] == {
        "Bucket": "meghan-media",
        "Key": "media/chat_voice/2026/03/05/u7/e123/file.webm",
    }
    assert call["expires_in"] == 1200


def test_upload_media_bytes_maps_client_error_to_domain_error():
    client = FakeS3Client()
    client.raise_on_put = RuntimeError("s3 down")
    service = S3StorageService(bucket="meghan-media", client=client)

    with pytest.raises(S3StorageError, match="Failed to upload media to S3"):
        service.upload_media_bytes(
            data_bytes=b"payload",
            content_type="audio/wav",
            owner_user_id=1,
            entity_type="chat_voice",
        )


def test_generate_presigned_get_url_maps_client_error_to_domain_error():
    client = FakeS3Client()
    client.raise_on_presign = RuntimeError("signing failed")
    service = S3StorageService(bucket="meghan-media", client=client)

    with pytest.raises(S3StorageError, match="Failed to generate presigned media URL"):
        service.generate_presigned_get_url(
            s3_key="media/chat_voice/2026/03/05/u1/file.wav",
            expires_in_seconds=300,
        )

