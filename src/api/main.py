import hashlib

from fastapi import FastAPI, HTTPException

from src.privacy.guardian import mask_pii

app = FastAPI(title="Sovereign Recruitment Intelligence API")


@app.post("/optimize/sanitize")
async def sanitize_input(resume_text: str):
    """
    Ingest raw resume text and apply the Privacy Shield.

    This is the first step before any AI inference occurs.
    """
    try:
        # 1. Ingestion & Hashing for session tracking
        session_id = hashlib.sha256(resume_text.encode()).hexdigest()

        # 2. Sanitization through the PII Guardian
        sanitized_text = mask_pii(resume_text)

        return {
            "session_id": session_id,
            "sanitized_content": sanitized_text,
            "status": "PII_MASKED_SUCCESSFULLY"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Mandatory for container smoke testing/runtime validation."""
    return {"status": "healthy"}
