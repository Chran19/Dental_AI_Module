"""
Phase 4 Test: Image Analysis Framework
Tests all components of the dental image analysis module
"""

import sys
import json
import torch
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.image_analysis.preprocessing.image_loader import DentalImageLoader
from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
from ml.image_analysis.models.cnn_model import create_dental_cnn_model
from ml.image_analysis.inference.pathology_detector import PathologyDetector
from ml.image_analysis.inference.bone_analyzer import BoneAnalyzer
from ml.image_analysis.inference.image_analyzer_service import ImageAnalyzerService
import numpy as np


def test_image_loader():
    """Test image loading"""
    print("=" * 60)
    print("[TEST 1] Image Loader Module")
    print("=" * 60)
    
    loader = DentalImageLoader()
    print("✓ Image loader initialized")
    
    # Test validation
    result = loader.validate_file('nonexistent.jpg')
    assert result == False, "Should reject nonexistent files"
    print("✓ File validation working")
    
    # Test supported formats
    assert '.jpg' in loader.SUPPORTED_FORMATS
    assert '.png' in loader.SUPPORTED_FORMATS
    print(f"✓ Supported formats: {loader.SUPPORTED_FORMATS}")
    
    return True


def test_image_preprocessor():
    """Test image preprocessing"""
    print("\n" + "=" * 60)
    print("[TEST 2] Image Preprocessor")
    print("=" * 60)
    
    preprocessor = DentalImagePreprocessor()
    
    # Create dummy image
    dummy_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    print(f"✓ Created dummy image: {dummy_image.shape}")
    
    # Test preprocessing pipeline
    processed = preprocessor.preprocess_radiograph(dummy_image)
    assert processed.shape == (512, 512, 3), f"Wrong shape: {processed.shape}"
    assert processed.dtype == np.float32, f"Wrong dtype: {processed.dtype}"
    assert processed.min() >= 0 and processed.max() <= 1, "Values out of range"
    print(f"✓ Preprocessing pipeline working")
    print(f"  Output shape: {processed.shape}")
    print(f"  Output dtype: {processed.dtype}")
    print(f"  Value range: [{processed.min():.3f}, {processed.max():.3f}]")
    
    return True


def test_cnn_model():
    """Test CNN model"""
    print("\n" + "=" * 60)
    print("[TEST 3] CNN Model (ResNet50-based)")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    model = create_dental_cnn_model(device=device, pretrained=True)
    model.eval()
    print(f"✓ CNN model created (ResNet50 backbone)")
    print(f"  Pathology classes: {len(model.PATHOLOGY_CLASSES)}")
    print(f"  Region classes: {len(model.REGION_CLASSES)}")
    
    # Test forward pass
    dummy_input = torch.randn(1, 3, 512, 512).to(device)
    with torch.no_grad():
        output = model(dummy_input)
    
    assert 'pathology_logits' in output, "Missing pathology_logits"
    assert 'region_logits' in output, "Missing region_logits"
    assert 'severity' in output, "Missing severity"
    assert 'confidence' in output, "Missing confidence"
    print("✓ Forward pass successful")
    print(f"  Pathology logits shape: {output['pathology_logits'].shape}")
    print(f"  Region logits shape: {output['region_logits'].shape}")
    print(f"  Severity shape: {output['severity'].shape}")
    print(f"  Confidence shape: {output['confidence'].shape}")
    
    return True


def test_pathology_detector():
    """Test pathology detection"""
    print("\n" + "=" * 60)
    print("[TEST 4] Pathology Detector")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = create_dental_cnn_model(device=device, pretrained=True)
    detector = PathologyDetector(model, device=device)
    print("✓ Pathology detector initialized")
    
    # Create dummy image tensor
    dummy_tensor = torch.randn(3, 512, 512).to(device)
    
    # Detect
    results = detector.detect_pathologies(dummy_tensor)
    
    assert 'primary_pathology' in results, "Missing primary_pathology"
    assert 'tooth_region' in results, "Missing tooth_region"
    assert 'severity_score' in results, "Missing severity_score"
    print("✓ Pathology detection working")
    print(f"  Detected: {results['primary_pathology']['name']}")
    print(f"  Confidence: {results['primary_pathology']['confidence']:.2%}")
    print(f"  Severity: {results['severity_score']:.1f}/10")
    print(f"  Requires intervention: {results['requires_intervention']['needed']}")
    
    return True


def test_bone_analyzer():
    """Test bone analysis"""
    print("\n" + "=" * 60)
    print("[TEST 5] Bone Analyzer")
    print("=" * 60)
    
    analyzer = BoneAnalyzer()
    print("✓ Bone analyzer initialized")
    
    # Create dummy preprocessed image
    dummy_image = np.random.rand(512, 512, 3).astype(np.float32)
    
    # Analyze
    results = analyzer.analyze_bone_loss(dummy_image)
    
    assert 'bone_density' in results, "Missing bone_density"
    assert 'alveolar_crest' in results, "Missing alveolar_crest"
    assert 'cortication' in results, "Missing cortication"
    assert 'overall_bone_quality' in results, "Missing overall_bone_quality"
    print("✓ Bone analysis working")
    print(f"  Bone type: {results['bone_density']['bone_type']}")
    print(f"  Bone loss %: {results['alveolar_crest']['bone_loss_percentage']:.1f}%")
    print(f"  Cortication: {results['cortication']['quality']}")
    print(f"  Overall quality: {results['overall_bone_quality']}")
    
    return True


def test_image_analyzer_service():
    """Test complete Image Analyzer Service"""
    print("\n" + "=" * 60)
    print("[TEST 6] Complete Image Analyzer Service (M8)")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    service = ImageAnalyzerService(device=device)
    print("✓ Image Analyzer Service (M8) initialized")
    print(f"  Device: {device}")
    print(f"  Model: ResNet50 with pathology/region/severity heads")
    
    # Create dummy image and save
    import tempfile
    from PIL import Image
    
    dummy_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    img = Image.fromarray(dummy_image)
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img.save(tmp.name)
        tmp_path = tmp.name
    
    # Analyze
    try:
        results = service.analyze_image(tmp_path)
        
        assert results['status'] == 'success', "Analysis failed"
        assert 'pathology_analysis' in results, "Missing pathology_analysis"
        assert 'bone_analysis' in results, "Missing bone_analysis"
        assert 'clinical_summary' in results, "Missing clinical_summary"
        assert 'recommendations' in results, "Missing recommendations"
        
        print("✓ Image analysis successful")
        print(f"  File: {results['file_info']['filename']}")
        print(f"  Pathology: {results['pathology_analysis']['primary_pathology']['name']}")
        print(f"  Severity: {results['pathology_analysis']['severity_level']}")
        print(f"  Bone quality: {results['bone_analysis']['overall_bone_quality']}")
        print(f"  Clinical summary:")
        for line in results['clinical_summary'].split('\n'):
            print(f"    {line}")
        
    finally:
        Path(tmp_path).unlink()
    
    return True


def test_batch_analysis():
    """Test batch image analysis"""
    print("\n" + "=" * 60)
    print("[TEST 7] Batch Image Analysis")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    service = ImageAnalyzerService(device=device)
    
    # Create multiple dummy images
    import tempfile
    from PIL import Image
    
    image_paths = []
    for i in range(3):
        dummy_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        img = Image.fromarray(dummy_image)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name)
            image_paths.append(tmp.name)
    
    try:
        # Analyze batch
        results = service.analyze_image_batch(image_paths)
        
        assert results['total_images'] == 3, "Wrong total image count"
        assert results['processed'] == 3, "Not all images processed"
        assert 'batch_summary' in results, "Missing batch_summary"
        
        print(f"✓ Batch analysis successful")
        print(f"  Total images: {results['total_images']}")
        print(f"  Successfully processed: {results['processed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Batch summary:")
        print(f"    Normal cases: {results['batch_summary'].get('normal_cases', 0)}")
        print(f"    Abnormal cases: {results['batch_summary'].get('abnormal_cases', 0)}")
        print(f"    Urgent cases: {results['batch_summary'].get('urgent_cases', 0)}")
        
    finally:
        for path in image_paths:
            Path(path).unlink()
    
    return True


def run_all_tests():
    """Run all Phase 4 tests"""
    print("\n" + "🔬 " * 20)
    print("PHASE 4: DENTAL IMAGE ANALYSIS - COMPREHENSIVE TEST SUITE")
    print("🔬 " * 20)
    
    tests = [
        test_image_loader,
        test_image_preprocessor,
        test_cnn_model,
        test_pathology_detector,
        test_bone_analyzer,
        test_image_analyzer_service,
        test_batch_analysis,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL PHASE 4 TESTS PASSING - IMAGE ANALYSIS FRAMEWORK READY!")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
