"""
CNN Model for Dental Radiograph Analysis
Uses ResNet50 backbone with custom heads for pathology detection

Fixed Issues:
- Correct 6-class pathology mapping matching actual OPG dataset
- Proper ImageNet normalization built into forward pass
- Frozen backbone for transfer learning with small datasets
- BatchNorm + proper dropout in classification heads
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Tuple, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DentalCNNModel(nn.Module):
    """ResNet50-based CNN for dental image analysis"""
    
    # Corrected pathology classes matching actual OPG dataset
    PATHOLOGY_CLASSES = {
        0: 'Normal',           # Healthy Teeth (223 images)
        1: 'Caries',           # Caries (119 images)
        2: 'Impacted_Teeth',   # Impacted teeth (87 images) - was wrongly "Implant"
        3: 'Bone_Loss',        # BDC-BDR / Bone Loss (52 images)
        4: 'Infection',        # Infection / Periapical (23 images)
        5: 'Fracture',         # Fractured Teeth (13 images)
    }
    
    # Region classes (tooth location)
    REGION_CLASSES = {
        0: 'Anterior_Upper',
        1: 'Anterior_Lower',
        2: 'Premolar_Upper',
        3: 'Premolar_Lower',
        4: 'Molar_Upper',
        5: 'Molar_Lower'
    }

    # ImageNet normalization constants (CRITICAL for ResNet50)
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]
    
    def __init__(self, num_pathologies: int = 6, 
                 num_regions: int = 6,
                 pretrained: bool = True,
                 freeze_backbone: bool = True):
        """
        Initialize dental CNN model
        
        Args:
            num_pathologies: Number of pathology classes (6 for real OPG dataset)
            num_regions: Number of tooth region classes
            pretrained: Use ImageNet pretrained weights
            freeze_backbone: Freeze ResNet backbone layers (recommended for small datasets)
        """
        super(DentalCNNModel, self).__init__()
        
        self.num_pathologies = num_pathologies
        self.num_regions = num_regions
        
        # Load ResNet50 backbone with proper weights API
        if pretrained:
            weights = models.ResNet50_Weights.IMAGENET1K_V2
            self.backbone = models.resnet50(weights=weights)
        else:
            self.backbone = models.resnet50(weights=None)
        
        backbone_out_features = self.backbone.fc.in_features  # 2048
        
        # Remove original classification layer
        self.backbone.fc = nn.Identity()
        
        # Freeze backbone for transfer learning (critical for ~360 training images)
        if freeze_backbone:
            self._freeze_backbone()
        
        # Register ImageNet normalization as buffers (move with model to device)
        self.register_buffer('img_mean', torch.tensor(self.IMAGENET_MEAN).view(1, 3, 1, 1))
        self.register_buffer('img_std', torch.tensor(self.IMAGENET_STD).view(1, 3, 1, 1))
        
        # Pathology detection head (improved with BatchNorm)
        self.pathology_head = nn.Sequential(
            nn.Linear(backbone_out_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_pathologies)
        )
        
        # Region classification head
        self.region_head = nn.Sequential(
            nn.Linear(backbone_out_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_regions)
        )
        
        # Severity estimation head (0-10 scale)
        self.severity_head = nn.Sequential(
            nn.Linear(backbone_out_features, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Output between 0-1, scaled to 0-10 in forward
        )
        
        # Confidence score
        self.confidence_head = nn.Sequential(
            nn.Linear(backbone_out_features, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Confidence 0-1
        )
    
    def _freeze_backbone(self):
        """Freeze all backbone parameters for transfer learning"""
        for param in self.backbone.parameters():
            param.requires_grad = False
        logger.info("Backbone frozen for transfer learning")
    
    def unfreeze_backbone(self, unfreeze_from: str = 'layer3'):
        """
        Gradually unfreeze backbone layers for fine-tuning
        
        Args:
            unfreeze_from: Which layer to start unfreezing from
                'layer4' - only last ResNet block (safest)
                'layer3' - last 2 blocks
                'layer2' - last 3 blocks
                'all' - unfreeze everything
        """
        if unfreeze_from == 'all':
            for param in self.backbone.parameters():
                param.requires_grad = True
            logger.info("Full backbone unfrozen")
            return
        
        unfreeze = False
        for name, param in self.backbone.named_parameters():
            if unfreeze_from in name:
                unfreeze = True
            if unfreeze:
                param.requires_grad = True
        
        trainable = sum(p.numel() for p in self.backbone.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.backbone.parameters())
        logger.info(f"Unfrozen from {unfreeze_from}: {trainable:,}/{total:,} backbone params trainable")
    
    def _normalize_imagenet(self, x: torch.Tensor) -> torch.Tensor:
        """Apply ImageNet normalization to input tensor"""
        return (x - self.img_mean) / self.img_std
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor (B, 3, H, W) - expected in [0, 1] range
            
        Returns:
            Dictionary with predictions:
            - pathology_logits: (B, num_pathologies)
            - region_logits: (B, num_regions)
            - severity: (B, 1) - severity score 0-10
            - confidence: (B, 1) - confidence score 0-1
        """
        # Apply ImageNet normalization (critical for ResNet50 transfer learning)
        x = self._normalize_imagenet(x)
        
        # Extract features
        features = self.backbone(x)
        
        # Generate predictions
        return {
            'pathology_logits': self.pathology_head(features),
            'region_logits': self.region_head(features),
            'severity': self.severity_head(features) * 10,  # Scale to 0-10
            'confidence': self.confidence_head(features)
        }
    
    @staticmethod
    def get_pathology_name(class_id: int) -> str:
        """Get pathology class name"""
        return DentalCNNModel.PATHOLOGY_CLASSES.get(class_id, 'Unknown')
    
    @staticmethod
    def get_region_name(class_id: int) -> str:
        """Get region class name"""
        return DentalCNNModel.REGION_CLASSES.get(class_id, 'Unknown')
    
    def save_model(self, save_path: str):
        """Save model weights with metadata"""
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'num_pathologies': self.num_pathologies,
            'num_regions': self.num_regions,
            'pathology_classes': self.PATHOLOGY_CLASSES,
            'region_classes': self.REGION_CLASSES,
        }, save_path)
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, load_path: str, device: str = 'cpu'):
        """Load model weights"""
        checkpoint = torch.load(load_path, map_location=device, weights_only=False)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.load_state_dict(checkpoint)
        self.eval()
        logger.info(f"Model loaded from {load_path}")
    
    def save_config(self, save_path: str):
        """Save model configuration"""
        config = {
            'num_pathologies': self.num_pathologies,
            'num_regions': self.num_regions,
            'pathology_classes': self.PATHOLOGY_CLASSES,
            'region_classes': self.REGION_CLASSES,
            'model_type': 'ResNet50',
            'imagenet_mean': self.IMAGENET_MEAN,
            'imagenet_std': self.IMAGENET_STD,
        }
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Config saved to {save_path}")


def create_dental_cnn_model(device: str = 'cpu',
                           pretrained: bool = True,
                           freeze_backbone: bool = True) -> DentalCNNModel:
    """Factory function to create dental CNN model"""
    model = DentalCNNModel(pretrained=pretrained, freeze_backbone=freeze_backbone)
    model = model.to(device)
    return model
