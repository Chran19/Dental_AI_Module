"""
Evaluation Framework for Phase 3 ML Models
Handles cross-validation, hyperparameter tuning, and metrics analysis
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_validate, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, roc_curve, auc, confusion_matrix,
                             classification_report)
from xgboost import XGBClassifier
from lifelines.utils import concordance_index
import joblib
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ModelEvaluator:
    """Base class for comprehensive model evaluation"""
    
    def __init__(self, name: str):
        self.name = name
        self.evaluation_results = {}
        self.best_params = {}
        self.best_score = None
        
    def cross_validate_model(self, model, X, y, cv=5, scoring=None):
        """Perform k-fold cross-validation"""
        logger.info(f"Running {cv}-fold cross-validation for {self.name}...")
        
        cv_results = cross_validate(
            model, X, y, 
            cv=cv, 
            scoring=scoring,
            return_train_score=True,
            n_jobs=-1
        )
        
        return cv_results
    
    def save_results(self, results_dir: Path, filename: str):
        """Save evaluation results to JSON"""
        results_dir.mkdir(parents=True, exist_ok=True)
        filepath = results_dir / f"{filename}.json"
        
        # Convert numpy types to python types for JSON serialization
        serializable_results = self._make_serializable(self.evaluation_results)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"✓ Results saved to {filepath}")
        return filepath
    
    def _make_serializable(self, obj):
        """Convert numpy types to native Python types"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(v) for v in obj]
        return obj


class DiagnosisEvaluator(ModelEvaluator):
    """Evaluation for multi-label diagnosis classifier"""
    
    def __init__(self):
        super().__init__("Diagnosis Classifier")
        self.label_names = ['diagnosis_1', 'diagnosis_2', 'diagnosis_3']
    
    def evaluate(self, model, X_test, y_test):
        """Comprehensive multi-label evaluation"""
        logger.info(f"\nEvaluating {self.name}...")
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Multi-label metrics
        exact_match = (y_pred == y_test.values).all(axis=1).mean()
        
        # Per-label accuracy
        per_label_accuracy = {}
        for i, label in enumerate(self.label_names):
            acc = accuracy_score(y_test.iloc[:, i], y_pred[:, i])
            per_label_accuracy[label] = float(acc)
        
        # Overall label accuracy (mean of all labels)
        label_accuracy = np.mean([per_label_accuracy[l] for l in self.label_names])
        
        self.evaluation_results = {
            'exact_match_accuracy': float(exact_match),
            'overall_label_accuracy': float(label_accuracy),
            'per_label_accuracy': per_label_accuracy,
            'n_samples': len(X_test),
            'n_features': X_test.shape[1],
            'n_labels': y_test.shape[1]
        }
        
        return self.evaluation_results
    
    def hyperparameter_tune(self, X_train, y_train, cv=5):
        """Tune XGBoost hyperparameters"""
        logger.info(f"Tuning hyperparameters for {self.name}...")
        
        param_grid = {
            'estimator__n_estimators': [100, 200, 300],
            'estimator__max_depth': [4, 6, 8],
            'estimator__learning_rate': [0.01, 0.05, 0.1],
            'estimator__min_child_weight': [1, 3, 5],
            'estimator__subsample': [0.7, 0.9, 1.0]
        }
        
        # Create base model
        from sklearn.multioutput import MultiOutputClassifier
        base_model = MultiOutputClassifier(
            XGBClassifier(random_state=42, verbosity=0)
        )
        
        # Grid search (using single core to avoid multiprocessing issues)
        grid = GridSearchCV(
            base_model, 
            param_grid,
            cv=cv,
            scoring='accuracy',
            n_jobs=1,
            verbose=1
        )
        
        grid.fit(X_train, y_train)
        
        self.best_params = grid.best_params_
        self.best_score = grid.best_score_
        
        logger.info(f"Best CV Score: {grid.best_score_:.4f}")
        logger.info(f"Best Parameters: {grid.best_params_}")
        
        return grid.best_estimator_, grid.best_params_, grid.best_score_


class TreatmentEvaluator(ModelEvaluator):
    """Evaluation for multi-class treatment outcome classifier"""
    
    def __init__(self):
        super().__init__("Treatment Classifier")
    
    def evaluate(self, model, X_test, y_test):
        """Comprehensive multi-class evaluation"""
        logger.info(f"\nEvaluating {self.name}...")
        
        y_pred = model.predict(X_test)
        
        # Classification metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics
        class_report = classification_report(
            y_test, y_pred, 
            output_dict=True,
            zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        self.evaluation_results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'per_class_metrics': class_report,
            'confusion_matrix': cm.tolist(),
            'n_samples': len(X_test),
            'n_features': X_test.shape[1],
            'n_classes': len(np.unique(y_test))
        }
        
        return self.evaluation_results
    
    def hyperparameter_tune(self, X_train, y_train, cv=5):
        """Tune XGBoost hyperparameters"""
        logger.info(f"Tuning hyperparameters for {self.name}...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.01, 0.05, 0.1],
            'min_child_weight': [1, 3, 5],
            'subsample': [0.7, 0.9, 1.0],
            'colsample_bytree': [0.7, 0.9, 1.0]
        }
        
        base_model = XGBClassifier(random_state=42, verbosity=0)
        
        # Use RandomizedSearch for faster tuning
        search = RandomizedSearchCV(
            base_model,
            param_grid,
            n_iter=20,
            cv=cv,
            scoring='accuracy',
            n_jobs=1,
            random_state=42,
            verbose=1
        )
        
        search.fit(X_train, y_train)
        
        self.best_params = search.best_params_
        self.best_score = search.best_score_
        
        logger.info(f"Best CV Score: {search.best_score_:.4f}")
        logger.info(f"Best Parameters: {search.best_params_}")
        
        return search.best_estimator_, search.best_params_, search.best_score_


class ImplantEvaluator(ModelEvaluator):
    """Evaluation for survival analysis implant model"""
    
    def __init__(self):
        super().__init__("Implant Survival Model")
    
    def evaluate(self, model, X_test, y_test):
        """Comprehensive survival analysis evaluation"""
        logger.info(f"\nEvaluating {self.name}...")
        
        # Extract survival time and event indicator
        T = y_test['T'].values
        E = y_test['E'].values
        
        # Get partial hazard predictions
        partial_hazard = model.predict_partial_hazard(X_test)
        
        # Calculate concordance index
        c_index = concordance_index(T, partial_hazard, E)
        
        # Event statistics
        n_events = E.sum()
        n_censored = len(E) - n_events
        event_rate = n_events / len(E)
        
        # Feature coefficients
        coeffs = model.params_.sort_values(key=abs, ascending=False)
        
        self.evaluation_results = {
            'concordance_index': float(c_index),
            'n_samples': len(X_test),
            'n_features': X_test.shape[1],
            'n_events': int(n_events),
            'n_censored': int(n_censored),
            'event_rate': float(event_rate),
            'top_features': {
                feat: {
                    'coefficient': float(coef),
                    'hazard_ratio': float(np.exp(coef))
                }
                for feat, coef in coeffs.head(10).items()
            }
        }
        
        return self.evaluation_results
