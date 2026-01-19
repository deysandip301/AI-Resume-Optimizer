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
    """Extract meaningful job-related keywords from text.

    Uses stop word filtering to remove common filler words.
    Keeps technical skills, tools, and job-relevant terms.
    """
    # Stop words - ONLY truly generic/filler words, NOT skills
    stop_words = {
        # Articles, pronouns, prepositions, conjunctions
        'a', 'an', 'the', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
        'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
        'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there',
        'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'just', 'can',
        'will', 'don', 'should', 'now', 'any', 'both', 'every',

        # Common verbs (non-skill)
        'get', 'got', 'getting', 'make', 'made', 'making', 'go', 'going',
        'went', 'gone', 'come', 'came', 'coming', 'take', 'took', 'taken',
        'see', 'saw', 'seen', 'know', 'knew', 'known', 'think', 'thought',
        'want', 'wanted', 'give', 'gave', 'given', 'tell', 'told',
        'ask', 'asked', 'seem', 'seemed', 'leave', 'left', 'put', 'keep',
        'kept', 'let', 'begin', 'began', 'show', 'showed', 'shown',
        'hear', 'heard', 'move', 'moved', 'like', 'liked', 'live', 'lived',
        'believe', 'believed', 'hold', 'held', 'bring', 'brought',
        'happen', 'happened', 'must', 'shall', 'would', 'could', 'might', 'may',

        # Common adjectives (non-differentiating)
        'good', 'great', 'best', 'better', 'new', 'first', 'last', 'long',
        'little', 'old', 'right', 'big', 'high', 'different', 'small', 'large',
        'next', 'early', 'young', 'important', 'public', 'bad', 'able', 'free',
        'sure', 'clear', 'full', 'special', 'easy', 'ready', 'possible', 'open',
        'late', 'hard', 'real', 'whole', 'least', 'short', 'certain', 'low',
        'likely', 'true', 'available', 'necessary', 'several', 'recent',
        'current', 'particular', 'fine', 'simple', 'strong', 'various',
        'additional', 'major', 'local', 'general', 'fast', 'paced', 'highly',
        'exceptional', 'brilliant', 'solid', 'appropriate', 'desirable',

        # Common nouns (non-skill)
        'time', 'year', 'years', 'people', 'way', 'day', 'days', 'man', 'men',
        'woman', 'women', 'child', 'children', 'world', 'life', 'hand', 'hands',
        'part', 'parts', 'place', 'places', 'case', 'cases', 'week', 'weeks',
        'point', 'points', 'thing', 'things', 'home', 'fact', 'facts', 'month',
        'months', 'lot', 'book', 'eye', 'eyes', 'job', 'word', 'words',
        'side', 'sides', 'kind', 'head', 'house', 'friend', 'friends', 'hour',
        'hours', 'line', 'lines', 'end', 'member', 'members', 'area', 'areas',
        'money', 'story', 'stories', 'state', 'city', 'name', 'family', 'room',
        'country', 'question', 'questions', 'idea', 'ideas', 'number', 'numbers',

        # Job posting filler
        'position', 'candidate', 'candidates', 'role', 'responsibilities',
        'requirements', 'qualifications', 'opportunity', 'opportunities',
        'looking', 'seeking', 'join', 'joining', 'offer', 'offers', 'offering',
        'apply', 'applying', 'resume', 'cover', 'letter', 'salary', 'benefits',
        'bonus', 'vacation', 'insurance', 'retirement', 'flexible', 'remote',
        'hybrid', 'onsite', 'office', 'location', 'located', 'based', 'working',
        'work', 'environment', 'culture', 'employer', 'employment', 'employee',
        'employees', 'staff', 'hire', 'hiring', 'hired', 'start', 'starting',
        'date', 'deadline', 'submit', 'submitted', 'please', 'thank', 'thanks',
        'note', 'notes', 'email', 'phone', 'contact', 'website', 'click', 'link',
        'info', 'information', 'details', 'description', 'overview', 'summary',
        'include', 'includes', 'including', 'require', 'requires', 'required',
        'prefer', 'prefers', 'preferred', 'plus', 'ideal', 'ideally',
        'minimum', 'maximum', 'need', 'needs', 'needed', 'expect', 'expected',

        # Office perks (NOT skills)
        'breakfast', 'lunch', 'dinner', 'snacks', 'food', 'meals', 'drinks',
        'coffee', 'tea', 'cafeteria', 'kitchen', 'kitchens', 'gym', 'fitness',
        'wellness', 'parking', 'commute', 'cab', 'cabs', 'transport', 'shuttle',
        'cubicle', 'cubicles', 'desk', 'desks', 'jeans', 'casual', 'dress',
        'attire', 'friday', 'fridays', 'rewards', 'perks', 'premium',
        'facility', 'facilities', 'amenities', 'lounge', 'recreation',
        'events', 'party', 'parties', 'celebration', 'outing', 'trip', 'trips',

        # Location words
        'india', 'usa', 'america', 'europe', 'asia', 'africa', 'australia',
        'canada', 'china', 'japan', 'germany', 'france', 'singapore', 'dubai',
        'london', 'paris', 'tokyo', 'sydney', 'mumbai', 'delhi', 'bangalore',
        'hyderabad', 'chennai', 'pune', 'kolkata', 'gurgaon', 'noida',
        'york', 'san', 'francisco', 'seattle', 'boston', 'chicago', 'austin',
        'denver', 'atlanta', 'miami', 'dallas', 'houston', 'phoenix',
        'street', 'wall', 'tower', 'towers', 'building', 'buildings', 'floor',
        'floors', 'campus', 'park', 'center', 'centre', 'plaza', 'avenue',
        'road', 'boulevard', 'lane', 'drive', 'llc', 'inc', 'corp', 'ltd', 'pvt',

        # Time/quantity
        'daily', 'weekly', 'monthly', 'annually', 'yearly', 'hourly',
        'per', 'percent', 'percentage', 'approximately', 'multiple',

        # Connecting words
        'also', 'well', 'however', 'therefore', 'thus', 'hence', 'although',
        'though', 'still', 'yet', 'already', 'even', 'ever', 'never', 'always',
        'often', 'sometimes', 'usually', 'generally', 'typically', 'especially',
        'specifically', 'particularly', 'mainly', 'mostly', 'primarily',
        'largely', 'simply', 'directly', 'currently', 'recently', 'alongside',

        # Education filler (but keep degree types)
        'ability', 'abilities', 'skill', 'skills', 'knowledge', 'proficiency',
        'proficient', 'familiar', 'familiarity', 'understanding', 'background',
        'equivalent', 'related', 'relevant', 'field', 'fields',

        # EEO/Legal words (NOT skills)
        'immigration', 'ethnicity', 'race', 'racial', 'gender', 'sex', 'sexual',
        'orientation', 'identity', 'marital', 'status', 'religion', 'religious',
        'ancestry', 'national', 'origin', 'nationality', 'citizenship', 'citizen',
        'veteran', 'veterans', 'military', 'disability', 'disabilities',
        'pregnancy', 'genetic', 'genetics', 'age', 'aged', 'protected',
        'discrimination', 'affiliation', 'political', 'ordinances', 'laws', 'law',
        'affirmative', 'action', 'eeo', 'eeoc', 'expression', 'creed', 'color',

        # Corporate values (NOT skills)
        'values', 'value', 'mission', 'vision', 'purpose', 'integrity',
        'honesty', 'respect', 'accountability', 'transparency', 'excellence',
        'passion', 'passionate', 'passions', 'excitement', 'excited', 'exciting',
        'thrive', 'thriving', 'empower', 'empowered', 'inspire', 'inspired',
        'innovative', 'innovate', 'creativity', 'creative', 'curiosity', 'curious',
        'mindset', 'attitude', 'positive', 'fun', 'enjoy', 'journey',
        'growth', 'grow', 'talent', 'talented', 'potential', 'aspirations',
        'achieve', 'achieving', 'succeed', 'success', 'successful', 'winning',
        'reward', 'rewarding', 'meaningful', 'impact', 'impactful', 'difference',
        'community', 'belong', 'belonging', 'together', 'shared', 'care', 'caring',
        'support', 'supporting', 'trust', 'everyone', 'everybody', 'anyone',
        'someone', 'person', 'persons', 'individual', 'individuals', 'human',

        # Internship/Program words (NOT skills)
        'internship', 'internships', 'intern', 'interns', 'program', 'programs',
        'semester', 'semesters', 'term', 'terms', 'rotation', 'rotational',
        'cohort', 'batch', 'completion', 'completing', 'complete', 'ongoing',
        'duration', 'period', 'temporary', 'permanent', 'apprentice', 'trainee',
        'mentee', 'mentor', 'mentoring', 'mentorship', 'guidance', 'guide',
        'coach', 'coaching', 'buddy',

        # Generic action verbs
        'provide', 'provides', 'providing', 'enable', 'enables', 'enabling',
        'allow', 'allows', 'allowing', 'help', 'helps', 'helping', 'assist',
        'assists', 'assisting', 'assistance', 'ensure', 'ensures', 'ensuring',
        'demonstrate', 'demonstrates', 'leverage', 'leverages', 'leveraging',
        'utilize', 'utilizes', 'utilizing', 'explore', 'explores', 'exploring',
        'pursue', 'pursues', 'pursuing', 'seek', 'seeks', 'seeking',
        'adopt', 'adopts', 'adopting', 'embrace', 'embraces', 'embracing',
        'receive', 'receives', 'receiving', 'accept', 'accepts', 'accepting',
        'consider', 'considers', 'considering', 'consideration', 'read', 'reads',
        'improve', 'improves', 'improving', 'advance', 'advances', 'advancing',
        'proactively', 'proactive', 'quickly', 'rapidly', 'efficiently',
        'effectively', 'collaborate', 'collaborates', 'collaborating',
        'cooperate', 'cooperates', 'cooperative', 'coordinate', 'coordinates',
        'learns', 'learn', 'learning', 'learned',

        # Generic nouns
        'customers', 'customer', 'clients', 'client', 'users', 'user',
        'products', 'product', 'services', 'service', 'solutions', 'solution',
        'projects', 'project', 'initiatives', 'initiative', 'efforts', 'effort',
        'goals', 'goal', 'objectives', 'objective', 'targets', 'target',
        'results', 'result', 'outcomes', 'outcome', 'deliverables', 'deliverable',
        'operations', 'operation', 'practices', 'practice', 'methods', 'method',
        'approaches', 'approach', 'strategies', 'strategy', 'plans', 'plan',
        'developments', 'development', 'resources', 'resource', 'materials',
        'documents', 'document', 'principles', 'principle', 'fundamentals',
        'concepts', 'concept', 'standards', 'standard', 'guidelines', 'guideline',
        'policies', 'policy', 'procedures', 'procedure', 'corner', 'corners',
        'planet', 'globe', 'worldwide', 'internal', 'external', 'chance',
        'ahead', 'forward', 'future', 'career', 'careers', 'path', 'paths',
        'teammates', 'teammate', 'colleagues', 'colleague', 'peers', 'peer',
        'managers', 'manager', 'supervisors', 'supervisor', 'directors',
        'executives', 'executive', 'leaders', 'applicants', 'applicant',
        'qualified', 'qualify', 'eligible', 'eligibility', 'availability',
        'accommodate', 'accommodation', 'accommodations', 'reasonable',
        'applicable', 'physical', 'mental', 'emotional', 'condition', 'conditions',
        'filled', 'fill', 'remaining', 'remain', 'due', 'regard', 'regards',
        'driving', 'driven', 'incorporates', 'incorporate', 'realize', 'realizes',
        'thousands', 'hundreds', 'millions', 'billions',

        # Company names only
        'microsoft', 'google', 'amazon', 'apple', 'meta', 'facebook', 'netflix',
        'uber', 'lyft', 'airbnb', 'salesforce', 'oracle', 'ibm', 'intel',
        'nvidia', 'amd', 'cisco', 'vmware', 'adobe', 'spotify',
    }

    # Extract words (min 2 chars to keep abbreviations like AI, ML)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

    # Filter stop words and return unique keywords
    keywords = {word for word in words if word not in stop_words}

    return keywords


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
    print(jd_keywords)
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
