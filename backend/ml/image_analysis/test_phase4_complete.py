"""
Phase 4: Comprehensive Testing Suite
Tests all components of the dental image analysis system
"""

import pytest
import torch
import tempfile
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPhase4Integration:
    """Integration tests for Phase 4 dental image analysis"""
    
    @pytest.fixture(scope="class")
    def dataset_available(self):
        """Check if dataset is available"""
        dataset_root = Path('backend/ml/datasets/dental_images')
        return {
            'available': dataset_root.exists(),
            'root': dataset_root,
            'images': (dataset_root / 'raw_images').exists() if dataset_root.exists() else False,
            'labels': (dataset_root / 'labels.csv').exists() if dataset_root.exists() else False,
        }
    
    def test_dataset_structure(self, dataset_available):
        """Test that dataset has correct structure"""
        assert dataset_available['available'], "Dataset not found at backend/ml/datasets/dental_images"
        assert dataset_available['images'], "raw_images directory not found"
        assert dataset_available['labels'], "labels.csv not found"
        
        logger.info("✓ Dataset structure is correct")
    
    def test_data_loader(self, dataset_available):
        """Test Phase4DentalImageDataset can load data"""
        if not dataset_available['available']:
            pytest.skip("Dataset not available")
        
        from ml.image_analysis.phase4_training_pipeline import Phase4DentalImageDataset
        from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
        
        preprocessor = DentalImagePreprocessor()
        
        # Test each split
        for split in ['train', 'val', 'test']:
            dataset = Phase4DentalImageDataset(
                dataset_root=dataset_available['root'],
                split_file=f'{split}_split.txt',
                preprocessor=preprocessor
            )
            
            assert len(dataset) > 0, f"{split} dataset is empty"
            
            # Test loading single item
            sample = dataset[0]
            assert 'image' in sample
            assert 'pathology' in sample
            assert 'region' in sample
            assert 'severity' in sample
            assert sample['image'].shape == (3, 512, 512), f"Image shape is {sample['image'].shape}, expected (3, 512, 512)"
            
            logger.info(f"✓ {split.upper()} split loaded successfully ({len(dataset)} images)")
    
    def test_model_initialization(self):
        """Test CNN model can be initialized"""
        from ml.image_analysis.models.cnn_model import DentalCNNModel
        
        model = DentalCNNModel(num_pathologies=8, num_regions=6, pretrained=False)
        
        assert model is not None
        assert hasattr(model, 'pathology_head')
        assert hasattr(model, 'region_head')
        
        logger.info(f"✓ Model initialized with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    def test_model_forward_pass(self):
        """Test model forward pass"""
        from ml.image_analysis.models.cnn_model import DentalCNNModel
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = DentalCNNModel(num_pathologies=8, num_regions=6, pretrained=False)
        model = model.to(device)
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(2, 3, 512, 512).to(device)
        
        with torch.no_grad():
            output = model(dummy_input)
        
        assert 'pathology_logits' in output
        assert 'region_logits' in output
        assert 'severity' in output
        assert 'confidence' in output
        
        assert output['pathology_logits'].shape == (2, 8)
        assert output['region_logits'].shape == (2, 6)
        assert output['severity'].shape == (2, 1)
        assert output['confidence'].shape == (2, 1)
        
        logger.info("✓ Model forward pass successful")
    
    def test_image_preprocessing(self):
        """Test image preprocessing pipeline"""
        from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
        import numpy as np
        
        preprocessor = DentalImagePreprocessor()
        
        # Create dummy image
        dummy_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        
        processed = preprocessor.preprocess_radiograph(dummy_image)
        
        assert processed.shape == (512, 512, 3)
        assert processed.dtype == np.float32
        assert processed.min() >= 0 and processed.max() <= 1
        
        logger.info("✓ Image preprocessing successful")
    
    def test_training_pipeline_setup(self, dataset_available):
        """Test training pipeline can be initialized"""
        if not dataset_available['available']:
            pytest.skip("Dataset not available")
        
        from ml.image_analysis.phase4_training_pipeline import Phase4DentalImageDataset, train_phase4_model
        from torch.utils.data import DataLoader
        
        # Test with tiny batch
        preprocessor = None  # test without preprocessor first
        
        dataset = Phase4DentalImageDataset(
            dataset_root=dataset_available['root'],
            split_file='train_split.txt',
            preprocessor=preprocessor
        )
        
        loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=0)
        
        # Get one batch
        batch = next(iter(loader))
        
        assert len(batch['image']) == 2
        assert batch['image'].shape == (2, 3, 512, 512)
        assert len(batch['pathology']) == 2
        
        logger.info("✓ Training pipeline initialized successfully")
    
    def test_evaluator_initialization(self, dataset_available):
        """Test evaluator can be initialized"""
        if not dataset_available['available']:
            pytest.skip("Dataset not available")
        
        from ml.image_analysis.phase4_evaluator import Phase4ModelEvaluator
        
        model_path = Path('backend/ml/models/dental_cnn_model_phase4.pth')
        
        evaluator = Phase4ModelEvaluator(
            model_path=model_path,
            dataset_root=dataset_available['root'],
            device='cpu'
        )
        
        assert evaluator is not None
        assert evaluator.dataset_root == dataset_available['root']
        
        logger.info("✓ Evaluator initialized successfully")


class TestDataIntegrity:
    """Tests for dataset integrity and quality"""
    
    @pytest.fixture
    def dataset_root(self):
        return Path('backend/ml/datasets/dental_images')
    
    def test_labels_csv_format(self, dataset_root):
        """Validate labels.csv format"""
        if not dataset_root.exists():
            pytest.skip("Dataset not available")
        
        import pandas as pd
        
        labels_file = dataset_root / 'labels.csv'
        assert labels_file.exists(), "labels.csv not found"
        
        df = pd.read_csv(labels_file)
        
        # Check required columns
        required_cols = ['filename', 'pathology_class', 'tooth_region', 'severity_score']
        for col in required_cols:
            assert col in df.columns, f"Column {col} not found in labels.csv"
        
        # Check no null values
        assert df.isnull().sum().sum() == 0, "Found null values in labels.csv"
        
        # Check valid pathology classes
        valid_pathologies = {'Normal', 'Caries', 'Fracture', 'Implant', 'Bone_Loss', 'Periapical_Lesion', 'Abscess', 'Restoration'}
        assert set(df['pathology_class'].unique()).issubset(valid_pathologies), "Invalid pathology classes found"
        
        # Check severity range
        assert (df['severity_score'].min() >= 0) and (df['severity_score'].max() <= 10), "Severity scores out of range"
        
        logger.info(f"✓ labels.csv format is valid ({len(df)} records)")
    
    def test_split_files_exist(self, dataset_root):
        """Check that all split files exist"""
        if not dataset_root.exists():
            pytest.skip("Dataset not available")
        
        for split in ['train', 'val', 'test']:
            split_file = dataset_root / f'{split}_split.txt'
            assert split_file.exists(), f"{split}_split.txt not found"
            
            with open(split_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            assert len(lines) > 0, f"{split}_split.txt is empty"
            logger.info(f"✓ {split}_split.txt exists ({len(lines)} files)")
    
    def test_image_files_exist(self, dataset_root):
        """Check that referenced images exist"""
        if not dataset_root.exists():
            pytest.skip("Dataset not available")
        
        import pandas as pd
        
        labels_df = pd.read_csv(dataset_root / 'labels.csv')
        images_dir = dataset_root / 'raw_images'
        
        for filename in labels_df['filename'].head(20):  # Test first 20
            img_path = images_dir / filename
            assert img_path.exists(), f"Image not found: {img_path}"
        
        logger.info(f"✓ Image files verified ({len(labels_df)} total)")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
