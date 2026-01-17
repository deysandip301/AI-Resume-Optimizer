"""Recruiter gaze simulation using visual saliency detection."""
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def generate_saliency_heatmap(image_path: str) -> Optional[np.ndarray]:
    """
    Generates a visual attention map using Static Saliency.
    Helps validate the 'F-Pattern' of reading.

    Args:
        image_path: Path to the image file to analyze.

    Returns:
        BGR image with heatmap overlay, or None if processing fails.

    Raises:
        FileNotFoundError: If image file doesn't exist.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(path))
    if image is None:
        logger.error(f"Failed to read image: {image_path}")
        return None

    try:
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        success, saliency_map = saliency.computeSaliency(image)

        if not success or saliency_map is None:
            logger.error("Saliency computation failed")
            return None

        # Normalize and convert to heatmap
        saliency_map = (saliency_map * 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)

        # Resize heatmap to match original image dimensions
        heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))

        # Overlay heatmap on original image
        result = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)

        logger.info(f"Generated saliency heatmap for {path.name}")
        return result

    except cv2.error as e:
        logger.error(f"OpenCV error during saliency computation: {e}")
        return None
