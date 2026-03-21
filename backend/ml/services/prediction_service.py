"""
ML Prediction Service Module
Provides unified interface for making ML predictions
Week 8-10: Service Integration
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from lifelines.utils import concordance_index
import logging

logger = logging.getLogger(__name__)


class MLPredictionService:
    """Unified ML prediction service for all 3 models"""
    
    def __init__(self, models_dir: Path):
        """Initialize prediction service with model paths"""
        self.models_dir = Path(models_dir)
        self.diagnosis_model = None
        self.treatment_model = None
        self.implant_model = None
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        try:
            self.diagnosis_model = joblib.load(self.models_dir / "diagnosis_model.joblib")
            logger.info("✓ Diagnosis model loaded")
        except Exception as e:
            logger.error(f"Failed to load diagnosis model: {e}")
        
        try:
            self.treatment_model = joblib.load(self.models_dir / "treatment_model.joblib")
            logger.info("✓ Treatment model loaded")
        except Exception as e:
            logger.error(f"Failed to load treatment model: {e}")
        
        try:
            self.implant_model = joblib.load(self.models_dir / "implant_cox_model.joblib")
            logger.info("✓ Implant model loaded")
        except Exception as e:
            logger.error(f"Failed to load implant model: {e}")
    
    def predict_diagnosis(self, features_df: pd.DataFrame, confidence=False):
        """
        Predict diagnosis (multi-label)
        
        Args:
            features_df: DataFrame with engineered features
            confidence: Whether to return prediction confidence
            
        Returns:
            diagnosis_predictions: Predicted diagnosis labels
        """
        if self.diagnosis_model is None:
            raise ValueError("Diagnosis model not loaded")
        
        predictions = self.diagnosis_model.predict(features_df)
        
        if confidence:
            # Get prediction probabilities if available
            try:
                probabilities = self.diagnosis_model.predict_proba(features_df)
                return predictions, probabilities
            except:
                return predictions, None
        
        return predictions
    
    def predict_treatment(self, features_df: pd.DataFrame, confidence=False):
        """
        Predict treatment outcome (multi-class)
        
        Args:
            features_df: DataFrame with engineered features
            confidence: Whether to return prediction confidence
            
        Returns:
            outcome_predictions: Predicted treatment outcomes
        """
        if self.treatment_model is None:
            raise ValueError("Treatment model not loaded")
        
        predictions = self.treatment_model.predict(features_df)
        
        if confidence:
            try:
                probabilities = self.treatment_model.predict_proba(features_df)
                return predictions, probabilities
            except:
                return predictions, None
        
        return predictions
    
    def predict_implant_survival(self, features_df: pd.DataFrame):
        """
        Predict implant survival (hazard/risk)
        
        Args:
            features_df: DataFrame with engineered features
            
        Returns:
            hazard_predictions: Partial hazard predictions
            risk_scores: Risk scores (higher = higher risk)
        """
        if self.implant_model is None:
            raise ValueError("Implant model not loaded")
        
        # Get partial hazard (lower = better survival)
        partial_hazard = self.implant_model.predict_partial_hazard(features_df)
        
        # Convert to risk score (1 - survival probability approximation)
        # Normalize hazards to 0-1 scale for risk score
        risk_score = partial_hazard / (partial_hazard.max() + 1e-6)
        
        return partial_hazard, risk_score
    
    def predict_all(self, clinical_data_df: pd.DataFrame, 
                   feature_engineers: dict = None):
        """
        Make predictions for all 3 models given raw clinical data
        
        Args:
            clinical_data_df: Raw clinical data
            feature_engineers: Dict of feature engineers for each model
            
        Returns:
            predictions: Dict with predictions from all models
        """
        predictions = {}
        
        # If feature engineers provided, engineer features first
        if feature_engineers:
            if 'diagnosis' in feature_engineers:
                diag_features = feature_engineers['diagnosis'].create_features(
                    clinical_data_df
                )
                predictions['diagnosis'] = self.predict_diagnosis(diag_features)
            
            if 'treatment' in feature_engineers:
                treat_features = feature_engineers['treatment'].create_features(
                    clinical_data_df
                )
                predictions['treatment'] = self.predict_treatment(treat_features)
            
            if 'implant' in feature_engineers:
                impl_features = feature_engineers['implant'].create_features(
                    clinical_data_df
                )
                hazard, risk = self.predict_implant_survival(impl_features)
                predictions['implant'] = {'hazard': hazard, 'risk': risk}
        
        return predictions


class BlendedPredictionService:
    """Blended predictions combining rule-based + ML predictions"""
    
    def __init__(self, ml_service: MLPredictionService, 
                 rule_weight: float = 0.6, ml_weight: float = 0.4):
        """
        Initialize blended service
        
        Args:
            ml_service: ML prediction service
            rule_weight: Weight for rule-based predictions (0-1)
            ml_weight: Weight for ML predictions (0-1)
        """
        self.ml_service = ml_service
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        
        if abs((rule_weight + ml_weight) - 1.0) > 0.01:
            raise ValueError("rule_weight + ml_weight must sum to 1.0")
    
    def blend_diagnosis(self, rule_pred, ml_pred, confidence_scores=None):
        """
        Blend rule-based and ML diagnosis predictions
        
        Args:
            rule_pred: Rule-based diagnosis predictions
            ml_pred: ML model diagnosis predictions
            confidence_scores: ML confidence scores (optional)
            
        Returns:
            blended_pred: Blended diagnosis prediction
        """
        # Simple voting blend for multi-label
        # Weight by configured weights
        blended = {
            'rule_based': rule_pred,
            'ml_model': ml_pred,
            'blend_weight_rule': self.rule_weight,
            'blend_weight_ml': self.ml_weight,
            'confidence': confidence_scores
        }
        return blended
    
    def blend_treatment(self, rule_pred, ml_pred):
        """
        Blend rule-based and ML treatment predictions
        
        Args:
            rule_pred: Rule-based treatment predictions
            ml_pred: ML model treatment predictions
            
        Returns:
            blended_pred: Blended treatment prediction
        """
        blended = {
            'rule_based': rule_pred,
            'ml_model': ml_pred,
            'blend_weight_rule': self.rule_weight,
            'blend_weight_ml': self.ml_weight
        }
        return blended
    
    def blend_implant(self, rule_risk, ml_risk):
        """
        Blend rule-based and ML implant risk predictions
        
        Args:
            rule_risk: Rule-based implant risk score
            ml_risk: ML model implant risk score
            
        Returns:
            blended_risk: Blended risk score
        """
        # Weighted average of risk scores
        blended_risk = self.rule_weight * rule_risk + self.ml_weight * ml_risk
        
        blended = {
            'rule_based_risk': rule_risk,
            'ml_model_risk': ml_risk,
            'blended_risk': blended_risk,
            'blend_weight_rule': self.rule_weight,
            'blend_weight_ml': self.ml_weight
        }
        return blended
