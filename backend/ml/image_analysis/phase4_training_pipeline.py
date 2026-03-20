"""
Phase 4: Complete Training Pipeline for Dental Image Analysis
Trains CNN model using the prepared dental_images dataset
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import logging
import json
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Phase4DentalImageDataset(Dataset):
    """Dataset loader for Phase 4 dental radiographs"""
    
    def __init__(self, dataset_root: Path, split_file: str = 'train_split.txt', 
                 labels_file: str = 'labels.csv', preprocessor=None):
        """
        Initialize dataset
        
        Args:
            dataset_root: Root directory containing dental_images
            split_file: Which split file to use (train/val/test)
            labels_file: CSV file with labels
            preprocessor: Image preprocessor instance
        """
        self.dataset_root = Path(dataset_root)
        self.images_dir = self.dataset_root / 'raw_images'
        self.labels_file = self.dataset_root / labels_file
        self.split_file = self.dataset_root / split_file
        self.preprocessor = preprocessor
        
        # Verify paths exist
        if not self.images_dir.exists():
            raise ValueError(f"Images directory not found: {self.images_dir}")
        if not self.labels_file.exists():
            raise ValueError(f"Labels file not found: {self.labels_file}")
        if not self.split_file.exists():
            raise ValueError(f"Split file not found: {self.split_file}")
        
        # Load labels
        self.labels_df = pd.read_csv(self.labels_file)
        
        # Load split
        with open(self.split_file, 'r') as f:
            self.image_names = [line.strip() for line in f if line.strip()]
        
        # Create pathology and region mappings
        self.pathology_to_idx = {
            'Normal': 0,
            'Caries': 1,
            'Periapical_Lesion': 2,
            'Bone_Loss': 3,
            'Abscess': 4,
            'Fracture': 5,
            'Restoration': 6,
            'Implant': 7
        }
        
        self.region_to_idx = {
            'Anterior_Upper': 0,
            'Anterior_Lower': 1,
            'Premolar_Upper': 2,
            'Premolar_Lower': 3,
            'Molar_Upper': 4,
            'Molar_Lower': 5
        }
        
        logger.info(f"Initialized Phase4DentalImageDataset with {len(self.image_names)} images from {split_file}")
    
    def __len__(self):
        return len(self.image_names)
    
    def __getitem__(self, idx):
        """Get single image and labels"""
        img_name = self.image_names[idx]
        img_path = self.images_dir / img_name
        
        # Load image
        from ml.image_analysis.preprocessing.image_loader import DentalImageLoader
        loader = DentalImageLoader()
        raw_image = loader.load_image(str(img_path))
        
        if raw_image is None:
            logger.error(f"Failed to load image: {img_path}")
            raise RuntimeError(f"Failed to load image: {img_path}")
        
        # Preprocess image
        if self.preprocessor:
            processed = self.preprocessor.preprocess_radiograph(raw_image)
        else:
            # Basic preprocessing if no preprocessor provided
            processed = raw_image / 255.0 if raw_image.max() > 1 else raw_image
        
        # Convert to tensor
        tensor = torch.from_numpy(processed).permute(2, 0, 1).float()
        
        # Get labels from CSV
        label_row = self.labels_df[self.labels_df['filename'] == img_name]
        
        if len(label_row) == 0:
            logger.warning(f"No labels found for {img_name}, using defaults")
            pathology_idx = 0
            region_idx = 0
            severity = 0.0
        else:
            pathology_class = label_row.iloc[0]['pathology_class']
            region_class = label_row.iloc[0]['tooth_region']
            severity = float(label_row.iloc[0]['severity_score'])
            
            pathology_idx = self.pathology_to_idx.get(pathology_class, 0)
            region_idx = self.region_to_idx.get(region_class, 0)
        
        return {
            'image': tensor,
            'filename': img_name,
            'pathology': torch.tensor(pathology_idx, dtype=torch.long),
            'region': torch.tensor(region_idx, dtype=torch.long),
            'severity': torch.tensor(severity, dtype=torch.float32),
        }


def train_phase4_model(config: dict = None):
    """
    Complete training pipeline for Phase 4 dental image analysis
    
    Args:
        config: Training configuration dictionary
    """
    
    if config is None:
        config = {
            'dataset_root': Path('backend/ml/datasets/dental_images'),
            'model_save_path': Path('backend/ml/models/dental_cnn_model_phase4.pth'),
            'results_dir': Path('backend/ml/results'),
            'batch_size': 16,
            'num_epochs': 20,
            'learning_rate': 0.001,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'num_workers': 2,
        }
    
    print("\n" + "="*70)
    print("PHASE 4: DENTAL IMAGE CNN TRAINING PIPELINE")
    print("="*70)
    
    logger.info(f"Configuration: {config}")
    
    # Create results directory
    config['results_dir'].mkdir(parents=True, exist_ok=True)
    
    # Initialize model
    from ml.image_analysis.models.cnn_model import DentalCNNModel
    from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
    
    logger.info("\n📦 Loading CNN Model...")
    model = DentalCNNModel(num_pathologies=8, num_regions=6, pretrained=True)
    model = model.to(config['device'])
    
    logger.info(f"Model loaded. Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Initialize preprocessor
    preprocessor = DentalImagePreprocessor()
    logger.info("✓ Image preprocessor initialized")
    
    # Create datasets
    logger.info("\n📂 Loading Datasets...")
    train_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='train_split.txt',
        preprocessor=preprocessor
    )
    
    val_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='val_split.txt',
        preprocessor=preprocessor
    )
    
    test_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='test_split.txt',
        preprocessor=preprocessor
    )
    
    logger.info(f"✓ Train: {len(train_dataset)} images")
    logger.info(f"✓ Val: {len(val_dataset)} images")
    logger.info(f"✓ Test: {len(test_dataset)} images")
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers'],
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers'],
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers'],
        pin_memory=True
    )
    
    logger.info("✓ Data loaders created")
    
    # Initialize loss functions and optimizer
    logger.info("\n⚙️ Initializing Training Components...")
    
    pathology_loss_fn = nn.CrossEntropyLoss(weight=torch.tensor([1.0, 2.0, 2.5, 1.5, 3.0, 4.0, 2.0, 3.5]).to(config['device']))
    region_loss_fn = nn.CrossEntropyLoss()
    severity_loss_fn = nn.MSELoss()
    
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'], weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3
    )
    
    logger.info("✓ Loss functions and optimizer initialized")
    
    # Training loop
    logger.info("\n🚀 Starting Training...\n")
    
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_pathology_acc': [],
        'val_pathology_acc': [],
        'epochs': []
    }
    
    best_val_loss = float('inf')
    patience_counter = 0
    patience = 5
    
    for epoch in range(config['num_epochs']):
        # Training phase
        model.train()
        train_loss = 0.0
        train_pathology_correct = 0
        train_pathology_total = 0
        
        for batch_idx, batch in enumerate(train_loader):
            images = batch['image'].to(config['device'])
            pathology_labels = batch['pathology'].to(config['device'])
            region_labels = batch['region'].to(config['device'])
            severity_labels = batch['severity'].to(config['device']).unsqueeze(1)
            
            optimizer.zero_grad()
            
            # Forward pass
            predictions = model(images)
            
            # Calculate losses
            pathology_loss = pathology_loss_fn(predictions['pathology_logits'], pathology_labels)
            region_loss = region_loss_fn(predictions['region_logits'], region_labels)
            severity_loss = severity_loss_fn(predictions['severity'], severity_labels)
            
            # Weighted combined loss
            total_loss = 0.5 * pathology_loss + 0.3 * region_loss + 0.2 * severity_loss
            
            # Backward pass
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += total_loss.item()
            
            # Calculate accuracy
            _, predicted = torch.max(predictions['pathology_logits'], 1)
            train_pathology_total += pathology_labels.size(0)
            train_pathology_correct += (predicted == pathology_labels).sum().item()
            
            if (batch_idx + 1) % 5 == 0:
                print(f"Epoch [{epoch+1}/{config['num_epochs']}] Batch [{batch_idx+1}/{len(train_loader)}] "
                      f"Loss: {total_loss.item():.4f}")
        
        avg_train_loss = train_loss / len(train_loader)
        train_acc = train_pathology_correct / train_pathology_total
        history['train_loss'].append(avg_train_loss)
        history['train_pathology_acc'].append(train_acc)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_pathology_correct = 0
        val_pathology_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                images = batch['image'].to(config['device'])
                pathology_labels = batch['pathology'].to(config['device'])
                region_labels = batch['region'].to(config['device'])
                severity_labels = batch['severity'].to(config['device']).unsqueeze(1)
                
                predictions = model(images)
                
                pathology_loss = pathology_loss_fn(predictions['pathology_logits'], pathology_labels)
                region_loss = region_loss_fn(predictions['region_logits'], region_labels)
                severity_loss = severity_loss_fn(predictions['severity'], severity_labels)
                
                total_loss = 0.5 * pathology_loss + 0.3 * region_loss + 0.2 * severity_loss
                val_loss += total_loss.item()
                
                _, predicted = torch.max(predictions['pathology_logits'], 1)
                val_pathology_total += pathology_labels.size(0)
                val_pathology_correct += (predicted == pathology_labels).sum().item()
        
        avg_val_loss = val_loss / len(val_loader)
        val_acc = val_pathology_correct / val_pathology_total
        history['val_loss'].append(avg_val_loss)
        history['val_pathology_acc'].append(val_acc)
        history['epochs'].append(epoch + 1)
        
        print(f"\n{'─'*70}")
        print(f"Epoch [{epoch+1}/{config['num_epochs']}] Summary:")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.4f}")
        print(f"{'─'*70}\n")
        
        # Learning rate scheduling
        scheduler.step(avg_val_loss)
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            config['model_save_path'].parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), config['model_save_path'])
            logger.info(f"✓ Best model saved to {config['model_save_path']}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered after {epoch+1} epochs")
                break
    
    # Save training history
    history_file = config['results_dir'] / f"training_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(history_file, 'w') as f:
        json.dump({k: (v if not isinstance(v[0], torch.Tensor) else [float(x) for x in v]) 
                   for k, v in history.items()}, f, indent=2)
    logger.info(f"✓ Training history saved to {history_file}")
    
    # Evaluate on test set
    logger.info("\n📊 Evaluating on Test Set...")
    model.load_state_dict(torch.load(config['model_save_path']))
    model.eval()
    
    test_pathology_preds = []
    test_pathology_true = []
    
    with torch.no_grad():
        for batch in test_loader:
            images = batch['image'].to(config['device'])
            pathology_labels = batch['pathology'].to(config['device'])
            
            predictions = model(images)
            _, predicted = torch.max(predictions['pathology_logits'], 1)
            
            test_pathology_preds.extend(predicted.cpu().numpy())
            test_pathology_true.extend(pathology_labels.cpu().numpy())
    
    test_results = {
        'accuracy': accuracy_score(test_pathology_true, test_pathology_preds),
        'precision': precision_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0),
        'recall': recall_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0),
        'f1': f1_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0),
    }
    
    logger.info(f"\n{'='*70}")
    logger.info("TEST SET RESULTS:")
    logger.info(f"{'='*70}")
    logger.info(f"Accuracy: {test_results['accuracy']:.4f}")
    logger.info(f"Precision: {test_results['precision']:.4f}")
    logger.info(f"Recall: {test_results['recall']:.4f}")
    logger.info(f"F1-Score: {test_results['f1']:.4f}")
    logger.info(f"{'='*70}\n")
    
    # Save test results
    results_file = config['results_dir'] / f"phase4_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    logger.info(f"✓ Test results saved to {results_file}")
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"\nModel saved: {config['model_save_path']}")
    print(f"Results saved: {results_file}")
    print(f"\nTest Results:")
    print(f"  Accuracy:  {test_results['accuracy']:.4f}")
    print(f"  Precision: {test_results['precision']:.4f}")
    print(f"  Recall:    {test_results['recall']:.4f}")
    print(f"  F1-Score:  {test_results['f1']:.4f}")
    print("="*70 + "\n")
    
    return model, history, test_results


if __name__ == '__main__':
    config = {
        'dataset_root': Path('backend/ml/datasets/dental_images'),
        'model_save_path': Path('backend/ml/models/dental_cnn_model_phase4.pth'),
        'results_dir': Path('backend/ml/results'),
        'batch_size': 16,
        'num_epochs': 20,
        'learning_rate': 0.001,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'num_workers': 0 if sys.platform == 'win32' else 2,  # Windows doesn't support multiprocessing in tests
    }
    
    model, history, results = train_phase4_model(config)
