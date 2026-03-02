import asyncio
from typing import Optional

import httpx

from app.core.config import settings

class STTServiceError(Exception):
    """Base error for STT service failures."""

class STTTimeoutError(STTServiceError):
    """Raised when transcription does not complete within the timeout."""

async def _assemblyai_upload_audio(
    client:httpx.AsyncClient,
    audio_bytes:bytes
    )->str:
    """
    Upload raw audio bytes to AssemblyAI and return the upload_url.
    """
    headers= {
        "authorization":settings.ASSEMBLYAI_API_KEY or "",

    }

    resp = await client.post(
        settings.ASSEMBLYAI_UPLOAD_URL,
        headers=headers,
        content=audio_bytes,
        timeout=30.0
    )

    try:
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise STTServiceError(f"AssemblyAI upload failed: {e}") from e

    data = resp.json()

    upload_url= data.get("upload_url")
    if not upload_url:
        raise STTServiceError(
            f"AssemblyAI upload response missing 'upload_url': {data}"
        )
    return upload_url

async def _assemblyai_create_transcript(
    client: httpx.AsyncClient,
    audio_url: str,
    language_code: Optional[str] = None,
) -> str:
    """
    Create a transcript job in AssemblyAI and return the transcript id.
    """
    headers = {
        # HTTP headers are case-insensitive, but mirror AssemblyAI docs for clarity
        "Authorization": settings.ASSEMBLYAI_API_KEY or "",
        "Content-Type": "application/json",
    }

    # Minimal, documented-safe body:
    # - audio_url from the upload step
    # - speech_models: required by AssemblyAI (must be one of the allowed models)
    # - language_code: default to US English if not provided
    body: dict = {
        "audio_url": audio_url,
        "speech_models": ["universal-2"],
        "language_code": language_code or "en_us",
    }

    resp = await client.post(
        settings.ASSEMBLYAI_TRANSCRIPT_URL,
        headers=headers,
        json=body,
        timeout=30.0,
    )

    if resp.status_code >= 400:
        # Surface full error body to logs / caller to make debugging easier
        detail = resp.text
        raise STTServiceError(
            f"AssemblyAI transcript create failed "
            f"({resp.status_code}): {detail}"
        )

    data = resp.json()
    transcript_id = data.get("id")
    if not transcript_id:
        raise STTServiceError(
            f"AssemblyAI transcript response missing 'id': {data}"
        )
    return transcript_id

async def _assemblyai_poll_transcript(
    client:httpx.AsyncClient,
    transcript_id:str,
    timeout_seconds:int=60,
    poll_interval_seconds:float=1.5
)->str:
    """
    Poll AssemblyAI for transcript completion and return the final text.
    """
    headers = {
        "authorization": settings.ASSEMBLYAI_API_KEY or "",
    }

    url = f"{settings.ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}"

    deadline = asyncio.get_event_loop().time() + timeout_seconds

    while True:
        if asyncio.get_event_loop().time() >deadline:
            raise STTTimeoutError(
                f"AssemblyAI transcription timed out after {timeout_seconds} seconds"
            )
        resp = await client.get(url,headers=headers,timeout=30.0)
        
        try:
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise STTServiceError(f"AssemblyAI transcript poll failed: {e}") from e

        data = resp.json()
        status = data.get("status")
        if status == "completed":
            text = data.get("text", "")
            if not text:
                raise STTServiceError(
                    f"AssemblyAI returned completed status but empty text: {data}"
                )
            return text

        if status == "error":
            error_message = data.get("error", "Unknown AssemblyAI error")
            raise STTServiceError(
                f"AssemblyAI transcription error: {error_message}"
            )

        # Still processing (status could be 'queued', 'processing', etc.)
        await asyncio.sleep(poll_interval_seconds)

async def transcribe_audio_assemblyai(
    audio_bytes:bytes,
    filename:str,
    timeout_seconds:int=60,
    language_code:Optional[str]=None
)->str:
    """
    High-level helper to transcribe audio using AssemblyAI.

    - Uploads the audio bytes.
    - Creates a transcript job.
    - Polls until completion or timeout.

    Returns:
        The final transcript text.

    Raises:
        STTServiceError on API / logical failures.
        STTTimeoutError if it does not complete within timeout_seconds.
    """

    if not settings.ASSEMBLYAI_API_KEY:
        raise STTServiceError(
            "ASSEMBLYAI_API_KEY is not configured. "
            "Set it in your .env and app.core.config.Settings."
        )
    async with httpx.AsyncClient() as client:
        upload_url= await _assemblyai_upload_audio(client,audio_bytes)
        transcript_id= await _assemblyai_create_transcript(client, upload_url, language_code=language_code
        )
        transcript = await _assemblyai_poll_transcript(
            client,
            transcript_id,
            timeout_seconds=timeout_seconds,
        )
        return transcript

