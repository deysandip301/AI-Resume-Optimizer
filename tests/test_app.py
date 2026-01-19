"""Unit tests for ATS Keyword Matcher."""
from src.app import extract_keywords, calculate_ats_score, get_score_label


def test_extract_keywords_filters_stop_words():
    """Test that common stop words are filtered out."""
    text = "The quick brown fox jumps over the lazy dog"
    keywords = extract_keywords(text)

    assert "the" not in keywords
    assert "over" not in keywords
    assert "quick" in keywords
    assert "brown" in keywords
    assert "fox" in keywords


def test_extract_keywords_handles_empty_text():
    """Test extraction with empty text."""
    keywords = extract_keywords("")
    assert keywords == set()


def test_extract_keywords_case_insensitive():
    """Test that keyword extraction is case insensitive."""
    text = "Python PYTHON python"
    keywords = extract_keywords(text)

    assert "python" in keywords
    assert len(keywords) == 1


def test_calculate_ats_score_perfect_match():
    """Test ATS score calculation with perfect match."""
    resume = {"python", "java", "docker"}
    jd = {"python", "java", "docker"}

    result = calculate_ats_score(resume, jd)

    assert result["score"] == 100.0
    assert result["matched"] == {"python", "java", "docker"}
    assert result["missing"] == set()


def test_calculate_ats_score_partial_match():
    """Test ATS score calculation with partial match."""
    resume = {"python", "java"}
    jd = {"python", "java", "docker", "kubernetes"}

    result = calculate_ats_score(resume, jd)

    assert result["score"] == 50.0
    assert result["matched"] == {"python", "java"}
    assert result["missing"] == {"docker", "kubernetes"}


def test_calculate_ats_score_no_match():
    """Test ATS score calculation with no match."""
    resume = {"python", "java"}
    jd = {"rust", "golang"}

    result = calculate_ats_score(resume, jd)

    assert result["score"] == 0.0
    assert result["matched"] == set()
    assert result["missing"] == {"rust", "golang"}


def test_calculate_ats_score_empty_jd():
    """Test ATS score with empty job description."""
    resume = {"python", "java"}
    jd = set()

    result = calculate_ats_score(resume, jd)

    assert result["score"] == 0.0


def test_get_score_label_excellent():
    """Test score label for excellent match."""
    assert get_score_label(85.0) == "Excellent Match"
    assert get_score_label(100.0) == "Excellent Match"


def test_get_score_label_good():
    """Test score label for good match."""
    assert get_score_label(65.0) == "Good Match"
    assert get_score_label(79.0) == "Good Match"


def test_get_score_label_fair():
    """Test score label for fair match."""
    assert get_score_label(45.0) == "Fair Match"


def test_get_score_label_needs_improvement():
    """Test score label for needs improvement."""
    assert get_score_label(25.0) == "Needs Improvement"


def test_get_score_label_poor():
    """Test score label for poor match."""
    assert get_score_label(10.0) == "Poor Match"
    assert get_score_label(0.0) == "Poor Match"


def test_real_resume_jd_scenario():
    """Test with realistic resume and JD content."""
    resume_text = """
    Senior Software Engineer with 5 years experience in Python and Java.
    Experienced with Docker, Kubernetes, and AWS cloud services.
    Strong background in microservices architecture and CI/CD pipelines.
    """

    jd_text = """
    Looking for a Software Engineer with Python and Java skills.
    Must have experience with Docker and Kubernetes.
    AWS experience preferred. Knowledge of microservices required.
    Experience with CI/CD and DevOps practices.
    """

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    result = calculate_ats_score(resume_keywords, jd_keywords)

    # Should have good match
    assert result["score"] >= 50.0
    assert "python" in result["matched"]
    assert "docker" in result["matched"]
    assert "kubernetes" in result["matched"]
