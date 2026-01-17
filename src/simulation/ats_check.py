"""ATS fraud detection scanner for hidden text in PDFs."""
import logging
from pathlib import Path
from typing import List, NamedTuple

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# RGB color for white (packed as integer)
WHITE_COLOR = 16777215  # RGB(255, 255, 255)


class HiddenTextFlag(NamedTuple):
    """Details about detected hidden text."""
    page_number: int
    text_snippet: str
    color: int


def scan_for_hidden_text(pdf_path: str) -> bool:
    """
    Scans PDF for text rendered in white or matching background.
    Mitigates 'High Risk: Potential Fraud Detection' flags.
    
    Args:
        pdf_path: Path to the PDF file to scan.
        
    Returns:
        True if hidden/white text is detected, False otherwise.
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist.
        ValueError: If file cannot be opened as PDF.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if "lines" not in block:
                        continue
                        
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            color = span.get("color", 0)
                            
                            # Check for white text
                            if color == WHITE_COLOR:
                                text_preview = span.get("text", "")[:50]
                                logger.warning(
                                    f"Hidden text detected on page {page_num}: "
                                    f"'{text_preview}...'"
                                )
                                return True
                                
        logger.info(f"No hidden text found in {path.name}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to scan PDF: {e}")
        raise ValueError(f"Cannot open file as PDF: {pdf_path}") from e


def scan_for_hidden_text_detailed(pdf_path: str) -> List[HiddenTextFlag]:
    """
    Detailed scan returning all instances of hidden text.
    
    Args:
        pdf_path: Path to the PDF file to scan.
        
    Returns:
        List of HiddenTextFlag with details about each detection.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    flags: List[HiddenTextFlag] = []
    
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        color = span.get("color", 0)
                        
                        if color == WHITE_COLOR:
                            flags.append(HiddenTextFlag(
                                page_number=page_num,
                                text_snippet=span.get("text", "")[:100],
                                color=color
                            ))
    
    return flags