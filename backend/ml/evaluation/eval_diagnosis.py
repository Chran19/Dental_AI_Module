"""
Project A: Diagnosis Model Evaluation & Hyperparameter Tuning (Week 6-7)
"""

import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, MODELS_DIR, RESULTS_DIR
from evaluation.evaluator import DiagnosisEvaluator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_diagnosis_model():
    """Evaluate current diagnosis model"""
    processed_dir = DATA_DIR / "processed"
    
    # Load data
    X_test = pd.read_csv(processed_dir / "diagnosis_features_test.csv")
    y_test = pd.read_csv(processed_dir / "diagnosis_target_test.csv")
    
    # Load model
    model = joblib.load(MODELS_DIR / "diagnosis_model.joblib")
    
    # Evaluate
    evaluator = DiagnosisEvaluator()
    results = evaluator.evaluate(model, X_test, y_test)
    
    # Save results
    evaluator.save_results(RESULTS_DIR, "diagnosis_baseline_evaluation")
    
    return evaluator, results


def tune_diagnosis_model():
    """Tune diagnosis model hyperparameters"""
    from sklearn.preprocessing import LabelEncoder
    processed_dir = DATA_DIR / "processed"
    
    # Load training data
    X_train = pd.read_csv(processed_dir / "diagnosis_features_train.csv")
    y_train_raw = pd.read_csv(processed_dir / "diagnosis_target_train.csv")
    X_test = pd.read_csv(processed_dir / "diagnosis_features_test.csv")
    y_test_raw = pd.read_csv(processed_dir / "diagnosis_target_test.csv")
    
    # Encode labels for each column (match training pipeline)
    y_train_encoded = y_train_raw.copy()
    y_test_encoded = y_test_raw.copy()
    
    for col in y_train_raw.columns:
        le = LabelEncoder()
        y_train_encoded[col] = le.fit_transform(y_train_raw[col].astype(str))
        y_test_encoded[col] = le.transform(y_test_raw[col].astype(str))
    
    # Tune
    evaluator = DiagnosisEvaluator()
    best_model, best_params, best_score = evaluator.hyperparameter_tune(
        X_train, y_train_encoded, cv=3  # Use cv=3 for faster tuning
    )
    
    # Make predictions and encode back for comparison
    y_pred = best_model.predict(X_test)
    
    # Calculate evaluation metrics on encoded labels
    from sklearn.metrics import accuracy_score
    exact_match = (y_pred == y_test_encoded.values).all(axis=1).mean()
    
    per_label_accuracy = {}
    for i, col in enumerate(y_test_encoded.columns):
        acc = accuracy_score(y_test_encoded.iloc[:, i], y_pred[:, i])
        per_label_accuracy[col.replace('_', ' ').title()] = float(acc)
    
    overall_accuracy = np.mean(list(per_label_accuracy.values()))
    
    results = {
        'exact_match_accuracy': float(exact_match),
        'overall_label_accuracy': float(overall_accuracy),
        'per_label_accuracy': per_label_accuracy,
        'n_samples': len(X_test),
        'n_features': X_test.shape[1],
        'n_labels': y_test_encoded.shape[1]
    }
    
    # Save tuned model
    joblib.dump(best_model, MODELS_DIR / "diagnosis_model_tuned.joblib")
    
    # Save tuning results
    evaluator.evaluation_results = results
    evaluator.evaluation_results['tuning_best_params'] = best_params
    evaluator.evaluation_results['tuning_cv_score'] = float(best_score)
    evaluator.save_results(RESULTS_DIR, "diagnosis_tuning_results")
    
    return best_model, best_params, results


def run_project_a():
    """Run Week 6-7 diagnosis evaluation"""
    print("\n" + "="*70)
    print("PROJECT A: DIAGNOSIS MODEL - EVALUATION & TUNING (Week 6-7)")
    print("="*70 + "\n")
    
    # Baseline evaluation
    print("[1/2] Baseline Model Evaluation...")
    evaluator_base, results_base = evaluate_diagnosis_model()
    print(f"  ✓ Baseline Exact Match: {results_base['exact_match_accuracy']:.4f}")
    print(f"  ✓ Baseline Label Accuracy: {results_base['overall_label_accuracy']:.4f}")
    
    # Hyperparameter tuning
    print("\n[2/2] Hyperparameter Tuning (GridSearchCV)...")
    best_model, best_params, results_tuned = tune_diagnosis_model()
    print(f"  ✓ Tuned Exact Match: {results_tuned['exact_match_accuracy']:.4f}")
    print(f"  ✓ Tuned Label Accuracy: {results_tuned['overall_label_accuracy']:.4f}")
    
    # Comparison
    improvement = (results_tuned['overall_label_accuracy'] - results_base['overall_label_accuracy']) * 100
    print(f"\n  Improvement: {improvement:+.2f}%")
    
    print("\n" + "="*70)
    print("Project A Complete")
    print("="*70)
    
    return {
        'baseline': results_base,
        'tuned': results_tuned,
        'best_params': best_params,
        'improvement': improvement
    }


if __name__ == "__main__":
    results = run_project_a()
