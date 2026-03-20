"""
Image Preprocessing: Normalize, resize, and augment dental radiographs
"""

import numpy as np
import cv2
from typing import Tuple, List, Optional
import logging
from PIL import ImageEnhance, Image

logger = logging.getLogger(__name__)


class DentalImagePreprocessor:
    """Preprocess dental radiographic images for CNN analysis"""
    
    # Standard input size for CNN model
    STANDARD_SIZE = (512, 512)
    
    # Radiograph-specific preprocessing settings
    CLAHE_CLIP_LIMIT = 2.0  # Contrast Limited Adaptive Histogram Equalization
    CLAHE_GRID_SIZE = (8, 8)
    
    @staticmethod
    def resize_image(image: np.ndarray, 
                     target_size: Tuple[int, int] = STANDARD_SIZE,
                     preserve_aspect: bool = True) -> np.ndarray:
        """
        Resize image to target size
        
        Args:
            image: Input image (H, W, C)
            target_size: (height, width)
            preserve_aspect: Keep aspect ratio with padding
            
        Returns:
            Resized image
        """
        if preserve_aspect:
            # Calculate scale to fit image in target_size
            h, w = image.shape[:2]
            scale = min(target_size[0] / h, target_size[1] / w)
            new_h, new_w = int(h * scale), int(w * scale)
            
            # Resize
            resized = cv2.resize(image, (new_w, new_h), 
                               interpolation=cv2.INTER_CUBIC)
            
            # Pad to target size (gray padding)
            pad_h = target_size[0] - new_h
            pad_w = target_size[1] - new_w
            pad_top, pad_bottom = pad_h // 2, pad_h - pad_h // 2
            pad_left, pad_right = pad_w // 2, pad_w - pad_w // 2
            
            padded = cv2.copyMakeBorder(resized, pad_top, pad_bottom,
                                       pad_left, pad_right,
                                       cv2.BORDER_CONSTANT, value=[128, 128, 128])
            return padded
        else:
            # Direct resize (may distort)
            return cv2.resize(image, target_size, interpolation=cv2.INTER_CUBIC)
    
    @staticmethod
    def normalize_intensity(image: np.ndarray) -> np.ndarray:
        """
        Normalize image intensity for radiographs
        Radiographs benefit from histogram equalization to improve contrast
        """
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Better for radiographs than standard histogram equalization
        clahe = cv2.createCLAHE(clipLimit=DentalImagePreprocessor.CLAHE_CLIP_LIMIT,
                               tileGridSize=DentalImagePreprocessor.CLAHE_GRID_SIZE)
        enhanced = clahe.apply(gray)
        
        # Convert back to RGB
        if len(image.shape) == 3:
            enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
            return enhanced_rgb
        else:
            return enhanced
    
    @staticmethod
    def normalize_to_float32(image: np.ndarray, 
                           scale: float = 255.0) -> np.ndarray:
        """
        Normalize image to float32 in range [0, 1]
        """
        image = image.astype(np.float32) / scale
        return np.clip(image, 0.0, 1.0)
    
    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, 
                          kernel_size: int = 3) -> np.ndarray:
        """Apply Gaussian blur for noise reduction"""
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def apply_bilateral_filter(image: np.ndarray) -> np.ndarray:
        """
        Apply bilateral filter
        Preserves edges while smoothing (good for radiographs)
        """
        if len(image.shape) == 3:
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            return cv2.bilateralFilter(image, 9, 75, 75)
    
    @staticmethod
    def preprocess_radiograph(image: np.ndarray,
                            apply_enhancement: bool = True) -> np.ndarray:
        """
        Complete preprocessing pipeline for dental radiographs
        
        Args:
            image: Input image (H, W, C)
            apply_enhancement: Apply intensity normalization
            
        Returns:
            Preprocessed image ready for CNN
        """
        # 1. Resize to standard size
        resized = DentalImagePreprocessor.resize_image(image)
        
        # 2. Apply enhancement if requested
        if apply_enhancement:
            enhanced = DentalImagePreprocessor.normalize_intensity(resized)
        else:
            enhanced = resized
        
        # 3. Apply bilateral filter for noise reduction while preserving edges
        filtered = DentalImagePreprocessor.apply_bilateral_filter(enhanced)
        
        # 4. Normalize to float32 [0, 1]
        normalized = DentalImagePreprocessor.normalize_to_float32(filtered)
        
        logger.debug(f"Preprocessed image shape: {normalized.shape}, dtype: {normalized.dtype}")
        return normalized
    
    @staticmethod
    def augment_image(image: np.ndarray,
                     rotation_range: float = 15,
                     horizontal_flip: bool = False) -> np.ndarray:
        """
        Data augmentation for training (elastic deformations, rotation)
        
        Args:
            image: Input image
            rotation_range: Max rotation in degrees
            horizontal_flip: Apply horizontal flip
            
        Returns:
            Augmented image
        """
        h, w = image.shape[:2]
        
        # Rotate
        angle = np.random.uniform(-rotation_range, rotation_range)
        rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REFLECT)
        
        # Horizontal flip (only if image is not oriented-specific)
        if horizontal_flip and np.random.random() > 0.5:
            rotated = cv2.flip(rotated, 1)
        
        return rotated
    
    @staticmethod
    def preprocess_batch(images: List[np.ndarray],
                        apply_enhancement: bool = True) -> List[np.ndarray]:
        """Preprocess batch of images"""
        preprocessed = []
        for img in images:
            processed = DentalImagePreprocessor.preprocess_radiograph(
                img, apply_enhancement=apply_enhancement
            )
            preprocessed.append(processed)
        return preprocessed
