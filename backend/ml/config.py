"""
ML Configuration Module
Centralized configuration for all ML model training and inference
"""

import os
from pathlib import Path

# Base ML directory paths
ML_DIR = Path(__file__).parent
DATA_DIR = ML_DIR / "data"
MODELS_DIR = ML_DIR / "models"
TRAINING_DIR = ML_DIR / "training"
EVALUATION_DIR = ML_DIR / "evaluation"
RESULTS_DIR = ML_DIR / "results"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, TRAINING_DIR, EVALUATION_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Dataset paths (point to existing datasets)
DATASETS = {
    "diagnosis": ML_DIR / "datasets" / "diagnosis" / "diagnosis_dataset.csv",
    "treatment": ML_DIR / "datasets" / "treatment_outcomes" / "treatment_dataset.csv",
    "implant": ML_DIR / "datasets" / "implant" / "implant_dataset.csv",
}

# Processed data paths
PROCESSED_DATA = {
    "diagnosis_train": DATA_DIR / "processed" / "diagnosis_train.csv",
    "diagnosis_test": DATA_DIR / "processed" / "diagnosis_test.csv",
    "treatment_train": DATA_DIR / "processed" / "treatment_train.csv",
    "treatment_test": DATA_DIR / "processed" / "treatment_test.csv",
    "implant_train": DATA_DIR / "processed" / "implant_train.csv",
    "implant_test": DATA_DIR / "processed" / "implant_test.csv",
}

# Model paths
MODEL_PATHS = {
    "diagnosis": MODELS_DIR / "diagnosis_model.joblib",
    "diagnosis_preprocessor": MODELS_DIR / "diagnosis_preprocessor.joblib",
    "diagnosis_feature_cols": MODELS_DIR / "diagnosis_features.joblib",
    
    "treatment": MODELS_DIR / "treatment_model.joblib",
    "treatment_preprocessor": MODELS_DIR / "treatment_preprocessor.joblib",
    "treatment_feature_cols": MODELS_DIR / "treatment_features.joblib",
    
    "implant": MODELS_DIR / "implant_model.joblib",
    "implant_preprocessor": MODELS_DIR / "implant_preprocessor.joblib",
    "implant_feature_cols": MODELS_DIR / "implant_features.joblib",
}

# =============================================================================
# PROJECT A: DIAGNOSIS CLASSIFIER
# =============================================================================

DIAGNOSIS_CONFIG = {
    "name": "Diagnosis XGBoost Classifier",
    "target": "confirmed_diagnosis_1",  # Primary diagnosis
    "task_type": "multi-label",  # Can have multiple diagnoses
    
    # Dataset configuration
    "dataset_path": DATASETS["diagnosis"],
    "test_size": 0.15,
    "validation_size": 0.15,
    "random_state": 42,
    "stratify": True,  # Stratified split by diagnosis distribution
    
    # Features to use
    "numeric_features": [
        "age", "pain_level", "temperature_c", "probing_depth_mm",
        "symptom_onset_days", "duration_days"
    ],
    "categorical_features": [
        "gender", "smoking_status", "swelling_grade", "bleeding_on_probing",
        "tooth_mobility", "percussion_response", "vitality_response"
    ],
    "systemic_features": "systemic_conditions",  # Multi-hot encoded
    
    # Handling class imbalance
    "use_smote": True,
    "smote_sampling_strategy": "auto",  # SMOTE minority classes
    
    # XGBoost hyperparameters (to be tuned)
    "xgb_params": {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "objective": "multi:softprob",
        "num_class": 13,  # 13 diagnosis codes (DX-01 to DX-13)
        "eval_metric": "mlogloss",
        "tree_method": "hist",
        "device": "cpu",
    },
    
    # Cross-validation
    "cv_folds": 5,
    "cv_stratified": True,
    
    # Target metric for evaluation
    "target_metrics": {
        "f1_macro": 0.85,  # Target F1 ≥ 0.85
        "roc_auc": 0.88,
    },
    
    # Early stopping
    "early_stopping_rounds": 50,
    "eval_metric": "mlogloss",
}

# =============================================================================
# PROJECT B: TREATMENT OUTCOME PREDICTOR
# =============================================================================

TREATMENT_CONFIG = {
    "name": "Treatment Outcome XGBoost Classifier",
    "target": "outcome",  # Success, Partial, Failure, Complication
    "task_type": "multi-class",
    "classes": ["Success", "Partial", "Failure", "Complication"],
    "n_classes": 4,
    
    # Dataset configuration
    "dataset_path": DATASETS["treatment"],
    "test_size": 0.15,
    "validation_size": 0.15,
    "random_state": 42,
    "stratify": True,
    
    # Features to use
    "numeric_features": [
        "patient_age", "pre_treatment_pain", "pre_treatment_swelling",
        "treatment_duration_days", "follow_up_weeks"
    ],
    "categorical_features": [
        "diagnosis", "treatment_applied", "patient_gender", "smoking_status",
        "restoration_type"
    ],
    "systemic_features": "systemic_conditions",
    
    # Class weights (for imbalanced dataset)
    "use_class_weights": True,
    
    # XGBoost hyperparameters
    "xgb_params": {
        "n_estimators": 150,
        "max_depth": 5,
        "learning_rate": 0.03,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "objective": "multi:softprob",
        "num_class": 4,
        "eval_metric": "mlogloss",
        "tree_method": "hist",
        "device": "cpu",
    },
    
    # Cross-validation
    "cv_folds": 5,
    "cv_stratified": True,
    
    # Target metrics
    "target_metrics": {
        "accuracy": 0.80,  # Target accuracy ≥ 0.80
        "roc_auc": 0.85,
        "failure_recall": 0.70,  # Capture at least 70% of failures
    },
    
    # Early stopping
    "early_stopping_rounds": 50,
}

# =============================================================================
# PROJECT C: IMPLANT SURVIVAL PREDICTOR
# =============================================================================

IMPLANT_CONFIG = {
    "name": "Implant Survival Cox Proportional Hazards",
    "task_type": "survival",  # Survival analysis
    "time_column": "T",  # Time to event or censoring
    "event_column": "E",  # Event indicator (1=failure, 0=censored)
    
    # Dataset configuration
    "dataset_path": DATASETS["implant"],
    "test_size": 0.15,
    "random_state": 42,
    
    # Features for survival model
    "features": [
        # Patient factors
        "patient_age", "patient_gender", "smoking_status",
        # Bone characteristics
        "bone_height_mm", "bone_width_mm", "bone_density_hu", "bone_quality_type",
        # Implant specifications
        "implant_diameter_mm", "implant_length_mm", "implant_type", "implant_surface",
        # Surgical factors
        "jaw_location", "insertion_torque_ncm", "surgical_technique",
        # Clinical factors
        "osseointegration_months",
    ],
    
    # Cox model configuration
    "cox_params": {
        "penalizer": 0.1,  # Regularization
    },
    
    # Target metrics
    "target_metrics": {
        "concordance_index": 0.82,  # Target C-index ≥ 0.82
        "brier_score_at_12m": 0.20,
    },
    
    # Risk stratification
    "risk_groups": {
        "low": "< 33rd percentile of partial hazard",
        "medium": "33rd-67th percentile",
        "high": "> 67th percentile",
    },
    
    # Cross-validation
    "cv_folds": 5,
}

# =============================================================================
# BLENDING CONFIGURATION (Rules + ML)
# =============================================================================

BLENDING_CONFIG = {
    "enabled": True,
    "rule_weight": 0.60,  # 60% rules
    "ml_weight": 0.40,    # 40% ML
    "fallback_strategy": "rules",  # If ML fails, use rules only
    
    # M3 (Diagnosis) blending
    "diagnosis_blending": {
        "rule_weight": 0.60,
        "ml_weight": 0.40,
        "confidence_threshold": 0.5,  # Min confidence to use ML
    },
    
    # M5 (Treatment) blending
    "treatment_blending": {
        "rule_weight": 0.60,
        "ml_weight": 0.40,
        "confidence_threshold": 0.5,
    },
    
    # Risk engine integration
    "risk_blending": {
        "rule_weight": 0.70,
        "ml_weight": 0.30,
    },
}

# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

TRAINING_CONFIG = {
    "batch_size": 32,
    "epochs": 100,
    "random_state": 42,
    "n_jobs": -1,  # Use all CPUs
    "verbose": 1,
    
    # Feature scaling
    "scale_features": True,
    "scaler_type": "StandardScaler",  # Standardize to mean=0, std=1
    
    # Encoding
    "categorical_encoding": "onehot",  # one-hot encoding
    "multi_hot_encoding": True,  # For systemic conditions
    
    # Missing value handling
    "missing_value_strategy": {
        "numeric": "median",  # Impute with median
        "categorical": "most_frequent",  # Impute with mode
    },
    
    # Outlier handling
    "remove_outliers": False,  # Keep for clinical data
    "outlier_method": "iqr",  # IQR method if enabled
}

# =============================================================================
# INFERENCE CONFIGURATION
# =============================================================================

INFERENCE_CONFIG = {
    "batch_inference": True,
    "batch_size": 32,
    "cache_models": True,
    "model_cache_ttl": 3600,  # Cache for 1 hour
    
    # Uncertainty quantification
    "return_confidence": True,
    "confidence_method": "probability",
    
    # Diagnosis inference
    "diagnosis_threshold": 0.5,
    "return_top_n_diagnoses": 5,  # Return top 5 likely diagnoses
    
    # Treatment inference
    "treatment_threshold": 0.5,
    "return_top_n_options": 3,  # Return top 3 treatment options
    
    # Implant inference
    "survival_timepoints": [6, 12, 24, 36, 60],  # Months (0.5, 1, 2, 3, 5 years)
}

# =============================================================================
# LOGGING & MONITORING
# =============================================================================

LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_dir": ML_DIR / "logs",
    "log_predictions": True,
    "log_models_loaded": True,
    "log_inference_metrics": True,
}

# Create log directory
LOGGING_CONFIG["log_dir"].mkdir(parents=True, exist_ok=True)

# =============================================================================
# VALIDATION & TESTING
# =============================================================================

VALIDATION_CONFIG = {
    "enable_clinical_validation": True,
    "validation_rules": {
        "diagnosis_agreement": 0.75,  # 75% rule-ML agreement
        "treatment_agreement": 0.75,
        "unknown_confidence": 0.3,  # Flag if confidence < 30%
    },
    
    "test_configurations": {
        "unit_tests": True,
        "integration_tests": True,
        "clinical_validation": True,
        "performance_tests": True,
    },
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_config(project_name: str) -> dict:
    """
    Get configuration for a specific project
    
    Args:
        project_name: "diagnosis", "treatment", or "implant"
    
    Returns:
        Dictionary with project configuration
    """
    configs = {
        "diagnosis": DIAGNOSIS_CONFIG,
        "treatment": TREATMENT_CONFIG,
        "implant": IMPLANT_CONFIG,
    }
    
    if project_name not in configs:
        raise ValueError(f"Unknown project: {project_name}")
    
    return configs[project_name]


def ensure_directories():
    """Ensure all required directories exist"""
    for directory in [DATA_DIR, MODELS_DIR, TRAINING_DIR, EVALUATION_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print("ML Configuration Module")
    print(f"ML Directory: {ML_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Models Directory: {MODELS_DIR}")
    print(f"Training Directory: {TRAINING_DIR}")
    print(f"Evaluation Directory: {EVALUATION_DIR}")
    
    ensure_directories()
    print("✓ All directories created")
