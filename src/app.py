"""ATS Keyword Matcher - Resume to Job Description analysis."""
import re
from typing import List, Set

import fitz  # PyMuPDF
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

app = FastAPI(
    title="ATS Keyword Matcher",
    description="Analyze resume-to-JD keyword alignment for ATS optimization",
    version="1.0.0",
)


class AnalysisResult(BaseModel):
    """Response model for resume analysis."""
    score: float
    score_label: str
    matched_keywords: List[str]
    missing_keywords: List[str]
    total_jd_keywords: int
    total_matched: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "up"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content from PDF bytes."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {e}")


def extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords from text.

    Filters out common stop words and short words.
    """
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who', 'whom',
        'their', 'our', 'your', 'my', 'his', 'her', 'all', 'each', 'every',
        'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
        'also', 'now', 'here', 'there', 'when', 'where', 'why', 'how', 'any',
        'if', 'then', 'because', 'while', 'although', 'though', 'after',
        'before', 'above', 'below', 'between', 'under', 'over', 'through',
        'during', 'about', 'into', 'out', 'up', 'down', 'off', 'again',
    }

    # Extract words (alphanumeric, min 2 chars)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

    # Filter stop words and return unique keywords
    return {word for word in words if word not in stop_words}


def calculate_ats_score(resume_keywords: Set[str], jd_keywords: Set[str]) -> dict:
    """Calculate ATS match score between resume and job description."""
    if not jd_keywords:
        return {
            "score": 0.0,
            "matched": set(),
            "missing": set(),
        }

    matched = resume_keywords.intersection(jd_keywords)
    missing = jd_keywords - resume_keywords
    score = (len(matched) / len(jd_keywords)) * 100

    return {
        "score": round(score, 2),
        "matched": matched,
        "missing": missing,
    }


def get_score_label(score: float) -> str:
    """Get human-readable label for ATS score."""
    if score >= 80:
        return "Excellent Match"
    elif score >= 60:
        return "Good Match"
    elif score >= 40:
        return "Fair Match"
    elif score >= 20:
        return "Needs Improvement"
    else:
        return "Poor Match"


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Job description text"),
) -> AnalysisResult:
    """
    Analyze resume against job description for ATS keyword matching.

    - Extracts text from uploaded PDF resume
    - Compares keywords against job description
    - Returns match score and missing keywords
    """
    # Validate file type
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Read and extract text from PDF
    try:
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF"
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    # Calculate ATS score
    result = calculate_ats_score(resume_keywords, jd_keywords)

    return AnalysisResult(
        score=result["score"],
        score_label=get_score_label(result["score"]),
        matched_keywords=sorted(list(result["matched"]))[:50],  # Top 50
        missing_keywords=sorted(list(result["missing"]))[:30],  # Top 30
        total_jd_keywords=len(jd_keywords),
        total_matched=len(result["matched"]),
    )


@app.post("/analyze/text", response_model=AnalysisResult)
async def analyze_text(
    resume_text: str = Form(..., description="Resume text content"),
    job_description: str = Form(..., description="Job description text"),
) -> AnalysisResult:
    """
    Analyze resume text against job description (no PDF upload).

    Useful for testing or when resume text is already extracted.
    """
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty"
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    # Calculate ATS score
    result = calculate_ats_score(resume_keywords, jd_keywords)

    return AnalysisResult(
        score=result["score"],
        score_label=get_score_label(result["score"]),
        matched_keywords=sorted(list(result["matched"]))[:50],
        missing_keywords=sorted(list(result["missing"]))[:30],
        total_jd_keywords=len(jd_keywords),
        total_matched=len(result["matched"]),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for container orchestration."""
    return HealthResponse()
