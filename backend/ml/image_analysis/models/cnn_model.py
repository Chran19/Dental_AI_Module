"""
CNN Model for Dental Radiograph Analysis
Uses ResNet50 backbone with custom heads for pathology detection
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
    
    # Pathology classes detected
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
    
    # Region classes (tooth location)
    REGION_CLASSES = {
        0: 'Anterior_Upper',
        1: 'Anterior_Lower',
        2: 'Premolar_Upper',
        3: 'Premolar_Lower',
        4: 'Molar_Upper',
        5: 'Molar_Lower'
    }
    
    def __init__(self, num_pathologies: int = 8, 
                 num_regions: int = 6,
                 pretrained: bool = True):
        """
        Initialize dental CNN model
        
        Args:
            num_pathologies: Number of pathology classes
            num_regions: Number of tooth region classes
            pretrained: Use ImageNet pretrained weights
        """
        super(DentalCNNModel, self).__init__()
        
        self.num_pathologies = num_pathologies
        self.num_regions = num_regions
        
        # Load ResNet50 backbone
        self.backbone = models.resnet50(pretrained=pretrained)
        backbone_out_features = self.backbone.fc.in_features
        
        # Remove original classification layer
        self.backbone.fc = nn.Identity()
        
        # Pathology detection head
        self.pathology_head = nn.Sequential(
            nn.Linear(backbone_out_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_pathologies)
        )
        
        # Region classification head
        self.region_head = nn.Sequential(
            nn.Linear(backbone_out_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_regions)
        )
        
        # Severity estimation head (0-10 scale)
        self.severity_head = nn.Sequential(
            nn.Linear(backbone_out_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Output between 0-1
        )
        
        # Confidence score
        self.confidence_head = nn.Sequential(
            nn.Linear(backbone_out_features, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Confidence 0-1
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor (B, 3, 512, 512)
            
        Returns:
            Dictionary with predictions:
            - pathology_logits: (B, num_pathologies)
            - region_logits: (B, num_regions)
            - severity: (B, 1) - severity score 0-10
            - confidence: (B, 1) - confidence score 0-1
        """
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
        """Save model weights"""
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), save_path)
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, load_path: str, device: str = 'cpu'):
        """Load model weights"""
        self.load_state_dict(torch.load(load_path, map_location=device))
        self.eval()  # Set to evaluation mode
        logger.info(f"Model loaded from {load_path}")
    
    def save_config(self, save_path: str):
        """Save model configuration"""
        config = {
            'num_pathologies': self.num_pathologies,
            'num_regions': self.num_regions,
            'pathology_classes': self.PATHOLOGY_CLASSES,
            'region_classes': self.REGION_CLASSES,
            'model_type': 'ResNet50',
        }
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Config saved to {save_path}")


def create_dental_cnn_model(device: str = 'cpu',
                           pretrained: bool = True) -> DentalCNNModel:
    """Factory function to create dental CNN model"""
    model = DentalCNNModel(pretrained=pretrained)
    model = model.to(device)
    return model
