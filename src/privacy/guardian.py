from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def mask_pii(text: str):
    # 1. Identify PII (Names, Emails, Phones) [cite: 73, 76]
    results = analyzer.analyze(text=text, entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"], language='en')
    
    # 2. Reversible Token Replacement [cite: 82, 85]
    # maps real data to synthetic tokens like <CANDIDATE_NAME>
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<CANDIDATE_NAME>"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_ADDRESS>"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE_NUMBER>"}),
    }
    
    anonymized_result = anonymizer.anonymize(
        text=text, 
        analyzer_results=results,
        operators=operators
    )
    return anonymized_result.text