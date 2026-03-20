"""
Project B: Treatment Model Evaluation & Hyperparameter Tuning (Week 6-7)
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, MODELS_DIR, RESULTS_DIR
from evaluation.evaluator import TreatmentEvaluator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_treatment_model():
    """Evaluate current treatment model"""
    processed_dir = DATA_DIR / "processed"
    
    # Load data
    X_test = pd.read_csv(processed_dir / "treatment_features_test.csv")
    y_test = pd.read_csv(processed_dir / "treatment_target_test.csv").squeeze()
    
    # Load model
    model = joblib.load(MODELS_DIR / "treatment_model.joblib")
    
    # Evaluate
    evaluator = TreatmentEvaluator()
    results = evaluator.evaluate(model, X_test, y_test)
    
    # Save results
    evaluator.save_results(RESULTS_DIR, "treatment_baseline_evaluation")
    
    return evaluator, results


def tune_treatment_model():
    """Tune treatment model hyperparameters with class weight balancing"""
    processed_dir = DATA_DIR / "processed"
    
    # Load training data
    X_train = pd.read_csv(processed_dir / "treatment_features_train.csv")
    y_train = pd.read_csv(processed_dir / "treatment_target_train.csv").squeeze()
    X_test = pd.read_csv(processed_dir / "treatment_features_test.csv")
    y_test = pd.read_csv(processed_dir / "treatment_target_test.csv").squeeze()
    
    # Tune
    evaluator = TreatmentEvaluator()
    best_model, best_params, best_score = evaluator.hyperparameter_tune(
        X_train, y_train, cv=5
    )
    
    # Evaluate tuned model
    results = evaluator.evaluate(best_model, X_test, y_test)
    
    # Save tuned model
    joblib.dump(best_model, MODELS_DIR / "treatment_model_tuned.joblib")
    
    # Save tuning results
    evaluator.evaluation_results['tuning_best_params'] = best_params
    evaluator.evaluation_results['tuning_cv_score'] = float(best_score)
    evaluator.save_results(RESULTS_DIR, "treatment_tuning_results")
    
    return best_model, best_params, results


def run_project_b():
    """Run Week 6-7 treatment evaluation"""
    print("\n" + "="*70)
    print("PROJECT B: TREATMENT MODEL - EVALUATION & TUNING (Week 6-7)")
    print("="*70 + "\n")
    
    # Baseline evaluation
    print("[1/2] Baseline Model Evaluation...")
    evaluator_base, results_base = evaluate_treatment_model()
    print(f"  ✓ Baseline Accuracy: {results_base['accuracy']:.4f}")
    print(f"  ✓ Baseline Precision: {results_base['precision']:.4f}")
    print(f"  ✓ Baseline F1-Score: {results_base['f1_score']:.4f}")
    
    # Hyperparameter tuning
    print("\n[2/2] Hyperparameter Tuning (RandomizedSearchCV)...")
    best_model, best_params, results_tuned = tune_treatment_model()
    print(f"  ✓ Tuned Accuracy: {results_tuned['accuracy']:.4f}")
    print(f"  ✓ Tuned Precision: {results_tuned['precision']:.4f}")
    print(f"  ✓ Tuned F1-Score: {results_tuned['f1_score']:.4f}")
    
    # Comparison
    improvement = (results_tuned['accuracy'] - results_base['accuracy']) * 100
    print(f"\n  Accuracy Improvement: {improvement:+.2f}%")
    
    print("\n" + "="*70)
    print("Project B Complete")
    print("="*70)
    
    return {
        'baseline': results_base,
        'tuned': results_tuned,
        'best_params': best_params,
        'improvement': improvement
    }


if __name__ == "__main__":
    results = run_project_b()
