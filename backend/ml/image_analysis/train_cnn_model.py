"""
Training Script for Dental Image Analysis CNN Model (Phase 4)
Trains ResNet50-based model for pathology detection
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import logging
from pathlib import Path
from typing import Optional, Tuple
import json

logger = logging.getLogger(__name__)


class DentalImageDataset(Dataset):
    """Dataset loader for dental radiographs"""
    
    def __init__(self, image_paths: list, labels: dict, preprocessor):
        self.image_paths = image_paths
        self.labels = labels
        self.preprocessor = preprocessor
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        from ml.image_analysis.preprocessing.image_loader import DentalImageLoader
        
        img_path = self.image_paths[idx]
        loader = DentalImageLoader()
        raw_image = loader.load_image(img_path)
        
        if raw_image is None:
            raise RuntimeError(f"Failed to load {img_path}")
        
        # Preprocess
        processed = self.preprocessor.preprocess_radiograph(raw_image)
        
        # Convert to tensor
        import torch
        tensor = torch.from_numpy(processed).permute(2, 0, 1).float()
        
        # Get labels
        label_dict = self.labels.get(Path(img_path).name, {})
        
        return {
            'image': tensor,
            'pathology': torch.tensor(label_dict.get('pathology', 0), dtype=torch.long),
            'region': torch.tensor(label_dict.get('region', 0), dtype=torch.long),
            'severity': torch.tensor(label_dict.get('severity', 0), dtype=torch.float32),
        }


def train_dental_cnn_model(model, train_loader, val_loader, 
                          device='cpu', num_epochs=10,
                          model_save_path='backend/ml/models/dental_cnn_model.pth'):
    """
    Train the dental image analysis CNN model
    
    Args:
        model: DentalCNNModel instance
        train_loader: Training DataLoader
        val_loader: Validation DataLoader
        device: Device to train on
        num_epochs: Number of training epochs
        model_save_path: Where to save trained model
    """
    
    # Loss functions
    pathology_loss = nn.CrossEntropyLoss()
    region_loss = nn.CrossEntropyLoss()
    severity_loss = nn.MSELoss()
    
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', 
                                                     factor=0.5, patience=3)
    
    best_val_loss = float('inf')
    training_history = {
        'train_loss': [],
        'val_loss': [],
        'train_accuracy': [],
        'val_accuracy': []
    }
    
    model = model.to(device)
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, batch in enumerate(train_loader):
            images = batch['image'].to(device)
            pathology_labels = batch['pathology'].to(device)
            region_labels = batch['region'].to(device)
            severity_labels = batch['severity'].to(device).unsqueeze(1)
            
            # Forward pass
            optimizer.zero_grad()
            predictions = model(images)
            
            # Calculate losses
            pathology_pred_loss = pathology_loss(predictions['pathology_logits'], pathology_labels)
            region_pred_loss = region_loss(predictions['region_logits'], region_labels)
            severity_pred_loss = severity_loss(predictions['severity'], severity_labels)
            
            # Combined loss (weighted)
            loss = 0.5 * pathology_pred_loss + 0.3 * region_pred_loss + 0.2 * severity_pred_loss
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += loss.item()
            
            # Calculate accuracy
            _, predicted = torch.max(predictions['pathology_logits'], 1)
            train_total += pathology_labels.size(0)
            train_correct += (predicted == pathology_labels).sum().item()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{num_epochs}, Batch {batch_idx+1}/{len(train_loader)}, "
                      f"Loss: {loss.item():.4f}")
        
        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = train_correct / train_total
        training_history['train_loss'].append(avg_train_loss)
        training_history['train_accuracy'].append(train_accuracy)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                images = batch['image'].to(device)
                pathology_labels = batch['pathology'].to(device)
                region_labels = batch['region'].to(device)
                severity_labels = batch['severity'].to(device).unsqueeze(1)
                
                predictions = model(images)
                
                pathology_pred_loss = pathology_loss(predictions['pathology_logits'], pathology_labels)
                region_pred_loss = region_loss(predictions['region_logits'], region_labels)
                severity_pred_loss = severity_loss(predictions['severity'], severity_labels)
                
                loss = 0.5 * pathology_pred_loss + 0.3 * region_pred_loss + 0.2 * severity_pred_loss
                val_loss += loss.item()
                
                _, predicted = torch.max(predictions['pathology_logits'], 1)
                val_total += pathology_labels.size(0)
                val_correct += (predicted == pathology_labels).sum().item()
        
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = val_correct / val_total
        training_history['val_loss'].append(avg_val_loss)
        training_history['val_accuracy'].append(val_accuracy)
        
        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"  Train Loss: {avg_train_loss:.4f}, Accuracy: {train_accuracy:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}, Accuracy: {val_accuracy:.4f}")
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_model(model_save_path)
            logger.info(f"Saved best model with val_loss: {best_val_loss:.4f}")
        
        # Adjust learning rate
        scheduler.step(avg_val_loss)
    
    # Save training history
    history_path = Path(model_save_path).parent / 'training_history.json'
    with open(history_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    
    logger.info(f"Training completed. Model saved to {model_save_path}")
    return model, training_history


if __name__ == '__main__':
    print("Dental Image Analysis Training Script")
    print("To train the model, provide your dataset and call train_dental_cnn_model()")
