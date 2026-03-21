"""
Project A: Diagnosis XGBoost Multi-Label Classifier
Trains and evaluates the diagnosis prediction model for M3
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, roc_auc_score, classification_report
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR, DATA_DIR, DIAGNOSIS_CONFIG

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DiagnosisModelTrainer:
    """Train and evaluate diagnosis classifier"""
    
    def __init__(self):
        self.model = None
        self.config = DIAGNOSIS_CONFIG
        self.metrics = {}
        self.label_encoders = {}  # Store encoders for each diagnosis column
    
    def load_features(self):
        """Load engineered features"""
        processed_dir = DATA_DIR / "processed"
        
        X_train = pd.read_csv(processed_dir / "diagnosis_features_train.csv")
        X_test = pd.read_csv(processed_dir / "diagnosis_features_test.csv")
        y_train = pd.read_csv(processed_dir / "diagnosis_target_train.csv")
        y_test = pd.read_csv(processed_dir / "diagnosis_target_test.csv")
        
        # Remove any remaining object columns (non-numeric, non-label-encoded)
        object_cols = X_train.select_dtypes(include=['object']).columns
        if len(object_cols) > 0:
            logger.info(f"Dropping non-numeric columns: {list(object_cols)}")
            X_train = X_train.drop(columns=object_cols)
            X_test = X_test.drop(columns=object_cols)
        
        logger.info(f"Loaded diagnosis features: {X_train.shape}, {X_test.shape}")
        return X_train, X_test, y_train, y_test
    
    def encode_labels(self, y_train, y_test, fit=True):
        """Encode string diagnosis codes to integers"""
        y_train_encoded = y_train.copy()
        y_test_encoded = y_test.copy()
        
        for col in y_train.columns:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                y_train_encoded[col] = self.label_encoders[col].fit_transform(
                    y_train[col].astype(str)
                )
                y_test_encoded[col] = self.label_encoders[col].transform(
                    y_test[col].astype(str)
                )
            else:
                y_test_encoded[col] = self.label_encoders[col].transform(
                    y_test[col].astype(str)
                )
        
        return y_train_encoded, y_test_encoded
    
    def train(self, X_train, y_train):
        """Train XGBoost model with cross-validation"""
        logger.info("Training diagnosis model with cross-validation...")
        
        # Use One-vs-Rest multi-output strategy
        base_clf = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            device="cpu",
            verbosity=0
        )
        
        self.model = MultiOutputClassifier(base_clf, n_jobs=-1)
        self.model.fit(X_train, y_train)
        
        logger.info("✓ Model training complete")
        return self.model
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        logger.info("Evaluating model on test set...")
        
        y_pred = self.model.predict(X_test)
        
        # For multi-label classification with numeric values
        # Exact match accuracy: all labels must be correct
        exact_match = np.mean((y_test.values == y_pred).all(axis=1))
        
        # Per-label accuracy (average across all labels)
        label_acc = np.mean(y_test.values == y_pred)
        
        # Calculate fraction correct per label
        label_accuracies = []
        for i in range(y_test.shape[1]):
            acc_i = np.mean(y_test.iloc[:, i].values == y_pred[:, i])
            label_accuracies.append(acc_i)
        label_acc_avg = np.mean(label_accuracies)
        
        self.metrics = {
            'exact_match_accuracy': float(exact_match),
            'label_accuracy': float(label_acc),
            'label_accuracy_avg': float(label_acc_avg),
            'n_samples': len(X_test),
            'n_features': X_test.shape[1],
            'n_labels': y_test.shape[1],
        }
        
        logger.info(f"\nTest Set Results:")
        logger.info(f"  Exact Match Accuracy: {exact_match:.4f} (all labels correct)")
        logger.info(f"  Label Accuracy (overall): {label_acc:.4f}")
        logger.info(f"  Label Accuracy (averaged): {label_acc_avg:.4f}")
        
        # Per-label breakdown
        logger.info(f"\nPer-Label Accuracy:")
        for i, col in enumerate(y_test.columns):
            logger.info(f"  {col}: {label_accuracies[i]:.4f}")
        
        return y_pred
    
    def save_model(self):
        """Save trained model"""
        logger.info("Saving model...")
        
        model_path = MODELS_DIR / "diagnosis_model.joblib"
        joblib.dump(self.model, model_path)
        logger.info(f"✓ Model saved: {model_path}")


def run_project_a():
    """Execute Project A training pipeline"""
    print("\n" + "="*60)
    print("PROJECT A: DIAGNOSIS MODEL TRAINING (Week 3-4)")
    print("="*60 + "\n")
    
    trainer = DiagnosisModelTrainer()
    
    # Load features
    X_train, X_test, y_train, y_test = trainer.load_features()
    
    # Encode labels (diagnosis codes to integers)
    y_train_enc, y_test_enc = trainer.encode_labels(y_train, y_test, fit=True)
    
    logger.info(f"\nDataset Summary:")
    logger.info(f"  Train features: {X_train.shape}")
    logger.info(f"  Test features: {X_test.shape}")
    logger.info(f"  Target labels: {y_train_enc.shape[1]}")
    
    # Train model
    trainer.train(X_train, y_train_enc)
    
    # Evaluate (on encoded labels)
    y_pred = trainer.evaluate(X_test, y_test_enc)
    
    # Save
    trainer.save_model()
    
    print("\n" + "="*60)
    print("✓ PROJECT A COMPLETE")
    print("="*60)
    
    return trainer, trainer.metrics


if __name__ == "__main__":
    trainer, metrics = run_project_a()
    
    print(f"\nFinal Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
