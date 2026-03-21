"""
Project B: Treatment Outcome XGBoost Classifier  
Trains and evaluates treatment outcome predictor for M5
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR, DATA_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TreatmentModelTrainer:
    """Train and evaluate treatment outcome classifier"""
    
    def __init__(self):
        self.model = None
        self.metrics = {}
        self.label_encoder = None
    
    def load_features(self):
        """Load engineered features"""
        processed_dir = DATA_DIR / "processed"
        
        X_train = pd.read_csv(processed_dir / "treatment_features_train.csv")
        X_test = pd.read_csv(processed_dir / "treatment_features_test.csv")
        y_train = pd.read_csv(processed_dir / "treatment_target_train.csv").squeeze()
        y_test = pd.read_csv(processed_dir / "treatment_target_test.csv").squeeze()
        
        # Remove object columns
        object_cols = X_train.select_dtypes(include=['object']).columns
        if len(object_cols) > 0:
            logger.info(f"Dropping object columns: {list(object_cols)}")
            X_train = X_train.drop(columns=object_cols)
            X_test = X_test.drop(columns=object_cols)
        
        logger.info(f"Loaded treatment features: {X_train.shape}, {X_test.shape}")
        return X_train, X_test, y_train, y_test
    
    def encode_target(self, y_train, y_test, fit=True):
        """Encode outcome labels to integers"""
        if fit:
            self.label_encoder = LabelEncoder()
            y_train_enc = self.label_encoder.fit_transform(y_train.astype(str))
            y_test_enc = self.label_encoder.transform(y_test.astype(str))
        else:
            y_test_enc = self.label_encoder.transform(y_test.astype(str))
        
        return y_train_enc, y_test_enc
    
    def train(self, X_train, y_train):
        """Train XGBoost multi-class classifier"""
        logger.info("Training treatment outcome model...")
        
        self.model = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            objective="multi:softprob",
            num_class=len(np.unique(y_train)),
            eval_metric="mlogloss",
            tree_method="hist",
            device="cpu",
            verbosity=0
        )
        
        self.model.fit(X_train, y_train)
        logger.info("✓ Model training complete")
        return self.model
    
    def evaluate(self, X_test, y_test, y_test_enc):
        """Evaluate model"""
        logger.info("Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test_enc, y_pred)
        precision = precision_score(y_test_enc, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test_enc, y_pred, average='weighted', zero_division=0)
        
        self.metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'n_samples': len(X_test),
            'n_features': X_test.shape[1],
        }
        
        logger.info(f"\nTest Set Results:")
        logger.info(f"  Accuracy: {accuracy:.4f} (target: ≥ 0.80)")
        logger.info(f"  Precision (weighted): {precision:.4f}")
        logger.info(f"  Recall (weighted): {recall:.4f}")
        
        # Per-class breakdown
        logger.info(f"\nPer-Class Metrics:")
        for i, cls in enumerate(self.label_encoder.classes_):
            class_mask = y_test_enc == i
            if class_mask.sum() > 0:
                acc_i = accuracy_score(y_test_enc[class_mask], y_pred[class_mask])
                logger.info(f"  {cls}: accuracy={acc_i:.4f}, n={class_mask.sum()}")
        
        return y_pred
    
    def save_model(self):
        """Save trained model"""
        logger.info("Saving model...")
        
        model_path = MODELS_DIR / "treatment_model.joblib"
        joblib.dump(self.model, model_path)
        logger.info(f"✓ Model saved: {model_path}")


def run_project_b():
    """Execute Project B training"""
    print("\n" + "="*60)
    print("PROJECT B: TREATMENT OUTCOME MODEL (Week 4-5)")
    print("="*60 + "\n")
    
    trainer = TreatmentModelTrainer()
    
    # Load features
    X_train, X_test, y_train, y_test = trainer.load_features()
    y_train_enc, y_test_enc = trainer.encode_target(y_train, y_test, fit=True)
    
    logger.info(f"\nDataset Summary:")
    logger.info(f"  Train: {X_train.shape}")
    logger.info(f"  Test: {X_test.shape}")
    logger.info(f"  Classes: {trainer.label_encoder.classes_}")
    
    # Train and evaluate
    trainer.train(X_train, y_train_enc)
    trainer.evaluate(X_test, y_test, y_test_enc)
    trainer.save_model()
    
    print("\n" + "="*60)
    print("✓ PROJECT B COMPLETE")
    print("="*60)
    
    return trainer, trainer.metrics


if __name__ == "__main__":
    trainer, metrics = run_project_b()
    print(f"\nFinal Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
