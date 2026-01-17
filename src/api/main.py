"""Sovereign Recruitment Intelligence API."""
import hashlib
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.privacy.guardian import mask_pii

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sovereign Recruitment Intelligence API",
    description="Privacy-first resume optimization with local AI processing",
    version="1.0.0",
)


class SanitizeRequest(BaseModel):
    """Request model for resume sanitization."""
    resume_text: str = Field(
        ...,
        min_length=10,
        description="Raw resume text to sanitize"
    )


class SanitizeResponse(BaseModel):
    """Response model for sanitized resume."""
    session_id: str = Field(..., description="SHA-256 hash for session tracking")
    sanitized_content: str = Field(..., description="PII-masked resume text")
    status: Literal["PII_MASKED_SUCCESSFULLY"] = "PII_MASKED_SUCCESSFULLY"


class HealthResponse(BaseModel):
    """Health check response model."""
    status: Literal["healthy"] = "healthy"


@app.post(
    "/optimize/sanitize",
    response_model=SanitizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Sanitize Resume PII",
)
async def sanitize_input(request: SanitizeRequest) -> SanitizeResponse:
    """
    Ingest raw resume text and apply the Privacy Shield.

    This is the first step before any AI inference occurs.
    All PII (names, emails, phone numbers) is masked with tokens.
    """
    try:
        # 1. Ingestion & Hashing for session tracking
        session_id = hashlib.sha256(
            request.resume_text.encode()
        ).hexdigest()

        # 2. Sanitization through the PII Guardian
        sanitized_text = mask_pii(request.resume_text)

        logger.info(f"Successfully sanitized resume, session: {session_id[:8]}...")

        return SanitizeResponse(
            session_id=session_id,
            sanitized_content=sanitized_text,
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Sanitization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during sanitization"
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
)
async def health_check() -> HealthResponse:
    """Health check endpoint for container orchestration and monitoring."""
    return HealthResponse()
