"""Privacy Guardian for PII detection and anonymization."""
import logging
from typing import Dict, List

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)

# Initialize engines (singleton pattern for performance)
_analyzer: AnalyzerEngine = None
_anonymizer: AnonymizerEngine = None


def _get_engines() -> tuple[AnalyzerEngine, AnonymizerEngine]:
    """Get or create Presidio engines (lazy initialization)."""
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
        logger.info("Initialized Presidio engines")
    return _analyzer, _anonymizer


# Supported PII entity types
SUPPORTED_ENTITIES: List[str] = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]

# Token mapping for reversible anonymization
OPERATOR_CONFIG: Dict[str, OperatorConfig] = {
    "PERSON": OperatorConfig("replace", {"new_value": "<CANDIDATE_NAME>"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_ADDRESS>"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE_NUMBER>"}),
}


def mask_pii(text: str, language: str = "en") -> str:
    """Mask PII in text using Microsoft Presidio.

    Args:
        text: Input text containing potential PII.
        language: Language code for NER (default: 'en').

    Returns:
        Anonymized text with PII replaced by tokens.

    Raises:
        ValueError: If text is empty or None.
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")

    analyzer, anonymizer = _get_engines()

    # 1. Identify PII (Names, Emails, Phones)
    results = analyzer.analyze(
        text=text,
        entities=SUPPORTED_ENTITIES,
        language=language
    )

    if results:
        logger.debug(f"Detected {len(results)} PII entities")

    # 2. Reversible Token Replacement
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=OPERATOR_CONFIG
    )

    return anonymized_result.text
