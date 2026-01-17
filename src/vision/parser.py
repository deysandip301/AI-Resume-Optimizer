"""Visual document parsing with layout detection and OCR."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

import cv2
import layoutparser as lp
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


class ExtractedSection(TypedDict):
    """Represents an extracted text section from a document."""
    type: str
    text: str
    confidence: Optional[float]


class VisualParser:
    """Parses visual documents using layout detection and OCR."""
    
    LABEL_MAP = {
        0: "Caption", 1: "Footnote", 2: "Formula", 3: "List-item",
        4: "Page-footer", 5: "Page-header", 6: "Picture",
        7: "Section-header", 8: "Table", 9: "Text", 10: "Title"
    }
    TEXT_BLOCK_TYPES = {"Text", "Title", "List-item", "Section-header"}
    
    def __init__(self, lang: str = 'en'):
        """Initialize the parser with layout detection and OCR models.
        
        Args:
            lang: Language code for OCR (default: 'en').
        """
        self.model = lp.Detectron2LayoutModel(
            'lp://DocLayNet/faster_rcnn_R_50_FPN_3x/config',
            label_map=self.LABEL_MAP
        )
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        logger.info(f"Initialized VisualParser with language: {lang}")

    def process_pdf_page(self, image_path: str) -> List[ExtractedSection]:
        """Detects layout and extracts text block-by-block.
        
        Args:
            image_path: Path to the image file to process.
            
        Returns:
            List of extracted sections with type, text, and confidence.
            
        Raises:
            FileNotFoundError: If image file doesn't exist.
            ValueError: If image cannot be read.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
            
        layout = self.model.detect(image)
        
        # Manhattan Sort: Sort blocks Top-to-Bottom, then Left-to-Right
        layout.sort(
            key=lambda b: (b.coordinates[1], b.coordinates[0]), 
            inplace=True
        )
        
        extracted_sections: List[ExtractedSection] = []
        for block in layout:
            if block.type in self.TEXT_BLOCK_TYPES:
                section = self._extract_block_text(block, image)
                if section:
                    extracted_sections.append(section)
        
        logger.info(f"Extracted {len(extracted_sections)} sections from {path.name}")
        return extracted_sections
    
    def _extract_block_text(
        self, 
        block, 
        image: np.ndarray
    ) -> Optional[ExtractedSection]:
        """Extract text from a single layout block.
        
        Args:
            block: Layout block with coordinates.
            image: Source image array.
            
        Returns:
            ExtractedSection or None if extraction fails.
        """
        try:
            # Add padding to avoid cutting off text
            segment = block.pad(
                left=5, right=5, top=5, bottom=5
            ).crop_image(image)
            
            result = self.ocr.ocr(segment, cls=True)
            
            # Handle empty or invalid OCR results
            if not result or not result[0]:
                logger.debug(f"No OCR result for {block.type} block")
                return None
                
            # Extract text and calculate average confidence
            texts = []
            confidences = []
            for line in result[0]:
                if line and len(line) >= 2 and line[1]:
                    texts.append(line[1][0])
                    confidences.append(line[1][1])
            
            if not texts:
                return None
                
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return ExtractedSection(
                type=block.type,
                text=" ".join(texts),
                confidence=round(avg_confidence, 3)
            )
        except Exception as e:
            logger.warning(f"Failed to extract text from block: {e}")
            return None