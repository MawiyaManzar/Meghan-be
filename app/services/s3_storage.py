"""
S3 storage helpers for private media objects (voice notes, etc.).

This module intentionally keeps a narrow surface:
- Build a safe object key (without direct PII in the path).
- Upload bytes to S3 with server-side encryption.
- Generate short-lived pre-signed GET URLs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import uuid
from typing import Any, Optional


logger = logging.getLogger(__name__)


class S3StorageError(Exception):
    """Raised for domain-level S3 storage failures."""


@dataclass(frozen=True)
class UploadResult:
    """Result payload returned after a successful S3 upload."""

    s3_key: str
    bucket: str


class S3StorageService:
    """Small wrapper over boto3 S3 client for media upload and URL signing."""

    def __init__(
        self,
        bucket: str,
        region_name: str = "us-east-1",
        prefix: str = "media",
        client: Any | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("bucket is required")

        cleaned_prefix = prefix.strip("/")
        self.bucket = bucket
        self.region_name = region_name
        self.prefix = cleaned_prefix
        self.client = client or self._build_default_client()

    def _build_default_client(self) -> Any:
        # Lazy import keeps test/import overhead small and allows easy mocking.
        import boto3

        return boto3.client("s3", region_name=self.region_name)

    def build_media_key(
        self,
        owner_user_id: int,
        entity_type: str,
        content_type: str,
        entity_id: Optional[int] = None,
    ) -> str:
        """
        Build a collision-resistant object key with no direct user PII.

        Example:
        media/chat_voice/2026/03/05/u42/e99/8a9d9f6e0e4d4e7b8a7d8a4b4f9b6e10.webm
        """
        if owner_user_id <= 0:
            raise ValueError("owner_user_id must be a positive integer")
        if not entity_type:
            raise ValueError("entity_type is required")
        if not content_type:
            raise ValueError("content_type is required")

        ext = self._extension_for_content_type(content_type)
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        random_suffix = uuid.uuid4().hex

        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.extend(
            [
                entity_type.strip().lower(),
                date_prefix,
                f"u{owner_user_id}",
            ]
        )
        if entity_id is not None:
            parts.append(f"e{entity_id}")
        parts.append(f"{random_suffix}.{ext}")
        return "/".join(parts)

    def upload_media_bytes(
        self,
        data_bytes: bytes,
        content_type: str,
        owner_user_id: int,
        entity_type: str,
        entity_id: Optional[int] = None,
    ) -> UploadResult:
        """
        Upload binary media to private S3 storage and return object location.
        """
        if not data_bytes:
            raise ValueError("data_bytes cannot be empty")
        if not content_type:
            raise ValueError("content_type is required")

        s3_key = self.build_media_key(
            owner_user_id=owner_user_id,
            entity_type=entity_type,
            content_type=content_type,
            entity_id=entity_id,
        )

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=data_bytes,
                ContentType=content_type,
                ServerSideEncryption="AES256",
            )
            logger.info(
                "S3 upload complete bucket=%s key=%s size=%d content_type=%s",
                self.bucket,
                s3_key,
                len(data_bytes),
                content_type,
            )
            return UploadResult(s3_key=s3_key, bucket=self.bucket)
        except Exception as exc:
            logger.error(
                "S3 upload failed bucket=%s key=%s error=%s",
                self.bucket,
                s3_key,
                str(exc),
                exc_info=True,
            )
            raise S3StorageError("Failed to upload media to S3") from exc

    def generate_presigned_get_url(
        self,
        s3_key: str,
        expires_in_seconds: int = 900,
    ) -> str:
        """
        Generate a temporary signed URL to read a private S3 object.
        """
        if not s3_key:
            raise ValueError("s3_key is required")
        if expires_in_seconds <= 0:
            raise ValueError("expires_in_seconds must be positive")

        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expires_in_seconds,
            )
        except Exception as exc:
            logger.error(
                "Failed to generate presigned URL bucket=%s key=%s error=%s",
                self.bucket,
                s3_key,
                str(exc),
                exc_info=True,
            )
            raise S3StorageError("Failed to generate presigned media URL") from exc

    def _extension_for_content_type(self, content_type: str) -> str:
        mapping = {
            "audio/webm": "webm",
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/wav": "wav",
            "audio/x-wav": "wav",
            "audio/mp4": "m4a",
            "audio/x-m4a": "m4a",
            "audio/ogg": "ogg",
        }
        return mapping.get(content_type.lower(), "bin")

