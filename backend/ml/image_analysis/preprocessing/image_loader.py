"""
Image Loading Module: Handle various dental radiograph formats
Supports: JPG, PNG, DICOM, TIFF
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


class DentalImageLoader:
    """Load dental radiographic images from files or memory"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.dcm'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate image file before loading"""
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Check format
        if file_path.suffix.lower() not in DentalImageLoader.SUPPORTED_FORMATS:
            logger.error(f"Unsupported format: {file_path.suffix}")
            return False
        
        # Check file size
        if file_path.stat().st_size > DentalImageLoader.MAX_FILE_SIZE:
            logger.error(f"File too large: {file_path.stat().st_size} bytes")
            return False
        
        return True
    
    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path
        
        Args:
            file_path: Path to image file
            
        Returns:
            numpy array of image data or None if error
        """
        try:
            if not DentalImageLoader.validate_file(file_path):
                return None
            
            file_path = Path(file_path)
            
            # Handle DICOM format separately if needed
            if file_path.suffix.lower() == '.dcm':
                return DentalImageLoader._load_dicom(file_path)
            
            # Load standard image formats
            img = Image.open(file_path)
            
            # Convert to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            elif img.mode == 'L':  # Grayscale
                img = img.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(img)
            
            logger.info(f"Loaded image: {file_path}, shape: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"Error loading image {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def _load_dicom(file_path: Path) -> Optional[np.ndarray]:
        """Load DICOM files (requires pydicom)"""
        try:
            import pydicom
            # Load DICOM file
            dicom_data = pydicom.dcmread(file_path)
            img_array = dicom_data.pixel_array
            
            # Normalize to 0-255 range
            if img_array.dtype != np.uint8:
                img_array = ((img_array - img_array.min()) / 
                           (img_array.max() - img_array.min()) * 255).astype(np.uint8)
            
            # Convert to RGB
            if len(img_array.shape) == 2:  # Grayscale
                img_array = np.stack([img_array] * 3, axis=-1)
            
            return img_array
        except Exception as e:
            logger.error(f"Error loading DICOM file: {str(e)}")
            return None
    
    @staticmethod
    def load_image_batch(file_paths: list) -> Tuple[list, list]:
        """
        Load multiple images
        
        Args:
            file_paths: List of image file paths
            
        Returns:
            (images list, valid_paths list)
        """
        images = []
        valid_paths = []
        
        for path in file_paths:
            img = DentalImageLoader.load_image(path)
            if img is not None:
                images.append(img)
                valid_paths.append(path)
        
        logger.info(f"Loaded {len(images)}/{len(file_paths)} images successfully")
        return images, valid_paths
    
    @staticmethod
    def get_image_info(file_path: str) -> Optional[dict]:
        """Get image metadata"""
        try:
            if not DentalImageLoader.validate_file(file_path):
                return None
            
            file_info = Path(file_path)
            img = Image.open(file_path)
            
            return {
                'filename': file_info.name,
                'format': img.format,
                'size': img.size,
                'mode': img.mode,
                'file_size_mb': file_info.stat().st_size / (1024 * 1024),
                'dpi': img.info.get('dpi', None)
            }
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return None
