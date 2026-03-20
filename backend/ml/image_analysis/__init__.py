"""
Phase 4: Dental Image Analysis Module (M8)

Provides AI-powered analysis of dental radiographs (X-rays, OPG, CBCT):
- Pathology detection (caries, lesions, abscess)
- Bone loss measurement
- Anatomical structure identification
- Treatment planning support
"""

from .preprocessing.image_loader import DentalImageLoader
from .preprocessing.image_preprocessor import DentalImagePreprocessor
from .models.cnn_model import DentalCNNModel
from .inference.pathology_detector import PathologyDetector
from .inference.bone_analyzer import BoneAnalyzer
from .inference.image_analyzer_service import ImageAnalyzerService

__all__ = [
    'DentalImageLoader',
    'DentalImagePreprocessor',
    'DentalCNNModel',
    'PathologyDetector',
    'BoneAnalyzer',
    'ImageAnalyzerService',
]
