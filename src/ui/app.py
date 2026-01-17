"""Streamlit UI for Sovereign Recruitment Intelligence."""
import sys
import tempfile
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import fitz  # PyMuPDF
import streamlit as st

from src.privacy.guardian import mask_pii
from src.simulation.gaze import generate_saliency_heatmap

st.set_page_config(
    page_title="Sovereign Recruitment Intelligence",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Sovereign Recruitment Intelligence")
st.markdown("*Privacy-first resume optimization with local AI processing*")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content from PDF bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def save_pdf_as_image(pdf_bytes: bytes) -> str:
    """Convert first page of PDF to image for visual analysis."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    # Render at 2x resolution for better quality
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    
    # Create temp file path without holding the file open (Windows compatibility)
    tmp_dir = tempfile.gettempdir()
    tmp_path = Path(tmp_dir) / f"resume_preview_{id(pdf_bytes)}.png"
    
    pix.save(str(tmp_path))
    doc.close()
    return str(tmp_path)


if uploaded_file:
    pdf_bytes = uploaded_file.read()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Privacy First - Sanitize before any other action
        st.subheader("🔒 Privacy Shield")
        with st.spinner("Applying Privacy Shield..."):
            extracted_raw_text = extract_text_from_pdf(pdf_bytes)
            
            if not extracted_raw_text.strip():
                st.error("Could not extract text from PDF. Please try a different file.")
            else:
                sanitized_text = mask_pii(extracted_raw_text)
                st.success("Privacy Shield Active: PII Anonymized.")
                
                with st.expander("View Sanitized Content"):
                    st.text_area("Anonymized Resume", sanitized_text, height=300)
    
    with col2:
        # 2. Visual Analytics
        st.subheader("👁️ Recruiter Eye-Tracking Simulation")
        with st.spinner("Generating attention heatmap..."):
            temp_image_path = save_pdf_as_image(pdf_bytes)
            heatmap = generate_saliency_heatmap(temp_image_path)
            
            if heatmap is not None:
                st.image(
                    heatmap, 
                    caption="Heatmap: Red areas indicate high recruiter focus.",
                    channels="BGR"
                )
                # Cleanup temp file
                Path(temp_image_path).unlink(missing_ok=True)
            else:
                st.error("Failed to generate heatmap.")