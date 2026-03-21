"""
Pathology Detection Service: Detect dental pathologies from radiographs
"""

import numpy as np
import torch
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PathologyDetector:
    """Detects pathologies in dental radiographs"""
    
    # Pathology thresholds
    DETECTION_THRESHOLD = 0.5
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    
    # Risk levels based on pathology type and severity
    SEVERITY_THRESHOLDS = {
        'Normal': (0, 1),
        'Caries': (1, 3),
        'Periapical_Lesion': (3, 7),
        'Bone_Loss': (2, 8),
        'Abscess': (5, 10),
        'Fracture': (4, 9),
        'Restoration': (0, 2),
        'Implant': (0, 2)
    }
    
    def __init__(self, model, device: str = 'cpu'):
        self.model = model
        self.device = device
        self.model.eval()
        
    def detect_pathologies(self, 
                          image_tensor: torch.Tensor) -> Dict:
        """
        Detect pathologies in image
        
        Args:
            image_tensor: Preprocessed image tensor (1, 3, 512, 512)
            
        Returns:
            Dictionary with detection results
        """
        with torch.no_grad():
            predictions = self.model(image_tensor.unsqueeze(0) if image_tensor.dim() == 3 
                                    else image_tensor)
        
        # Extract outputs
        pathology_logits = predictions['pathology_logits'][0]  # (num_pathologies,)
        region_logits = predictions['region_logits'][0]  # (num_regions,)
        severity = predictions['severity'][0].item()  # scalar
        confidence = predictions['confidence'][0].item()  # scalar
        
        # Get probabilities
        pathology_probs = torch.softmax(pathology_logits, dim=0).cpu().numpy()
        region_probs = torch.softmax(region_logits, dim=0).cpu().numpy()
        
        # Get top pathology
        top_pathology_id = np.argmax(pathology_probs)
        top_pathology_prob = pathology_probs[top_pathology_id]
        
        # Get top region
        top_region_id = np.argmax(region_probs)
        top_region_prob = region_probs[top_region_id]
        
        # Build result dictionary
        result = {
            'timestamp': datetime.now().isoformat(),
            'primary_pathology': {
                'class_id': int(top_pathology_id),
                'name': self.model.get_pathology_name(int(top_pathology_id)),
                'confidence': float(top_pathology_prob),
                'confidence_level': self._get_confidence_level(top_pathology_prob)
            },
            'tooth_region': {
                'class_id': int(top_region_id),
                'name': self.model.get_region_name(int(top_region_id)),
                'confidence': float(top_region_prob)
            },
            'severity_score': float(severity),
            'severity_level': self._get_severity_level(top_pathology_id, severity),
            'model_confidence': float(confidence),
            'all_pathologies': self._get_all_pathologies(pathology_probs),
            'is_abnormal': bool(top_pathology_id != 0),  # 0 is 'Normal'
            'requires_intervention': self._assess_intervention_need(
                top_pathology_id, severity, confidence
            )
        }
        
        logger.info(f"Detected: {result['primary_pathology']['name']} "
                   f"(confidence: {result['primary_pathology']['confidence']:.2%})")
        
        return result
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Classify confidence as LOW, MODERATE, HIGH"""
        if confidence < 0.6:
            return 'LOW'
        elif confidence < 0.85:
            return 'MODERATE'
        else:
            return 'HIGH'
    
    def _get_severity_level(self, pathology_id: int, severity: float) -> str:
        """Classify severity as MILD, MODERATE, SEVERE"""
        pathology_name = self.model.get_pathology_name(pathology_id)
        
        if pathology_name == 'Normal':
            return 'NONE'
        
        # Get thresholds for this pathology
        if pathology_name in self.SEVERITY_THRESHOLDS:
            min_sev, max_sev = self.SEVERITY_THRESHOLDS[pathology_name]
        else:
            min_sev, max_sev = 1, 10
        
        # Normalize severity to 0-1
        if max_sev > min_sev:
            norm_severity = (severity - min_sev) / (max_sev - min_sev)
        else:
            norm_severity = severity / 10
        
        if norm_severity < 0.33:
            return 'MILD'
        elif norm_severity < 0.67:
            return 'MODERATE'
        else:
            return 'SEVERE'
    
    def _get_all_pathologies(self, probs: np.ndarray) -> List[Dict]:
        """Get all pathologies above threshold, sorted by probability"""
        results = []
        for class_id, prob in enumerate(probs):
            if prob > self.DETECTION_THRESHOLD:
                results.append({
                    'class_id': int(class_id),
                    'name': self.model.get_pathology_name(class_id),
                    'probability': float(prob)
                })
        
        # Sort by probability descending
        results.sort(key=lambda x: x['probability'], reverse=True)
        return results[:5]  # Return top 5
    
    def _assess_intervention_need(self, pathology_id: int, 
                                 severity: float, 
                                 confidence: float) -> Dict:
        """Assess if intervention is needed"""
        pathology_name = self.model.get_pathology_name(pathology_id)
        
        # Pathologies that always need intervention
        urgent_pathologies = ['Abscess', 'Fracture', 'Periapical_Lesion']
        
        needs_intervention = pathology_name in urgent_pathologies or (
            pathology_name not in ['Normal', 'Restoration'] and 
            severity > 5 and 
            confidence > 0.7
        )
        
        return {
            'needed': bool(needs_intervention),
            'urgency': self._get_urgency(pathology_name, severity),
            'recommended_action': self._get_recommended_action(pathology_name, severity)
        }
    
    def _get_urgency(self, pathology_name: str, severity: float) -> str:
        """Determine urgency level"""
        if pathology_name == 'Abscess':
            return 'EMERGENCY'
        elif pathology_name in ['Fracture', 'Periapical_Lesion']:
            return 'HIGH'
        elif severity > 7:
            return 'HIGH'
        elif severity > 4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommended_action(self, pathology_name: str, severity: float) -> str:
        """Get recommended clinical action"""
        if pathology_name == 'Caries':
            return 'Requires restoration, consider preventive assessment'
        elif pathology_name == 'Periapical_Lesion':
            return 'Endodontic treatment or re-treatment recommended'
        elif pathology_name == 'Abscess':
            return 'Immediate drainage and antibiotics needed'
        elif pathology_name == 'Bone_Loss':
            return 'Periodontal assessment and treatment plan needed'
        elif pathology_name == 'Fracture':
            return 'Surgical consultation recommended'
        else:
            return 'Monitor and follow-up as needed'
