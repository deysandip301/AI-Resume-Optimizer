from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def mask_pii(text: str):
    """Mask PII in text using Presidio."""
    # 1. Identify PII (Names, Emails, Phones)
    entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]
    results = analyzer.analyze(text=text, entities=entities, language='en')

    # 2. Reversible Token Replacement
    # maps real data to synthetic tokens like <CANDIDATE_NAME>
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<CANDIDATE_NAME>"}),
        "EMAIL_ADDRESS": OperatorConfig(
            "replace", {"new_value": "<EMAIL_ADDRESS>"}
        ),
        "PHONE_NUMBER": OperatorConfig(
            "replace", {"new_value": "<PHONE_NUMBER>"}
        ),
    }

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )
    return anonymized_result.text
