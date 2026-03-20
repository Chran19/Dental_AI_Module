"""
Project C: Implant Model Evaluation & Feature Analysis (Week 6-7)
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, MODELS_DIR, RESULTS_DIR
from evaluation.evaluator import ImplantEvaluator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_implant_model():
    """Evaluate current implant model"""
    processed_dir = DATA_DIR / "processed"
    
    # Load data
    X_test = pd.read_csv(processed_dir / "implant_features_test.csv")
    y_test = pd.read_csv(processed_dir / "implant_target_test.csv")
    
    # Load model
    model = joblib.load(MODELS_DIR / "implant_cox_model.joblib")
    
    # Evaluate
    evaluator = ImplantEvaluator()
    results = evaluator.evaluate(model, X_test, y_test)
    
    # Save results
    evaluator.save_results(RESULTS_DIR, "implant_baseline_evaluation")
    
    return evaluator, results


def optimize_implant_features():
    """Feature selection and optimization for implant model"""
    processed_dir = DATA_DIR / "processed"
    
    # Load training data
    X_train = pd.read_csv(processed_dir / "implant_features_train.csv")
    y_train = pd.read_csv(processed_dir / "implant_target_train.csv")
    X_test = pd.read_csv(processed_dir / "implant_features_test.csv")
    y_test = pd.read_csv(processed_dir / "implant_target_test.csv")
    
    # Extract survival variables
    T_train = y_train['T'].values
    E_train = y_train['E'].values
    T_test = y_test['T'].values
    E_test = y_test['E'].values
    
    # Fit Cox model with all features
    cph_full = CoxPHFitter(penalizer=0.1)
    
    # Prepare data for lifelines (needs duration and event indicator)
    train_df = X_train.copy()
    train_df['T'] = T_train
    train_df['E'] = E_train
    
    logger.info("Fitting Cox model with feature penalization...")
    cph_full.fit(train_df, duration_col='T', event_col='E')
    
    # Get feature importances (absolute coefficient values)
    feature_importance = np.abs(cph_full.params_).sort_values(ascending=False)
    
    # Top features (those with highest absolute coefficients)
    top_n = min(15, len(feature_importance))
    top_features = feature_importance.head(top_n).index.tolist()
    
    logger.info(f"Top {top_n} features selected for implant model")
    
    # Evaluate on test set
    test_df = X_test.copy()
    test_df['T'] = T_test
    test_df['E'] = E_test
    
    partial_hazard_test = cph_full.predict_partial_hazard(X_test)
    c_index_full = concordance_index(T_test, partial_hazard_test, E_test)
    
    return {
        'model': cph_full,
        'feature_importance': feature_importance.to_dict(),
        'top_features': top_features,
        'concordance_index': float(c_index_full),
        'n_features': len(X_train.columns)
    }


def run_project_c():
    """Run Week 6-7 implant evaluation"""
    print("\n" + "="*70)
    print("PROJECT C: IMPLANT MODEL - EVALUATION & OPTIMIZATION (Week 6-7)")
    print("="*70 + "\n")
    
    # Baseline evaluation
    print("[1/2] Baseline Model Evaluation...")
    evaluator_base, results_base = evaluate_implant_model()
    print(f"  ✓ Baseline Concordance Index: {results_base['concordance_index']:.4f}")
    print(f"  ✓ Event Rate: {results_base['event_rate']*100:.2f}%")
    print(f"  ✓ Events: {results_base['n_events']}, Censored: {results_base['n_censored']}")
    
    # Feature optimization
    print("\n[2/2] Feature Selection & Optimization...")
    opt_results = optimize_implant_features()
    print(f"  ✓ Top 15 features selected from {opt_results['n_features']} total")
    print(f"  ✓ Optimized Concordance Index: {opt_results['concordance_index']:.4f}")
    
    top_5 = list(opt_results['feature_importance'].items())[:5]
    print(f"\n  Top 5 Features:")
    for feat, importance in top_5:
        print(f"    • {feat}: {importance:.4f}")
    
    print("\n" + "="*70)
    print("Project C Complete")
    print("="*70)
    
    return {
        'baseline': results_base,
        'optimization': opt_results
    }


if __name__ == "__main__":
    results = run_project_c()
