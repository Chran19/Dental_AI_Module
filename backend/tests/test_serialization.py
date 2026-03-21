"""
Test for image analysis serialization fix
Verifies that numpy booleans are properly converted to Python types
"""

import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils import convert_to_serializable, NumpyTorchEncoder
import numpy as np
import torch


def test_numpy_boolean_serialization():
    """Test that numpy booleans are properly serialized"""
    
    # Create test data with numpy booleans
    test_data = {
        'is_abnormal': np.bool_(True),
        'needed': np.bool_(False),
        'cortication_present': bool(np.bool_(True)),
    }
    
    # Apply conversion
    result = convert_to_serializable(test_data)
    
    # Verify all booleans are native Python types
    assert isinstance(result['is_abnormal'], bool)
    assert isinstance(result['needed'], bool)
    assert isinstance(result['cortication_present'], bool)
    assert result['is_abnormal'] is True
    assert result['needed'] is False
    
    # Verify it can be serialized to JSON
    json_str = json.dumps(result, cls=NumpyTorchEncoder)
    assert '"is_abnormal": true' in json_str
    assert '"needed": false' in json_str
    
    print("[PASS] Numpy boolean serialization test passed")


def test_nested_numpy_types():
    """Test nested structures with numpy types"""
    
    test_data = {
        'pathology': {
            'class_id': np.int64(0),
            'confidence': np.float32(0.95),
            'is_abnormal': np.bool_(False),
        },
        'region': {
            'class_id': np.int64(5),
            'confidence': np.float64(0.87),
        },
        'values': [np.int32(1), np.int32(2), np.int32(3)],
    }
    
    result = convert_to_serializable(test_data)
    
    # Verify conversions
    assert isinstance(result['pathology']['class_id'], int)
    assert isinstance(result['pathology']['confidence'], float)
    assert isinstance(result['pathology']['is_abnormal'], bool)
    assert isinstance(result['values'][0], int)
    
    # Verify JSON serialization
    json_str = json.dumps(result, cls=NumpyTorchEncoder)
    assert json_str is not None
    
    print("[PASS] Nested numpy types test passed")


def test_pathology_detector_output_serialization():
    """Test that pathology detector output can be serialized"""
    
    # Simulate pathology detector output with numpy types
    pathology_output = {
        'timestamp': '2024-01-15T10:30:00',
        'primary_pathology': {
            'class_id': np.int64(2),
            'name': 'Periapical_Lesion',
            'confidence': np.float64(0.92),
            'confidence_level': 'HIGH'
        },
        'tooth_region': {
            'class_id': np.int64(3),
            'name': 'Premolar_Upper',
            'confidence': np.float64(0.88)
        },
        'severity_score': np.float32(6.5),
        'severity_level': 'MODERATE',
        'model_confidence': np.float32(0.85),
        'all_pathologies': [
            {
                'class_id': np.int64(2),
                'name': 'Periapical_Lesion',
                'probability': np.float64(0.92)
            },
            {
                'class_id': np.int64(1),
                'name': 'Caries',
                'probability': np.float64(0.05)
            }
        ],
        'is_abnormal': np.bool_(True),
        'requires_intervention': {
            'needed': np.bool_(True),
            'urgency': 'HIGH',
            'recommended_action': 'Endodontic treatment or re-treatment recommended'
        }
    }
    
    result = convert_to_serializable(pathology_output)
    
    # Verify all numpy types are converted
    assert isinstance(result['primary_pathology']['class_id'], int)
    assert isinstance(result['primary_pathology']['confidence'], float)
    assert isinstance(result['is_abnormal'], bool)
    assert isinstance(result['requires_intervention']['needed'], bool)
    
    # Verify JSON serialization works
    json_str = json.dumps(result, cls=NumpyTorchEncoder)
    assert '"is_abnormal": true' in json_str
    assert '"needed": true' in json_str
    
    print("[PASS] Pathology detector output serialization test passed")


def test_bone_analyzer_output_serialization():
    """Test that bone analyzer output can be serialized"""
    
    bone_output = {
        'bone_density': {
            'density_ratio': np.float64(0.68),
            'bone_type': 'D2_Dense',
            'pixel_count': np.int64(356352),
            'assessment': 'D2_Dense bone density detected'
        },
        'alveolar_crest': {
            'crest_level_pixels': np.float64(145.5),
            'bone_loss_percentage': np.float64(28.4),
            'assessment': 'Mild to Moderate bone loss'
        },
        'cortication': {
            'present': np.bool_(True),
            'quality': 'Well-defined',
            'assessment': 'Normal lamina dura visible'
        },
        'overall_bone_quality': 'GOOD - Suitable for implant placement',
        'recommendations': 'Normal bone pattern - proceed with standard treatment plan'
    }
    
    result = convert_to_serializable(bone_output)
    
    # Verify conversions
    assert isinstance(result['bone_density']['density_ratio'], float)
    assert isinstance(result['bone_density']['pixel_count'], int)
    assert isinstance(result['cortication']['present'], bool)
    
    # Verify JSON serialization
    json_str = json.dumps(result, cls=NumpyTorchEncoder)
    assert '"present": true' in json_str
    
    print("[PASS] Bone analyzer output serialization test passed")


if __name__ == '__main__':
    test_numpy_boolean_serialization()
    test_nested_numpy_types()
    test_pathology_detector_output_serialization()
    test_bone_analyzer_output_serialization()
    print("\n[PASS] All serialization tests passed!")
