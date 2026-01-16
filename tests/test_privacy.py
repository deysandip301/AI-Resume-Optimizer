import pytest
from src.privacy.guardian import mask_pii


def test_pii_masking_accuracy():
    """
    Test that the Privacy Shield successfully identifies and masks
    sensitive names and emails.
    """
    raw_text = (
        "Jane Doe is a software engineer at Google. "
        "Contact: jane.doe@example.com"
    )
    sanitized = mask_pii(raw_text)

    # Assertions to ensure privacy is maintained
    assert "Jane Doe" not in sanitized
    assert "jane.doe@example.com" not in sanitized
    assert "<CANDIDATE_NAME>" in sanitized
    assert "<EMAIL_ADDRESS>" in sanitized


def test_context_preservation():
    """
    Ensure that non-PII technical skills are NOT masked,
    maintaining semantic integrity for the LLM.
    """
    raw_text = "Expert in Python and AWS."
    sanitized = mask_pii(raw_text)

    assert "Python" in sanitized
    assert "AWS" in sanitized
