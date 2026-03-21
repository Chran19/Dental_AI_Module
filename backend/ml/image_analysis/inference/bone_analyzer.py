"""
Bone Analysis Service: Measure bone loss, density, and structure
"""

import numpy as np
import cv2
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class BoneAnalyzer:
    """Analyzes bone loss, density, and measurements from radiographs"""
    
    def __init__(self):
        """Initialize bone analyzer"""
        pass
    
    def analyze_bone_loss(self, image: np.ndarray) -> Dict:
        """
        Estimate bone loss from radiograph
        
        Args:
            image: Preprocessed radiograph (512, 512, 3) float32 0-1
            
        Returns:
            Dictionary with bone loss analysis
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = (image * 255).astype(np.uint8)
        
        # Analyze bone density regions
        bone_analysis = self._analyze_bone_density(gray)
        
        # Estimate alveolar bone level
        alveolar_analysis = self._analyze_alveolar_crest(gray)
        
        # Detect cortication
        cortication = self._analyze_cortication(gray)
        
        return {
            'bone_density': bone_analysis,
            'alveolar_crest': alveolar_analysis,
            'cortication': cortication,
            'overall_bone_quality': self._assess_bone_quality(
                bone_analysis, alveolar_analysis, cortication
            ),
            'recommendations': self._get_bone_recommendations(
                bone_analysis, alveolar_analysis, cortication
            )
        }
    
    def _analyze_bone_density(self, gray: np.ndarray) -> Dict:
        """Analyze bone density patterns"""
        # Apply threshold to identify bone regions
        _, bone_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        bone_mask = cv2.morphologyEx(bone_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate bone coverage
        total_pixels = bone_mask.size
        bone_pixels = cv2.countNonZero(bone_mask)
        bone_density = bone_pixels / total_pixels if total_pixels > 0 else 0
        
        # Estimate bone type (D1-D4 classification)
        bone_type = self._classify_bone_type(bone_density)
        
        return {
            'density_ratio': float(bone_density),
            'bone_type': bone_type,
            'pixel_count': int(bone_pixels),
            'assessment': f'{bone_type} bone density detected'
        }
    
    def _classify_bone_type(self, density: float) -> str:
        """Classify bone based on density (D1-D4)"""
        if density > 0.75:
            return 'D1_Very_Dense'
        elif density > 0.60:
            return 'D2_Dense'
        elif density > 0.45:
            return 'D3_Moderate'
        else:
            return 'D4_Low_Density'
    
    def _analyze_alveolar_crest(self, gray: np.ndarray) -> Dict:
        """Analyze alveolar bone crest level"""
        height = gray.shape[0]
        
        # Scan from apical to coronal to find bone crest
        bone_levels = []
        for col in range(0, gray.shape[1], 10):  # Sample every 10 pixels
            col_data = gray[:, col]
            # Find transitions (bone to marrow/tooth)
            diff = np.diff(col_data)
            # Look for significant intensity changes
            edges = np.where(np.abs(diff) > 30)[0]
            if len(edges) > 0:
                bone_levels.append(edges[0])
        
        if bone_levels:
            avg_crest_level = np.mean(bone_levels)
            bone_loss_percentage = (avg_crest_level / height) * 100
        else:
            avg_crest_level = height / 2
            bone_loss_percentage = 0
        
        return {
            'crest_level_pixels': float(avg_crest_level),
            'bone_loss_percentage': float(bone_loss_percentage),
            'assessment': self._assess_bone_loss_severity(bone_loss_percentage)
        }
    
    def _assess_bone_loss_severity(self, loss_percentage: float) -> str:
        """Assess severity of bone loss"""
        if loss_percentage < 25:
            return 'Minimal or No bone loss'
        elif loss_percentage < 50:
            return 'Mild to Moderate bone loss'
        elif loss_percentage < 75:
            return 'Advanced bone loss'
        else:
            return 'Severe bone loss'
    
    def _analyze_cortication(self, gray: np.ndarray) -> Dict:
        """Detect cortication (well-defined bone outline)"""
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for continuous lines (cortication)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, 
                               minLineLength=50, maxLineGap=10)
        
        # Assess cortication quality
        cortication_present = bool(lines is not None and len(lines) > 3)
        cortication_quality = 'Well-defined' if cortication_present else 'Ill-defined or Absent'
        
        return {
            'present': cortication_present,
            'quality': cortication_quality,
            'assessment': 'Normal lamina dura visible' if cortication_present 
                         else 'Lamina dura not clearly visible - possible pathology'
        }
    
    def _assess_bone_quality(self, density: Dict, 
                           alveolar: Dict, 
                           cortication: Dict) -> str:
        """Overall bone quality assessment"""
        score = 0
        
        # Density score
        if density['bone_type'] in ['D1_Very_Dense', 'D2_Dense']:
            score += 2
        elif density['bone_type'] == 'D3_Moderate':
            score += 1
        
        # Alveolar bone score
        if alveolar['bone_loss_percentage'] < 25:
            score += 2
        elif alveolar['bone_loss_percentage'] < 50:
            score += 1
        
        # Cortication score
        if cortication['present']:
            score += 2
        
        # Overall assessment
        if score >= 5:
            return 'EXCELLENT - Ideal for implant placement'
        elif score >= 3:
            return 'GOOD - Suitable for implant placement'
        elif score >= 1:
            return 'FAIR - May require bone grafting'
        else:
            return 'POOR - Significant bone augmentation needed'
    
    def _get_bone_recommendations(self, density: Dict, 
                                 alveolar: Dict, 
                                 cortication: Dict) -> str:
        """Get clinical recommendations based on bone analysis"""
        recommendations = []
        
        # Density recommendations
        if density['bone_type'] == 'D4_Low_Density':
            recommendations.append('Low bone density - assess for underlying systemic conditions')
        
        # Bone loss recommendations
        if alveolar['bone_loss_percentage'] > 50:
            recommendations.append('Significant bone loss - consider bone grafting before implant')
        
        # Cortication recommendations
        if not cortication['present']:
            recommendations.append('Ill-defined bone outline - possible infection or chronic pathology')
        
        if not recommendations:
            recommendations.append('Normal bone pattern - proceed with standard treatment plan')
        
        return ' | '.join(recommendations)
