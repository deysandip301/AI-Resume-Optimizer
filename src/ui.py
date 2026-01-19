import streamlit as st
import requests
import fitz  # PyMuPDF

# Page config
st.set_page_config(
    page_title="ATS Keyword Matcher",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .score-box {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .score-excellent { background-color: #d4edda; border: 2px solid #28a745; }
    .score-good { background-color: #fff3cd; border: 2px solid #ffc107; }
    .score-poor { background-color: #f8d7da; border: 2px solid #dc3545; }
    .keyword-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .matched { background-color: #d4edda; color: #155724; }
    .missing { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>📝 ATS Keyword Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Check how well your resume matches the job description</p>", unsafe_allow_html=True)

st.divider()

# API URL - uses localhost since both run in same container
API_URL = "http://localhost:8000"

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file."""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_keywords_from_jd(jd_text: str) -> list:
    """Extract keywords from JD (simple word extraction)."""
    # Common tech keywords to look for
    common_keywords = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node", "nodejs", "express", "django", "flask", "fastapi", "spring",
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "git", "github", "gitlab", "ci/cd", "jenkins", "devops", "agile",
        "rest", "api", "microservices", "linux", "bash", "shell",
        "machine learning", "ml", "ai", "data science", "pandas", "numpy",
        "html", "css", "tailwind", "bootstrap", "figma", "ui/ux"
    ]
    
    jd_lower = jd_text.lower()
    found_keywords = []
    for keyword in common_keywords:
        if keyword in jd_lower:
            found_keywords.append(keyword)
    
    return found_keywords if found_keywords else jd_text.replace(",", " ").split()[:20]

# Resume Upload Section
st.subheader("📄 Upload Your Resume")
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume")

st.divider()

# JD Input Section
st.subheader("📋 Job Description")
jd_input_method = st.radio(
    "How would you like to provide the Job Description?",
    ["Paste Text", "Upload File"],
    horizontal=True
)

jd_text = ""
if jd_input_method == "Paste Text":
    jd_text = st.text_area(
        "Paste the Job Description here:",
        height=200,
        placeholder="Paste the full job description or key requirements here..."
    )
else:
    jd_file = st.file_uploader("Upload JD (PDF or TXT)", type=["pdf", "txt"], key="jd")
    if jd_file:
        if jd_file.type == "application/pdf":
            jd_text = extract_text_from_pdf(jd_file)
        else:
            jd_text = jd_file.read().decode("utf-8")
        st.success(f"JD loaded: {len(jd_text)} characters")

st.divider()

# Analyze Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyze Match Score", type="primary", use_container_width=True)

# Analysis Logic
if analyze_button:
    if not resume_file:
        st.error("⚠️ Please upload your resume (PDF)")
    elif not jd_text.strip():
        st.error("⚠️ Please provide a job description")
    else:
        with st.spinner("Analyzing your resume..."):
            try:
                # Extract resume text
                resume_file.seek(0)  # Reset file pointer
                resume_text = extract_text_from_pdf(resume_file)
                
                # Extract keywords from JD
                keywords = extract_keywords_from_jd(jd_text)
                
                # Call backend API
                response = requests.post(
                    f"{API_URL}/analyze/text",
                    json={
                        "text": resume_text,
                        "keywords": keywords
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    score = data.get("score", 0)
                    matched = data.get("matched_keywords", [])
                    missing = data.get("missing_keywords", [])
                    label = data.get("score_label", "")
                    
                    # Display Score
                    st.divider()
                    st.subheader("📊 Results")
                    
                    # Score with color coding
                    if score >= 75:
                        score_class = "score-excellent"
                        emoji = "🎉"
                    elif score >= 50:
                        score_class = "score-good"
                        emoji = "👍"
                    else:
                        score_class = "score-poor"
                        emoji = "📈"
                    
                    st.markdown(f"""
                    <div class="score-box {score_class}">
                        <h1>{emoji} {score}%</h1>
                        <h3>{label}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Keywords breakdown
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### ✅ Matched Keywords")
                        if matched:
                            for kw in matched:
                                st.markdown(f"<span class='keyword-tag matched'>✓ {kw}</span>", unsafe_allow_html=True)
                        else:
                            st.write("No keywords matched")
                    
                    with col2:
                        st.markdown("### ❌ Missing Keywords")
                        if missing:
                            for kw in missing:
                                st.markdown(f"<span class='keyword-tag missing'>✗ {kw}</span>", unsafe_allow_html=True)
                        else:
                            st.write("All keywords matched! 🎉")
                    
                    # Recommendations
                    if missing:
                        st.divider()
                        st.subheader("💡 Recommendations")
                        st.info(f"Consider adding these keywords to your resume: **{', '.join(missing[:5])}**")
                
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to API at {API_URL}. Make sure the backend is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
<p style='text-align: center; color: gray; font-size: 0.8rem;'>
    ATS Keyword Matcher - Built with FastAPI & Streamlit<br>
    <a href='/docs' target='_blank'>API Documentation</a>
</p>
""", unsafe_allow_html=True)
