"""Resume optimization using local LLM and semantic embeddings."""
import logging
from typing import List, Optional

import ollama
from ollama import ResponseError
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class ResumeOptimizer:
    """Optimizes resume content using semantic analysis and local LLM."""

    DEFAULT_MODEL = "llama3:8b"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the optimizer with embedding and LLM models.

        Args:
            model_name: Ollama model name. Defaults to llama3:8b.
        """
        self.embedder = SentenceTransformer(self.EMBEDDING_MODEL)
        self.model_name = model_name or self.DEFAULT_MODEL
        logger.info(f"Initialized ResumeOptimizer with model: {self.model_name}")

    def analyze_skill_gap(self, resume_text: str, jd_text: str) -> float:
        """Identifies missing semantic concepts between resume and JD.

        Args:
            resume_text: The candidate's resume text.
            jd_text: The job description text.

        Returns:
            Cosine similarity score (0-1). Lower = larger skill gap.
        """
        if not resume_text.strip() or not jd_text.strip():
            raise ValueError("Resume and job description text cannot be empty")

        resume_emb = self.embedder.encode(resume_text, convert_to_tensor=True)
        jd_emb = self.embedder.encode(jd_text, convert_to_tensor=True)

        similarity = util.cos_sim(resume_emb, jd_emb)
        return float(similarity.item())

    def optimize_bullet_point(
        self,
        bullet: str,
        jd_context: str,
        keywords: List[str]
    ) -> str:
        """Rewrite a bullet point using local LLM to align with job description.

        Args:
            bullet: Original bullet point text.
            jd_context: Relevant job description context.
            keywords: Target keywords to incorporate.

        Returns:
            Optimized bullet point text.

        Raises:
            ConnectionError: If Ollama service is unavailable.
            RuntimeError: If LLM inference fails.
        """
        if not bullet.strip():
            raise ValueError("Bullet point cannot be empty")

        keywords_str = ", ".join(keywords) if keywords else "None specified"

        prompt = f"""Role: Expert Executive Resume Writer
Task: Rewrite the following bullet point to better align with the job description.
Target Keywords: {keywords_str}
Job Context: {jd_context}
Original Bullet: {bullet}

Instructions:
- Maintain factual accuracy - do not fabricate metrics or achievements
- Focus on quantifiable impact and measurable outcomes
- Incorporate target keywords naturally where appropriate
- Use strong action verbs
- Keep the bullet concise (one to two lines)

Rewritten Bullet:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7}
            )
            return response['message']['content'].strip()
        except ResponseError as e:
            logger.error(f"Ollama model error: {e}")
            raise RuntimeError(f"LLM inference failed: {e}") from e
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise ConnectionError(
                "Ollama service unavailable. Ensure Ollama is running."
            ) from e
