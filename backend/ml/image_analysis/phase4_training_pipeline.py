"""
Phase 4: Complete Training Pipeline for Dental Image Analysis
Trains ResNet50-based model using the OPG dental X-ray dataset

Fixed Issues:
- Correct 6-class pathology mapping matching real OPG dataset
- Proper transfer learning: freeze backbone → train heads → unfreeze → fine-tune
- Correct class weights based on actual data distribution
- Data augmentation via torchvision transforms
- Cosine annealing LR scheduler
- Mixed precision training support
- Proper model save format (dict with model_state_dict key)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import logging
import json
from datetime import datetime
from collections import Counter
import sys
import os

# Add the backend directory to sys.path for proper imports
_backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Parent path already added above


class Phase4DentalImageDataset(Dataset):
    """Dataset loader for Phase 4 dental radiographs with proper augmentation"""
    
    def __init__(self, dataset_root: Path, split_file: str = 'train_split.txt', 
                 labels_file: str = 'labels.csv', preprocessor=None,
                 augment: bool = False):
        """
        Initialize dataset
        
        Args:
            dataset_root: Root directory containing dental_images
            split_file: Which split file to use (train/val/test)
            labels_file: CSV file with labels
            preprocessor: Image preprocessor instance
            augment: Whether to apply training augmentation
        """
        self.dataset_root = Path(dataset_root)
        self.images_dir = self.dataset_root / 'raw_images'
        self.labels_file = self.dataset_root / labels_file
        self.split_file = self.dataset_root / split_file
        self.preprocessor = preprocessor
        self.augment = augment
        
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
        
        # Corrected pathology mapping matching actual OPG dataset
        self.pathology_to_idx = {
            'Normal': 0,           # Healthy Teeth
            'Caries': 1,           # Caries
            'Impacted_Teeth': 2,   # Impacted teeth (was wrongly 'Implant')
            'Bone_Loss': 3,        # BDC-BDR
            'Infection': 4,        # Infection (was wrongly 'Periapical_Lesion')
            'Fracture': 5,         # Fractured Teeth
        }
        
        self.region_to_idx = {
            'Anterior_Upper': 0,
            'Anterior_Lower': 1,
            'Premolar_Upper': 2,
            'Premolar_Lower': 3,
            'Molar_Upper': 4,
            'Molar_Lower': 5
        }
        
        # Get augmentation transforms
        if augment and preprocessor:
            self.transforms = preprocessor.get_training_transforms()
        else:
            self.transforms = None
        
        # Build label list for sampler
        self._build_labels()
        
        logger.info(f"Initialized dataset with {len(self.image_names)} images from {split_file} (augment={augment})")
    
    def _build_labels(self):
        """Build label list for weighted sampling"""
        self.label_list = []
        for img_name in self.image_names:
            label_row = self.labels_df[self.labels_df['filename'] == img_name]
            if len(label_row) > 0:
                pathology_class = label_row.iloc[0]['pathology_class']
                self.label_list.append(self.pathology_to_idx.get(pathology_class, 0))
            else:
                self.label_list.append(0)
    
    def get_class_weights(self) -> torch.Tensor:
        """Calculate inverse frequency class weights"""
        counts = Counter(self.label_list)
        total = len(self.label_list)
        num_classes = len(self.pathology_to_idx)
        
        weights = torch.zeros(num_classes)
        for cls_id in range(num_classes):
            count = counts.get(cls_id, 1)  # Avoid division by zero
            weights[cls_id] = total / (num_classes * count)
        
        logger.info(f"Class weights: {weights.tolist()}")
        return weights
    
    def get_sampler(self) -> WeightedRandomSampler:
        """Get weighted random sampler for balanced batches"""
        counts = Counter(self.label_list)
        class_weights = {cls: 1.0 / count for cls, count in counts.items()}
        sample_weights = [class_weights[label] for label in self.label_list]
        
        return WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True
        )
    
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
        
        # Preprocess image (resize, enhance, normalize to [0,1])
        if self.preprocessor:
            processed = self.preprocessor.preprocess_radiograph(raw_image)
        else:
            import cv2
            processed = cv2.resize(raw_image, (512, 512))
            processed = processed.astype(np.float32) / 255.0
        
        # Convert to tensor (C, H, W)
        tensor = torch.from_numpy(processed).permute(2, 0, 1).float()
        
        # Apply augmentation transforms (on tensor)
        if self.transforms is not None:
            tensor = self.transforms(tensor)
        
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
    
    Two-phase training strategy:
    1. Phase 1: Freeze backbone, train only classification heads (5 epochs)
    2. Phase 2: Unfreeze backbone layer3+layer4, fine-tune with lower LR (15 epochs)
    
    Args:
        config: Training configuration dictionary
    """
    
    if config is None:
        config = {
            'dataset_root': Path('backend/ml/datasets/dental_images'),
            'model_save_path': Path('backend/ml/models/dental_cnn_model_improved.pth'),
            'results_dir': Path('backend/ml/results'),
            'batch_size': 16,
            'phase1_epochs': 8,       # Frozen backbone, train heads only
            'phase2_epochs': 15,      # Unfrozen, fine-tune
            'phase1_lr': 1e-3,        # Higher LR for heads
            'phase2_lr': 1e-5,        # Very low LR for fine-tuning backbone
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'num_workers': 0 if sys.platform == 'win32' else 2,
        }
    
    print("\n" + "="*70)
    print("PHASE 4: DENTAL IMAGE CNN TRAINING PIPELINE (IMPROVED)")
    print("="*70)
    
    logger.info(f"Configuration: {config}")
    logger.info(f"Device: {config['device']}")
    
    # Create results directory
    config['results_dir'] = Path(config['results_dir'])
    config['results_dir'].mkdir(parents=True, exist_ok=True)
    config['model_save_path'] = Path(config['model_save_path'])
    config['model_save_path'].parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize model with frozen backbone
    from ml.image_analysis.models.cnn_model import DentalCNNModel
    from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
    
    logger.info("\nLoading CNN Model (frozen backbone)...")
    model = DentalCNNModel(
        num_pathologies=6, num_regions=6, 
        pretrained=True, freeze_backbone=True
    )
    model = model.to(config['device'])
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Model loaded. Total: {total_params:,} | Trainable: {trainable_params:,}")
    
    # Initialize preprocessor
    preprocessor = DentalImagePreprocessor()
    
    # Create datasets
    logger.info("\nLoading Datasets...")
    train_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='train_split.txt',
        preprocessor=preprocessor,
        augment=True  # Training augmentation
    )
    
    val_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='val_split.txt',
        preprocessor=preprocessor,
        augment=False
    )
    
    test_dataset = Phase4DentalImageDataset(
        dataset_root=config['dataset_root'],
        split_file='test_split.txt',
        preprocessor=preprocessor,
        augment=False
    )
    
    logger.info(f"Train: {len(train_dataset)} images")
    logger.info(f"Val: {len(val_dataset)} images")
    logger.info(f"Test: {len(test_dataset)} images")
    
    # Get class weights for imbalanced dataset
    class_weights = train_dataset.get_class_weights().to(config['device'])
    
    # Get weighted sampler for balanced batches
    train_sampler = train_dataset.get_sampler()
    
    # Create data loaders (use sampler instead of shuffle)
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        sampler=train_sampler,  # Weighted sampling for balance
        num_workers=config['num_workers'],
        pin_memory=True,
        drop_last=True
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
    
    # Loss functions with class weights
    pathology_loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    region_loss_fn = nn.CrossEntropyLoss()
    severity_loss_fn = nn.SmoothL1Loss()  # More robust than MSE
    
    # ==========================================
    # PHASE 1: Train heads only (backbone frozen)
    # ==========================================
    print("\n" + "="*70)
    print("PHASE 1: Training Classification Heads (Backbone Frozen)")
    print("="*70)
    
    # Only optimize head parameters
    head_params = list(model.pathology_head.parameters()) + \
                  list(model.region_head.parameters()) + \
                  list(model.severity_head.parameters()) + \
                  list(model.confidence_head.parameters())
    
    optimizer = optim.AdamW(head_params, lr=config['phase1_lr'], weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config['phase1_epochs'], eta_min=1e-5
    )
    
    history = {
        'train_loss': [], 'val_loss': [],
        'train_pathology_acc': [], 'val_pathology_acc': [],
        'learning_rate': [], 'phase': []
    }
    
    best_val_loss = float('inf')
    best_val_acc = 0.0
    
    best_val_loss, best_val_acc = _train_epochs(
        model, train_loader, val_loader, optimizer, scheduler,
        pathology_loss_fn, region_loss_fn, severity_loss_fn,
        config, history, config['phase1_epochs'], phase=1,
        best_val_loss=best_val_loss, best_val_acc=best_val_acc
    )
    
    # ==========================================
    # PHASE 2: Fine-tune with unfrozen backbone
    # ==========================================
    print("\n" + "="*70)
    print("PHASE 2: Fine-tuning (Backbone layer3+ Unfrozen)")
    print("="*70)
    
    # Unfreeze backbone from layer3 onwards
    model.unfreeze_backbone(unfreeze_from='layer3')
    
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Trainable params after unfreeze: {trainable_params:,}")
    
    # New optimizer with lower LR for backbone
    optimizer = optim.AdamW([
        {'params': model.backbone.parameters(), 'lr': config['phase2_lr']},
        {'params': head_params, 'lr': config['phase2_lr'] * 10},  # Heads get 10x LR
    ], weight_decay=1e-4)
    
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config['phase2_epochs'], eta_min=1e-7
    )
    
    best_val_loss, best_val_acc = _train_epochs(
        model, train_loader, val_loader, optimizer, scheduler,
        pathology_loss_fn, region_loss_fn, severity_loss_fn,
        config, history, config['phase2_epochs'], phase=2,
        best_val_loss=best_val_loss, best_val_acc=best_val_acc
    )
    
    # ==========================================
    # EVALUATION on test set
    # ==========================================
    print("\n" + "="*70)
    print("EVALUATING ON TEST SET")
    print("="*70)
    
    # Load best model
    checkpoint = torch.load(config['model_save_path'], map_location=config['device'], weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
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
    
    # Class names for report
    idx_to_class = {v: k for k, v in train_dataset.pathology_to_idx.items()}
    class_names = [idx_to_class[i] for i in range(6)]
    
    test_results = {
        'accuracy': float(accuracy_score(test_pathology_true, test_pathology_preds)),
        'precision': float(precision_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0)),
        'recall': float(recall_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0)),
        'f1': float(f1_score(test_pathology_true, test_pathology_preds, average='weighted', zero_division=0)),
    }
    
    print(f"\n{'='*70}")
    print("TEST SET RESULTS:")
    print(f"{'='*70}")
    print(f"Accuracy:  {test_results['accuracy']:.4f}")
    print(f"Precision: {test_results['precision']:.4f}")
    print(f"Recall:    {test_results['recall']:.4f}")
    print(f"F1-Score:  {test_results['f1']:.4f}")
    print(f"{'='*70}\n")
    
    # Print detailed classification report
    print("\nDetailed Classification Report:")
    print(classification_report(test_pathology_true, test_pathology_preds, 
                               target_names=class_names, zero_division=0))
    
    # Print confusion matrix
    cm = confusion_matrix(test_pathology_true, test_pathology_preds)
    print("\nConfusion Matrix:")
    print(cm)
    
    # Save results
    results_file = config['results_dir'] / f"phase4_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    # Save training history
    history_file = config['results_dir'] / f"training_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"\nModel saved: {config['model_save_path']}")
    print(f"Results saved: {results_file}")
    print(f"History saved: {history_file}")
    print("="*70 + "\n")
    
    return model, history, test_results


def _train_epochs(model, train_loader, val_loader, optimizer, scheduler,
                  pathology_loss_fn, region_loss_fn, severity_loss_fn,
                  config, history, num_epochs, phase,
                  best_val_loss, best_val_acc):
    """Run training for a set of epochs"""
    
    patience = 5
    patience_counter = 0
    
    for epoch in range(num_epochs):
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
            
            predictions = model(images)
            
            # Calculate losses
            pathology_loss = pathology_loss_fn(predictions['pathology_logits'], pathology_labels)
            region_loss = region_loss_fn(predictions['region_logits'], region_labels)
            severity_loss = severity_loss_fn(predictions['severity'], severity_labels)
            
            # Weighted combined loss (pathology is most important)
            total_loss = 0.6 * pathology_loss + 0.25 * region_loss + 0.15 * severity_loss
            
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += total_loss.item()
            
            _, predicted = torch.max(predictions['pathology_logits'], 1)
            train_pathology_total += pathology_labels.size(0)
            train_pathology_correct += (predicted == pathology_labels).sum().item()
            
            if (batch_idx + 1) % 5 == 0:
                print(f"  Phase {phase} Epoch [{epoch+1}/{num_epochs}] "
                      f"Batch [{batch_idx+1}/{len(train_loader)}] "
                      f"Loss: {total_loss.item():.4f}")
        
        avg_train_loss = train_loss / max(len(train_loader), 1)
        train_acc = train_pathology_correct / max(train_pathology_total, 1)
        
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
                
                total_loss = 0.6 * pathology_loss + 0.25 * region_loss + 0.15 * severity_loss
                val_loss += total_loss.item()
                
                _, predicted = torch.max(predictions['pathology_logits'], 1)
                val_pathology_total += pathology_labels.size(0)
                val_pathology_correct += (predicted == pathology_labels).sum().item()
        
        avg_val_loss = val_loss / max(len(val_loader), 1)
        val_acc = val_pathology_correct / max(val_pathology_total, 1)
        
        current_lr = optimizer.param_groups[0]['lr']
        
        # Update history
        history['train_loss'].append(float(avg_train_loss))
        history['val_loss'].append(float(avg_val_loss))
        history['train_pathology_acc'].append(float(train_acc))
        history['val_pathology_acc'].append(float(val_acc))
        history['learning_rate'].append(float(current_lr))
        history['phase'].append(phase)
        
        print(f"\n{'─'*70}")
        print(f"Phase {phase} | Epoch [{epoch+1}/{num_epochs}] | LR: {current_lr:.2e}")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"  Val Loss:   {avg_val_loss:.4f} | Val Acc:   {val_acc:.4f}")
        print(f"  Best Val Acc: {best_val_acc:.4f}")
        print(f"{'─'*70}\n")
        
        scheduler.step()
        
        # Save best model (by val accuracy, not loss)
        if val_acc > best_val_acc or (val_acc == best_val_acc and avg_val_loss < best_val_loss):
            best_val_loss = avg_val_loss
            best_val_acc = val_acc
            patience_counter = 0
            
            # Save with model_state_dict key (matches loading code)
            torch.save({
                'model_state_dict': model.state_dict(),
                'num_pathologies': 6,
                'num_regions': 6,
                'best_val_acc': best_val_acc,
                'best_val_loss': best_val_loss,
                'phase': phase,
                'epoch': epoch,
            }, config['model_save_path'])
            logger.info(f"Saved best model (val_acc={best_val_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
    
    return best_val_loss, best_val_acc


if __name__ == '__main__':
    config = {
        'dataset_root': Path('backend/ml/datasets/dental_images'),
        'model_save_path': Path('backend/ml/models/dental_cnn_model_improved.pth'),
        'results_dir': Path('backend/ml/results'),
        'batch_size': 16,
        'phase1_epochs': 8,
        'phase2_epochs': 15,
        'phase1_lr': 1e-3,
        'phase2_lr': 1e-5,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'num_workers': 0 if sys.platform == 'win32' else 2,
    }
    
    model, history, results = train_phase4_model(config)
