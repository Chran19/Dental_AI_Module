"""
Phase 4: Model Evaluation and Analysis Module
Comprehensive evaluation of trained dental image CNN model
"""

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase4ModelEvaluator:
    """Comprehensive evaluation for Phase 4 dental image CNN model"""
    
    PATHOLOGY_CLASSES = {
        0: 'Normal',
        1: 'Caries',
        2: 'Periapical_Lesion',
        3: 'Bone_Loss',
        4: 'Abscess',
        5: 'Fracture',
        6: 'Restoration',
        7: 'Implant'
    }
    
    REGION_CLASSES = {
        0: 'Anterior_Upper',
        1: 'Anterior_Lower',
        2: 'Premolar_Upper',
        3: 'Premolar_Lower',
        4: 'Molar_Upper',
        5: 'Molar_Lower'
    }
    
    def __init__(self, model_path: Path, dataset_root: Path, device: str = 'cpu'):
        """
        Initialize evaluator
        
        Args:
            model_path: Path to trained model
            dataset_root: Root directory of dataset
            device: Device to use (cpu/cuda)
        """
        self.model_path = Path(model_path)
        self.dataset_root = Path(dataset_root)
        self.device = device
        self.results = {}
        
        logger.info(f"Initializing Phase4ModelEvaluator")
        logger.info(f"  Model: {model_path}")
        logger.info(f"  Dataset: {dataset_root}")
        logger.info(f"  Device: {device}")
    
    def evaluate_on_split(self, split_name: str = 'test'):
        """
        Evaluate model on specified dataset split
        
        Args:
            split_name: 'train', 'val', or 'test'
        
        Returns:
            Dictionary with evaluation metrics
        """
        from ml.image_analysis.phase4_training_pipeline import Phase4DentalImageDataset
        from ml.image_analysis.models.cnn_model import DentalCNNModel
        from torch.utils.data import DataLoader
        
        logger.info(f"\n{'='*70}")
        logger.info(f"EVALUATING ON {split_name.upper()} SET")
        logger.info(f"{'='*70}")
        
        # Load model
        model = DentalCNNModel(num_pathologies=8, num_regions=6, pretrained=False)
        if self.model_path.exists():
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            logger.info(f"✓ Model loaded from {self.model_path}")
        else:
            logger.warning(f"Model file not found: {self.model_path}")
            return {}
        
        model = model.to(self.device)
        model.eval()
        
        # Load dataset
        from ml.image_analysis.preprocessing.image_preprocessor import DentalImagePreprocessor
        preprocessor = DentalImagePreprocessor()
        
        dataset = Phase4DentalImageDataset(
            dataset_root=self.dataset_root,
            split_file=f'{split_name}_split.txt',
            preprocessor=preprocessor
        )
        
        dataloader = DataLoader(dataset, batch_size=16, shuffle=False, num_workers=0)
        
        # Collect predictions and ground truth
        pathology_preds = []
        pathology_true = []
        region_preds = []
        region_true = []
        severity_preds = []
        severity_true = []
        confidences = []
        filenames = []
        
        with torch.no_grad():
            for batch_idx, batch in enumerate(dataloader):
                images = batch['image'].to(self.device)
                
                predictions = model(images)
                
                # Pathology
                pathology_logits = predictions['pathology_logits']
                pathology_probs = torch.softmax(pathology_logits, dim=1)
                _, pathology_pred = torch.max(pathology_probs, 1)
                
                # Region
                region_logits = predictions['region_logits']
                region_probs = torch.softmax(region_logits, dim=1)
                _, region_pred = torch.max(region_probs, 1)
                
                # Severity
                severity_pred = predictions['severity']
                
                # Confidence (max softmax probability)
                confidence = torch.max(pathology_probs, 1)[0]
                
                pathology_preds.extend(pathology_pred.cpu().numpy())
                pathology_true.extend(batch['pathology'].cpu().numpy())
                region_preds.extend(region_pred.cpu().numpy())
                region_true.extend(batch['region'].cpu().numpy())
                severity_preds.extend(severity_pred.squeeze().cpu().numpy())
                severity_true.extend(batch['severity'].cpu().numpy())
                confidences.extend(confidence.cpu().numpy())
                filenames.extend(batch['filename'])
                
                if (batch_idx + 1) % 5 == 0:
                    logger.info(f"Processed {batch_idx + 1}/{len(dataloader)} batches")
        
        # Calculate metrics
        results = {
            'split': split_name,
            'timestamp': datetime.now().isoformat(),
            'samples': len(pathology_true),
            
            'pathology': {
                'accuracy': float(accuracy_score(pathology_true, pathology_preds)),
                'precision': float(precision_score(pathology_true, pathology_preds, average='weighted', zero_division=0)),
                'recall': float(recall_score(pathology_true, pathology_preds, average='weighted', zero_division=0)),
                'f1': float(f1_score(pathology_true, pathology_preds, average='weighted', zero_division=0)),
                'confusion_matrix': confusion_matrix(pathology_true, pathology_preds).tolist(),
            },
            
            'region': {
                'accuracy': float(accuracy_score(region_true, region_preds)),
                'precision': float(precision_score(region_true, region_preds, average='weighted', zero_division=0)),
                'recall': float(recall_score(region_true, region_preds, average='weighted', zero_division=0)),
                'f1': float(f1_score(region_true, region_preds, average='weighted', zero_division=0)),
            },
            
            'severity': {
                'mae': float(np.mean(np.abs(np.array(severity_true) - np.array(severity_preds)))),
                'rmse': float(np.sqrt(np.mean((np.array(severity_true) - np.array(severity_preds)) ** 2))),
                'r2': float(1 - np.sum((np.array(severity_true) - np.array(severity_preds)) ** 2) / 
                           np.sum((np.array(severity_true) - np.mean(severity_true)) ** 2)),
            },
            
            'confidence': {
                'mean': float(np.mean(confidences)),
                'std': float(np.std(confidences)),
                'min': float(np.min(confidences)),
                'max': float(np.max(confidences)),
            }
        }
        
        # Per-class metrics
        results['pathology_per_class'] = {}
        for class_idx, class_name in self.PATHOLOGY_CLASSES.items():
            mask = np.array(pathology_true) == class_idx
            if mask.sum() > 0:
                results['pathology_per_class'][class_name] = {
                    'samples': int(mask.sum()),
                    'accuracy': float(accuracy_score(np.array(pathology_true)[mask], 
                                                    np.array(pathology_preds)[mask])),
                    'precision': float(precision_score(np.array(pathology_true)[mask],
                                                      np.array(pathology_preds)[mask], 
                                                      average='weighted', zero_division=0)),
                }
        
        # Print results
        logger.info(f"\n{'─'*70}")
        logger.info(f"PATHOLOGY DETECTION")
        logger.info(f"{'─'*70}")
        logger.info(f"Accuracy:  {results['pathology']['accuracy']:.4f}")
        logger.info(f"Precision: {results['pathology']['precision']:.4f}")
        logger.info(f"Recall:    {results['pathology']['recall']:.4f}")
        logger.info(f"F1-Score:  {results['pathology']['f1']:.4f}")
        
        logger.info(f"\n{'─'*70}")
        logger.info(f"REGION CLASSIFICATION")
        logger.info(f"{'─'*70}")
        logger.info(f"Accuracy:  {results['region']['accuracy']:.4f}")
        logger.info(f"Precision: {results['region']['precision']:.4f}")
        logger.info(f"Recall:    {results['region']['recall']:.4f}")
        logger.info(f"F1-Score:  {results['region']['f1']:.4f}")
        
        logger.info(f"\n{'─'*70}")
        logger.info(f"SEVERITY ESTIMATION")
        logger.info(f"{'─'*70}")
        logger.info(f"MAE:  {results['severity']['mae']:.4f}")
        logger.info(f"RMSE: {results['severity']['rmse']:.4f}")
        logger.info(f"R²:   {results['severity']['r2']:.4f}")
        
        logger.info(f"\n{'─'*70}")
        logger.info(f"MODEL CONFIDENCE")
        logger.info(f"{'─'*70}")
        logger.info(f"Mean:       {results['confidence']['mean']:.4f}")
        logger.info(f"Std:        {results['confidence']['std']:.4f}")
        logger.info(f"Range:      {results['confidence']['min']:.4f} - {results['confidence']['max']:.4f}")
        
        self.results[split_name] = results
        return results
    
    def save_results(self, output_dir: Path = None):
        """Save evaluation results to JSON"""
        if output_dir is None:
            output_dir = Path('backend/ml/results')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = output_dir / f"phase4_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\n✓ Results saved to {results_file}")
        return results_file


def evaluate_phase4_model(model_path: str = 'backend/ml/models/dental_cnn_model_phase4.pth',
                         dataset_root: str = 'backend/ml/datasets/dental_images'):
    """
    Easy-to-use evaluation function
    
    Args:
        model_path: Path to trained model
        dataset_root: Root directory of dataset
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Using device: {device}")
    
    evaluator = Phase4ModelEvaluator(
        model_path=model_path,
        dataset_root=dataset_root,
        device=device
    )
    
    # Evaluate on all splits
    for split in ['train', 'val', 'test']:
        evaluator.evaluate_on_split(split)
    
    # Save results
    evaluator.save_results()
    
    return evaluator


if __name__ == '__main__':
    evaluate_phase4_model()
