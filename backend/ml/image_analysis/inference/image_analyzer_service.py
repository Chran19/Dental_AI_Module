"""
Image Analyzer Service: Main orchestrator for M8 (Dental Image Analysis)
Integrates pathology detection, bone analysis, and clinical insights
"""

import torch
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..preprocessing.image_loader import DentalImageLoader
from ..preprocessing.image_preprocessor import DentalImagePreprocessor
from ..models.cnn_model import DentalCNNModel, create_dental_cnn_model
from .pathology_detector import PathologyDetector
from .bone_analyzer import BoneAnalyzer

logger = logging.getLogger(__name__)


class ImageAnalyzerService:
    """
    Phase 4 M8: Dental Image Analysis Service
    Analyzes radiographs for pathology, bone loss, and treatment planning
    """
    
    def __init__(self, model_path: Optional[str] = None, 
                 device: str = 'cpu'):
        """
        Initialize Image Analyzer Service
        
        Args:
            model_path: Path to trained CNN model
            device: 'cpu' or 'cuda'
        """
        self.device = device
        
        # Initialize components
        self.image_loader = DentalImageLoader()
        self.image_preprocessor = DentalImagePreprocessor()
        self.bone_analyzer = BoneAnalyzer()
        
        # Load CNN model
        default_model_path = Path(__file__).parent.parent.parent.parent / 'models' / 'dental_cnn_model_phase4.pth'
        model_path = model_path or str(default_model_path)
        
        if Path(model_path).exists():
            try:
                self.model = create_dental_cnn_model(device=device, pretrained=False)
                checkpoint = torch.load(model_path, map_location=device)
                self.model.load_state_dict(checkpoint['model_state_dict'] if isinstance(checkpoint, dict) else checkpoint)
                self.model.to(device)
                logger.info(f"✅ Loaded trained model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}. Using ImageNet weights.")
                self.model = create_dental_cnn_model(device=device, pretrained=True)
        else:
            logger.warning(f"Model not found at {model_path}. Using ImageNet pretrained weights.")
            self.model = create_dental_cnn_model(device=device, pretrained=True)
        
        # Initialize pathology detector
        self.pathology_detector = PathologyDetector(self.model, device=device)
        
        logger.info(f"ImageAnalyzerService initialized on {device}")
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze single radiographic image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Comprehensive analysis dictionary
        """
        logger.info(f"Analyzing image: {image_path}")
        
        # 1. Load image
        raw_image = self.image_loader.load_image(image_path)
        if raw_image is None:
            return self._error_response(f"Failed to load image: {image_path}")
        
        # 2. Get image info
        image_info = self.image_loader.get_image_info(image_path)
        
        # 3. Preprocess image
        processed_image = self.image_preprocessor.preprocess_radiograph(raw_image)
        image_tensor = torch.from_numpy(processed_image).permute(2, 0, 1).to(self.device)
        
        # 4. Detect pathologies
        pathology_results = self.pathology_detector.detect_pathologies(image_tensor)
        
        # 5. Analyze bone
        bone_results = self.bone_analyzer.analyze_bone_loss(processed_image)
        
        # 6. Generate annotated image
        annotated_img, img_base64 = self.generate_annotated_image(processed_image, pathology_results)
        
        # 7. Generate clinical summary
        clinical_summary = self._generate_clinical_summary(pathology_results, bone_results)
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'file_info': image_info,
            'pathology_analysis': pathology_results,
            'bone_analysis': bone_results,
            'clinical_summary': clinical_summary,
            'annotated_image_base64': img_base64,
            'recommendations': self._generate_recommendations(
                pathology_results, bone_results
            )
        }
    
    def analyze_image_batch(self, image_paths: List[str]) -> Dict:
        """
        Analyze multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Batch analysis results
        """
        logger.info(f"Analyzing batch of {len(image_paths)} images")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(image_paths),
            'processed': 0,
            'failed': 0,
            'images': [],
            'batch_summary': {}
        }
        
        for image_path in image_paths:
            try:
                analysis = self.analyze_image(image_path)
                if analysis['status'] == 'success':
                    results['images'].append(analysis)
                    results['processed'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error analyzing {image_path}: {str(e)}")
                results['failed'] += 1
        
        # Generate batch summary
        results['batch_summary'] = self._generate_batch_summary(results['images'])
        
        return results
    
    def analyze_from_bytes(self, image_bytes: bytes, 
                          filename: str = 'image.jpg') -> Dict:
        """
        Analyze image from bytes (for file uploads)
        
        Args:
            image_bytes: Image file bytes
            filename: Original filename
            
        Returns:
            Analysis results
        """
        import tempfile
        from PIL import Image as PILImage
        
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, 
                                            delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            # Analyze
            result = self.analyze_image(tmp_path)
            
            # Clean up
            Path(tmp_path).unlink()
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing bytes: {str(e)}")
            return self._error_response(str(e))
    
    def _generate_clinical_summary(self, pathology: Dict, bone: Dict) -> str:
        """Generate clinical summary from analysis results"""
        lines = []
        
        # Primary finding
        lines.append(f"Primary Finding: {pathology['primary_pathology']['name']} "
                    f"({pathology['primary_pathology']['confidence_level']})")
        
        # Severity
        lines.append(f"Severity: {pathology['severity_level']} "
                    f"(score: {pathology['severity_score']:.1f}/10)")
        
        # Location
        lines.append(f"Location: {pathology['tooth_region']['name']}")
        
        # Bone status
        lines.append(f"Bone Status: {bone['overall_bone_quality']}")
        
        # Intervention need
        if pathology['requires_intervention']['needed']:
            lines.append(f"Intervention: {pathology['requires_intervention']['urgency']} - "
                        f"{pathology['requires_intervention']['recommended_action']}")
        else:
            lines.append("Intervention: Routine follow-up")
        
        return '\n'.join(lines)
    
    def _generate_recommendations(self, pathology: Dict, bone: Dict) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # Pathology-based recommendations
        recommendations.append(pathology['requires_intervention']['recommended_action'])
        
        # Bone-based recommendations
        recommendations.append(bone['recommendations'])
        
        # Urgency recommendations
        if pathology['requires_intervention']['urgency'] == 'EMERGENCY':
            recommendations.append('⚠️  URGENT: Patient requires immediate clinical review')
        elif pathology['requires_intervention']['urgency'] == 'HIGH':
            recommendations.append('Priority: Schedule appointment within 1-2 weeks')
        
        # Follow-up recommendations
        if pathology['primary_pathology']['name'] != 'Normal':
            recommendations.append('Follow-up imaging recommended in 3-6 months after treatment')
        else:
            recommendations.append('Normal findings - routine follow-up as per standard protocol')
        
        return recommendations
    
    def _generate_batch_summary(self, images: List[Dict]) -> Dict:
        """Generate summary for batch analysis"""
        if not images:
            return {}
        
        # Count pathologies
        pathology_counts = {}
        urgent_count = 0
        
        for img in images:
            pathology = img['pathology_analysis']['primary_pathology']['name']
            pathology_counts[pathology] = pathology_counts.get(pathology, 0) + 1
            
            if img['pathology_analysis']['requires_intervention']['urgency'] == 'EMERGENCY':
                urgent_count += 1
        
        return {
            'total_analyzed': len(images),
            'pathology_distribution': pathology_counts,
            'urgent_cases': urgent_count,
            'normal_cases': len([img for img in images 
                               if img['pathology_analysis']['is_abnormal'] == False]),
            'abnormal_cases': len([img for img in images 
                                  if img['pathology_analysis']['is_abnormal'] == True])
        }
    
    def generate_annotated_image(self, image_array: np.ndarray, 
                                pathology_results: Dict) -> Tuple[np.ndarray, str]:
        """
        Generate annotated radiograph with detected pathologies marked
        
        Args:
            image_array: Preprocessed image (512, 512, 3) float32
            pathology_results: Detection results from pathology detector
            
        Returns:
            Tuple of (annotated_image_array, base64_string)
        """
        import cv2
        import base64
        from io import BytesIO
        from PIL import Image
        
        # Convert to uint8 for annotation
        img_uint8 = (image_array * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
        
        # Add pathology information as text overlay
        text_y = 30
        primary_path = pathology_results.get('primary_pathology', {})
        
        # Pathology name
        pathology_name = primary_path.get('name', 'Unknown')
        confidence = primary_path.get('confidence', 0)
        cv2.putText(img_bgr, f"Pathology: {pathology_name} ({confidence:.1%})",
                   (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Severity score
        severity = primary_path.get('severity_score', 0)
        text_y += 30
        cv2.putText(img_bgr, f"Severity: {severity:.1f}/10",
                   (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Region
        region = pathology_results.get('tooth_region', 'Unknown')
        text_y += 30
        cv2.putText(img_bgr, f"Region: {region}",
                   (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Interventional status
        intervention = pathology_results.get('requires_intervention', {})
        if intervention.get('needed'):
            text_y += 30
            urgency_color = (0, 0, 255) if intervention.get('urgency') == 'EMERGENCY' else (0, 165, 255)
            cv2.putText(img_bgr, f"⚠️ {intervention.get('urgency', 'URGENT')}",
                       (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, urgency_color, 2)
        
        # Draw border around image
        cv2.rectangle(img_bgr, (5, 5), (507, 507), (0, 255, 0), 2)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', img_bgr)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return img_bgr, img_base64
    
    def _error_response(self, error_msg: str) -> Dict:
        """Generate error response"""
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': error_msg
        }


def create_image_analyzer_service(model_path: Optional[str] = None,
                                 device: str = 'cpu') -> ImageAnalyzerService:
    """Factory function to create analyzer service"""
    return ImageAnalyzerService(model_path=model_path, device=device)
