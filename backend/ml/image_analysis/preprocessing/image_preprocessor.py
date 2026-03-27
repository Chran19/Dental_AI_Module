"""
Image Preprocessing: Normalize, resize, and augment dental radiographs

Fixed Issues:
- Removed CLAHE grayscale conversion that destroyed color channels
- Apply CLAHE per-channel to preserve RGB information
- Added proper torchvision transforms for training augmentation
- Separated preprocessing for training vs inference
"""

import numpy as np
import cv2
from typing import Tuple, List, Optional
import logging
from PIL import Image, ImageEnhance
import torch

logger = logging.getLogger(__name__)


class DentalImagePreprocessor:
    """Preprocess dental radiographic images for CNN analysis"""
    
    # Standard input size for CNN model
    STANDARD_SIZE = (512, 512)
    
    # Radiograph-specific preprocessing settings
    CLAHE_CLIP_LIMIT = 2.0
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
            h, w = image.shape[:2]
            scale = min(target_size[0] / h, target_size[1] / w)
            new_h, new_w = int(h * scale), int(w * scale)
            
            resized = cv2.resize(image, (new_w, new_h), 
                               interpolation=cv2.INTER_CUBIC)
            
            # Pad to target size (gray padding for radiographs)
            pad_h = target_size[0] - new_h
            pad_w = target_size[1] - new_w
            pad_top, pad_bottom = pad_h // 2, pad_h - pad_h // 2
            pad_left, pad_right = pad_w // 2, pad_w - pad_w // 2
            
            padded = cv2.copyMakeBorder(resized, pad_top, pad_bottom,
                                       pad_left, pad_right,
                                       cv2.BORDER_CONSTANT, value=[128, 128, 128])
            return padded
        else:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_CUBIC)
    
    @staticmethod
    def normalize_intensity(image: np.ndarray) -> np.ndarray:
        """
        Normalize image intensity for radiographs.
        
        FIXED: Apply CLAHE per-channel instead of converting to grayscale.
        This preserves the RGB structure that ResNet50 expects.
        """
        clahe = cv2.createCLAHE(
            clipLimit=DentalImagePreprocessor.CLAHE_CLIP_LIMIT,
            tileGridSize=DentalImagePreprocessor.CLAHE_GRID_SIZE
        )
        
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Apply CLAHE per channel to preserve color information
            channels = cv2.split(image)
            enhanced_channels = [clahe.apply(ch) for ch in channels]
            enhanced = cv2.merge(enhanced_channels)
            return enhanced
        elif len(image.shape) == 2:
            # Grayscale image
            return clahe.apply(image)
        else:
            return image
    
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
        return cv2.bilateralFilter(image, 9, 75, 75)
    
    @staticmethod
    def preprocess_radiograph(image: np.ndarray,
                            apply_enhancement: bool = True) -> np.ndarray:
        """
        Complete preprocessing pipeline for dental radiographs (inference).
        
        Returns image as float32 in [0, 1] range, ready for the CNN model
        (ImageNet normalization is now applied inside the model's forward pass).
        
        Args:
            image: Input image (H, W, C) uint8
            apply_enhancement: Apply CLAHE intensity normalization
            
        Returns:
            Preprocessed image (512, 512, 3) float32 in [0, 1]
        """
        # 1. Resize to standard size
        resized = DentalImagePreprocessor.resize_image(image)
        
        # 2. Apply CLAHE enhancement per-channel (preserves RGB)
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
    def get_training_transforms():
        """
        Get torchvision transforms for training data augmentation.
        These are applied AFTER loading and converting to tensor.
        
        Returns callable transforms for training.
        """
        import torchvision.transforms as T
        
        return T.Compose([
            T.RandomHorizontalFlip(p=0.5),
            T.RandomRotation(degrees=15, fill=0.5),
            T.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
            T.RandomErasing(p=0.1, scale=(0.02, 0.1)),
        ])
    
    @staticmethod
    def get_validation_transforms():
        """
        Get torchvision transforms for validation/test (no augmentation).
        Returns identity transform.
        """
        import torchvision.transforms as T
        return T.Compose([])  # No augmentation for val/test
    
    @staticmethod
    def augment_image(image: np.ndarray,
                     rotation_range: float = 15,
                     horizontal_flip: bool = False) -> np.ndarray:
        """
        Legacy data augmentation for training (numpy-based).
        Prefer get_training_transforms() for torch-based augmentation.
        """
        h, w = image.shape[:2]
        
        # Rotate
        angle = np.random.uniform(-rotation_range, rotation_range)
        rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REFLECT)
        
        # Horizontal flip
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
