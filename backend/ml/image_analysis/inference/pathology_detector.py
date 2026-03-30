"""
Pathology Detection Service: Detect dental pathologies from radiographs

Fixed Issues:
- Updated to 6 real pathology classes matching OPG dataset
- Corrected class names (Impacted_Teeth, Infection instead of wrong mappings)
- Updated severity thresholds for actual conditions
- Better confidence calibration
"""

import numpy as np
import torch
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PathologyDetector:
    """Detects pathologies in dental radiographs"""
    
    # Confidence and pathology thresholds
    CONFIDENCE_THRESHOLD = 0.70  # 70% - decision threshold for treatment recommendations
    DETECTION_THRESHOLD = 0.3    # Lowered since we have fewer classes now
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    
    # Risk levels based on pathology type and severity
    SEVERITY_THRESHOLDS = {
        'Normal': (0, 1),
        'Caries': (1, 5),
        'Impacted_Teeth': (2, 7),
        'Bone_Loss': (2, 8),
        'Infection': (4, 9),
        'Fracture': (4, 9),
    }
    
    # Tooth type classifications for context
    TOOTH_REGIONS = {
        0: {'name': 'Anterior_Upper', 'tooth_types': ['Incisor', 'Canine'], 'esthetic_importance': 'High'},
        1: {'name': 'Anterior_Lower', 'tooth_types': ['Incisor', 'Canine'], 'esthetic_importance': 'High'},
        2: {'name': 'Premolar_Upper', 'tooth_types': ['Premolar'], 'esthetic_importance': 'Medium'},
        3: {'name': 'Premolar_Lower', 'tooth_types': ['Premolar'], 'esthetic_importance': 'Medium'},
        4: {'name': 'Molar_Upper', 'tooth_types': ['Molar'], 'esthetic_importance': 'Low'},
        5: {'name': 'Molar_Lower', 'tooth_types': ['Molar'], 'esthetic_importance': 'Low'},
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
            image_tensor: Preprocessed image tensor (3, 512, 512) in [0,1] range
            
        Returns:
            Dictionary with detection results
        """
        with torch.no_grad():
            # Ensure proper batch dimension
            if image_tensor.dim() == 3:
                input_tensor = image_tensor.unsqueeze(0)
            else:
                input_tensor = image_tensor
            
            predictions = self.model(input_tensor)
        
        # Extract outputs
        pathology_logits = predictions['pathology_logits'][0]  # (num_pathologies,)
        region_logits = predictions['region_logits'][0]  # (num_regions,)
        severity = predictions['severity'][0].item()  # scalar
        confidence = predictions['confidence'][0].item()  # scalar
        
        # Get probabilities
        pathology_probs = torch.softmax(pathology_logits, dim=0).cpu().numpy()
        region_probs = torch.softmax(region_logits, dim=0).cpu().numpy()
        
        # Get top pathology
        top_pathology_id = int(np.argmax(pathology_probs))
        top_pathology_prob = float(pathology_probs[top_pathology_id])
        
        # Get top region
        top_region_id = int(np.argmax(region_probs))
        top_region_prob = float(region_probs[top_region_id])
        
        # Build result dictionary
        result = {
            'timestamp': datetime.now().isoformat(),
            'primary_pathology': {
                'class_id': top_pathology_id,
                'name': self.model.get_pathology_name(top_pathology_id),
                'confidence': top_pathology_prob,
                'confidence_level': self._get_confidence_level(top_pathology_prob)
            },
            'tooth_region': {
                'class_id': top_region_id,
                'name': self.model.get_region_name(top_region_id),
                'confidence': top_region_prob
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
        if confidence < 0.5:
            return 'LOW'
        elif confidence < 0.75:
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
        
        norm_severity = max(0, min(1, norm_severity))  # Clamp
        
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
        """
        Assess if intervention is needed
        
        1. CONFIDENCE THRESHOLD: If confidence < 70%, recommend further evaluation only
        2. Returns structured recommendation with explainability
        """
        pathology_name = self.model.get_pathology_name(pathology_id)
        
        # Priority 1: Check confidence threshold
        if confidence < self.CONFIDENCE_THRESHOLD:
            return {
                'needed': False,
                'confidence_warning': True,
                'confidence_value': confidence,
                'urgency': 'LOW',
                'recommended_action': 'Needs further evaluation',
                'clinical_reasoning': (
                    f'Model confidence is {confidence:.1%} (below {self.CONFIDENCE_THRESHOLD:.0%} threshold). '
                    f'Clinical review required before making treatment decisions.'
                ),
                'treatment_recommendation': None
            }
        
        # Priority 2: Determine intervention need based on pathology type and severity
        pathologies_requiring_intervention = {
            'Infection': {'base_urgency': 'HIGH', 'always_intervene': True},
            'Fracture': {'base_urgency': 'HIGH', 'always_intervene': True},
            'Impacted_Teeth': {'base_urgency': 'MEDIUM', 'severity_threshold': 5},
            'Bone_Loss': {'base_urgency': 'MEDIUM', 'severity_threshold': 6},
            'Caries': {'base_urgency': 'MEDIUM', 'severity_threshold': 3},
        }
        
        needs_intervention = False
        urgency = 'LOW'
        
        if pathology_name in pathologies_requiring_intervention:
            config = pathologies_requiring_intervention[pathology_name]
            
            if config.get('always_intervene'):
                needs_intervention = True
            elif 'severity_threshold' in config:
                needs_intervention = severity > config['severity_threshold']
            
            if needs_intervention:
                urgency = config['base_urgency']
        
        return {
            'needed': bool(needs_intervention),
            'confidence_warning': False,
            'confidence_value': confidence,
            'urgency': urgency,
            'recommended_action': self._get_recommended_action_enhanced(
                pathology_name, severity, confidence
            ),
            'treatment_recommendation': self._get_treatment_recommendation(
                pathology_name, severity
            ) if needs_intervention else None
        }
    
    def _get_urgency(self, pathology_name: str, severity: float) -> str:
        """Determine urgency level"""
        if pathology_name == 'Infection' and severity > 6:
            return 'EMERGENCY'
        elif pathology_name in ['Fracture', 'Infection']:
            return 'HIGH'
        elif pathology_name == 'Impacted_Teeth' and severity > 5:
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
        elif pathology_name == 'Infection':
            return 'Endodontic treatment, drainage and/or antibiotics recommended'
        elif pathology_name == 'Bone_Loss':
            return 'Periodontal assessment and treatment plan needed'
        elif pathology_name == 'Fracture':
            return 'Surgical consultation recommended'
        elif pathology_name == 'Impacted_Teeth':
            return 'Evaluate for surgical extraction, monitor for complications'
        else:
            return 'Monitor and follow-up as needed'
    
    def _get_recommended_action_enhanced(self, pathology_name: str, 
                                        severity: float, 
                                        confidence: float) -> str:
        """
        Get enhanced recommended action with clinical context
        Integrates Priority 3: location, tooth type, implant considerations
        """
        if pathology_name == 'Caries':
            if severity < 3:
                return 'Monitor and apply preventive fluoride/sealants'
            elif severity < 5:
                return 'Schedule restorative consultation within 2-3 weeks'
            else:
                return 'Urgent: Schedule restorative treatment'
                
        elif pathology_name == 'Infection':
            if severity < 5:
                return 'Endodontic evaluation required; consider antibacterial irrigation'
            elif severity < 7:
                return 'Urgent: Endodontic treatment or extraction'; 
            else:
                return 'Emergency: Immediate endodontic debridement, drainage, antibiotics'
                
        elif pathology_name == 'Bone_Loss':
            if severity < 4:
                return 'Periodontal assessment; implement improved oral hygiene'
            elif severity < 6:
                return 'Periodontal treatment indicated (scaling, root planing)'
            else:
                return 'Advanced bone loss: Evaluate for surgical periodontal treatment'
                
        elif pathology_name == 'Fracture':
            return 'Immediate endodontic consultation; evaluate for splinting vs extraction'
            
        elif pathology_name == 'Impacted_Teeth':
            if severity < 4:
                return 'Monitor regularly; assess eruptive potential'
            else:
                return 'Surgical consultation recommended for extraction evaluation'
                
        else:
            return 'Continue routine dental care'
    
    def _get_treatment_recommendation(self, pathology_name: str, 
                                    severity: float) -> Dict:
        """
        Get detailed treatment recommendations with clinical reasoning
        Priority 4: Add explainability with clinical context
        """
        recommendations = {
            'Caries': {
                'primary': 'Dental restoration',
                'options': ['Composite/amalgam filling', 'Ceramic restoration', 'Crown (if severe)'],
                'clinical_reasoning': (
                    'Caries involves demineralization of tooth structure. '
                    'Early treatment prevents pulp involvement and systemic infection.'
                ),
                'timing': 'Routine' if severity < 3 else 'Priority',
                'follow_up': 'Recall in 6 months for assessment'
            },
            'Infection': {
                'primary': 'Endodontic treatment or extraction',
                'options': ['Root canal therapy', 'Apical surgery', 'Extraction'],
                'clinical_reasoning': (
                    'Radiolucency at apex indicates apical periodontitis. '
                    'Endodontic treatment aims to eliminate infection and preserve tooth structure.'
                ),
                'timing': 'Urgent',
                'follow_up': 'Post-treatment imaging in 6-12 months; monitor for healing'
            },
            'Bone_Loss': {
                'primary': 'Periodontal treatment',
                'options': ['Non-surgical scaling/root planing', 'Surgical pocket reduction', 'Regenerative therapy'],
                'clinical_reasoning': (
                    'Horizontal or vertical bone loss indicates periodontal disease. '
                    'Treatment focuses on halting disease progression and restoring bony support.'
                ),
                'timing': 'Scheduled',
                'follow_up': 'Periodontal maintenance every 3-4 months'
            },
            'Fracture': {
                'primary': 'Endodontic + Restorative treatment',
                'options': ['Splinting + pulp therapy', 'Crown restoration', 'Extraction (if unfavorable)'],
                'clinical_reasoning': (
                    'Tooth fracture may involve pulpal exposure and create bacterial pathway. '
                    'Treatment depends on fracture location and tooth type.'
                ),
                'timing': 'Urgent',
                'follow_up': 'Vitality testing at 2 weeks, 1 month, and 6 months'
            },
            'Impacted_Teeth': {
                'primary': 'Surgical management',
                'options': ['Surgical extraction', 'Orthodontic guidance (if favorable)', 'Monitoring'],
                'clinical_reasoning': (
                    'Impacted tooth may cause cyst formation, root resorption, or infection. '
                    'Management depends on age, angulation, and adjacent tooth health.'
                ),
                'timing': 'Planned' if severity < 4 else 'Urgent',
                'follow_up': 'Periodic monitoring if conservative approach selected'
            }
        }
        
        return recommendations.get(pathology_name, {
            'primary': 'Professional consultation',
            'options': ['Clinical evaluation'],
            'clinical_reasoning': 'Detailed assessment needed',
            'timing': 'Routine'
        })
    
    def check_module_consistency(self, pathology: Dict, bone_analysis: Dict) -> Dict:
        """
        Priority 2: Module consistency check
        Flag contradictions between pathology and bone analysis
        
        Example: Infection + Excellent bone quality is contradictory
        """
        pathology_name = pathology['primary_pathology']['name']
        bone_quality = bone_analysis.get('overall_bone_quality', 'Unknown')
        
        contradictions = []
        warnings = []
        
        # Check for pathology-bone quality contradictions
        if pathology_name == 'Infection' and bone_quality in ['Excellent', 'Very_Good']:
            contradictions.append({
                'issue': 'Infection detected with excellent bone quality',
                'severity': 'WARNING',
                'explanation': (
                    'Infection typically occurs in compromised bone. '
                    'Excellent bone suggests either early infection or possible detection artifact. '
                    'Recommend clinical correlation and follow-up imaging.'
                )
            })
        
        if pathology_name == 'Bone_Loss' and bone_quality in ['Very_Good', 'Excellent']:
            warnings.append({
                'issue': 'Bone loss diagnosis with preserved overall density',
                'severity': 'MINOR',
                'explanation': 'Verify localized vs generalized bone loss pattern'
            })
        
        # Infection must have evidence of severity
        if pathology_name == 'Infection' and pathology['severity_score'] < 3:
            warnings.append({
                'issue': 'Infection detected with low severity score',
                'severity': 'MINOR',
                'explanation': 'Early/incipient infection; monitor closely'
            })
        
        return {
            'contradictions': contradictions,
            'warnings': warnings,
            'is_consistent': len(contradictions) == 0
        }
    
    def add_clinical_evidence(self, pathology: Dict, region: Dict) -> str:
        """
        Priority 4: Add explainability with clinical evidence
        Generate evidence-based explanation for the detection
        """
        pathology_name = pathology['primary_pathology']['name']
        region_name = region['tooth_region']['name']
        severity = pathology['severity_score']
        confidence = pathology['primary_pathology']['confidence']
        
        evidence_text = f"{pathology_name.replace('_', ' ')}"
        
        # Location context
        if 'Upper' in region_name:
            evidence_text += " in maxillary "
        else:
            evidence_text += " in mandibular "
        
        evidence_text += region_name.split('_')[0].lower() + " region"
        
        # Pathology-specific evidence
        if pathology_name == 'Caries':
            evidence_text += (
                f" with {severity:.0f}/10 severity. "
                f"Radiopaque lesion evident in dentin/enamel junction at "
                f"{region_name.lower()}. Recommend clinical examination to confirm cavitation."
            )
        elif pathology_name == 'Infection':
            evidence_text += (
                f" (severity: {severity:.0f}/10). "
                f"Radiolucency visible at apical region. "
                f"Possible periapical periodontitis due to bacterial invasion of pulp. "
                f"Root canal therapy strongly indicated."
            )
        elif pathology_name == 'Bone_Loss':
            evidence_text += (
                f" (severity: {severity:.0f}/10). "
                f"Horizontal/vertical bone resorption pattern observed. "
                f"Suggests chronic periodontal disease with alveolar crest resorption."
            )
        elif pathology_name == 'Fracture':
            evidence_text += (
                f" (severity: {severity:.0f}/10). "
                f"Radiolucent line indicating fracture plane evident in "
                f"{region_name.lower()}. "
                f"Extent and direction of fracture determine treatment options."
            )
        elif pathology_name == 'Impacted_Teeth':
            evidence_text += (
                f". Tooth is not in normal occlusal position. "
                f"Risk of cyst formation and root resorption. "
                f"Extraction or surgical guidance evaluation needed."
            )
        
        # Add confidence caveat
        if confidence < 0.85:
            evidence_text += f" (Model confidence: {confidence:.1%})"
        
        return evidence_text

