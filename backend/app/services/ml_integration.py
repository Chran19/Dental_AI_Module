"""
M3 Clinical Input Service - ML Integration
Enhanced with ML-based diagnosis predictions
Week 8-10: Service Integration
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ml.services.prediction_service import MLPredictionService, BlendedPredictionService
from ml.data.feature_engineering import DiagnosisFeatureEngineer
from ml.config import MODELS_DIR

logger = logging.getLogger(__name__)


class EnhancedClinicallInputService:
    """Enhanced clinical input service with ML integration"""
    
    def __init__(self):
        self.ml_service = MLPredictionService(MODELS_DIR)
        self.blended_service = BlendedPredictionService(
            self.ml_service,
            rule_weight=0.6,  # 60% rule-based
            ml_weight=0.4     # 40% ML
        )
        self.diagnosis_engineer = DiagnosisFeatureEngineer()
    
    def predict_diagnosis_with_ml(self, clinical_data: Dict) -> Dict:
        """
        Predict diagnosis combining rule-based + ML
        
        Args:
            clinical_data: Clinical input data from M3
            
        Returns:
            predictions: Dict with rule-based, ML, and blended predictions
        """
        # Rule-based diagnosis (existing M3 logic)
        rule_based_diagnosis = self._rule_based_diagnosis(clinical_data)
        
        # ML-based diagnosis
        try:
            # Convert to dataframe for feature engineering
            clinical_df = pd.DataFrame([clinical_data])
            
            # Engineer features
            engineered_features = self.diagnosis_engineer.create_features(clinical_df)
            
            # Get ML predictions
            ml_diagnosis = self.ml_service.predict_diagnosis(
                engineered_features,
                confidence=True
            )
            
            # Blend predictions
            blended = self.blended_service.blend_diagnosis(
                rule_based_diagnosis,
                ml_diagnosis[0],
                ml_diagnosis[1] if len(ml_diagnosis) > 1 else None
            )
            
            return {
                'status': 'success',
                'rule_based': rule_based_diagnosis,
                'ml_model': ml_diagnosis[0] if isinstance(ml_diagnosis, tuple) else ml_diagnosis,
                'blended': blended,
                'clinical_data': clinical_data
            }
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                'status': 'fallback',
                'rule_based': rule_based_diagnosis,
                'ml_model': None,
                'blended': None,
                'error': str(e)
            }
    
    def _rule_based_diagnosis(self, clinical_data: Dict) -> str:
        """Rule-based diagnosis logic (existing M3 implementation)"""
        pain_level = clinical_data.get('pain_level', 0)
        swelling = clinical_data.get('swelling_grade', 'None')
        fever = clinical_data.get('fever', 0)
        
        # Example rule-based logic (replace with actual M3 logic)
        if pain_level > 7 and swelling != 'None':
            return 'Severe_Periapical_Pathology'
        elif fever and pain_level > 5:
            return 'Acute_Pulpitis'
        else:
            return 'Moderate_Caries'


class EnhancedTreatmentService:
    """Enhanced treatment service with ML integration"""
    
    def __init__(self):
        self.ml_service = MLPredictionService(MODELS_DIR)
        self.blended_service = BlendedPredictionService(
            self.ml_service,
            rule_weight=0.6,
            ml_weight=0.4
        )
        from ml.data.feature_engineering import TreatmentFeatureEngineer
        self.treatment_engineer = TreatmentFeatureEngineer()
    
    def predict_outcome_with_ml(self, treatment_data: Dict) -> Dict:
        """
        Predict treatment outcome combining rule-based + ML
        
        Args:
            treatment_data: Treatment data from M5
            
        Returns:
            predictions: Dict with rule-based, ML, and blended predictions
        """
        # Rule-based outcome (existing M5 logic)
        rule_based_outcome = self._rule_based_outcome(treatment_data)
        
        # ML-based outcome
        try:
            treatment_df = pd.DataFrame([treatment_data])
            engineered_features = self.treatment_engineer.create_features(treatment_df)
            
            ml_outcome = self.ml_service.predict_treatment(
                engineered_features,
                confidence=True
            )
            
            blended = self.blended_service.blend_treatment(
                rule_based_outcome,
                ml_outcome[0] if isinstance(ml_outcome, tuple) else ml_outcome
            )
            
            return {
                'status': 'success',
                'rule_based': rule_based_outcome,
                'ml_model': ml_outcome[0] if isinstance(ml_outcome, tuple) else ml_outcome,
                'blended': blended,
                'treatment_data': treatment_data
            }
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                'status': 'fallback',
                'rule_based': rule_based_outcome,
                'ml_model': None,
                'blended': None,
                'error': str(e)
            }
    
    def _rule_based_outcome(self, treatment_data: Dict) -> str:
        """Rule-based outcome logic (existing M5 implementation)"""
        treatment_applied = treatment_data.get('treatment_applied', '')
        duration = treatment_data.get('treatment_duration_days', 0)
        
        # Example rule-based logic (replace with actual M5 logic)
        if duration > 14:
            return 'Success'
        elif duration > 7:
            return 'Partial'
        else:
            return 'Failure'


class EnhancedImplantService:
    """Enhanced implant service with ML integration"""
    
    def __init__(self):
        self.ml_service = MLPredictionService(MODELS_DIR)
        self.blended_service = BlendedPredictionService(
            self.ml_service,
            rule_weight=0.6,
            ml_weight=0.4
        )
        from ml.data.feature_engineering import ImplantFeatureEngineer
        self.implant_engineer = ImplantFeatureEngineer()
    
    def predict_survival_risk_with_ml(self, implant_data: Dict) -> Dict:
        """
        Predict implant survival risk combining rule-based + ML
        
        Args:
            implant_data: Implant data from M2
            
        Returns:
            predictions: Dict with rule-based, ML, and blended risk scores
        """
        # Rule-based risk (existing M2 logic)
        rule_based_risk = self._rule_based_risk(implant_data)
        
        # ML-based risk
        try:
            implant_df = pd.DataFrame([implant_data])
            engineered_features = self.implant_engineer.create_features(implant_df)
            
            hazard, risk_score = self.ml_service.predict_implant_survival(
                engineered_features
            )
            
            blended = self.blended_service.blend_implant(
                rule_based_risk,
                float(risk_score[0]) if len(risk_score) > 0 else risk_score
            )
            
            return {
                'status': 'success',
                'rule_based_risk': rule_based_risk,
                'ml_hazard': float(hazard[0]) if len(hazard) > 0 else hazard,
                'ml_risk_score': float(risk_score[0]) if len(risk_score) > 0 else risk_score,
                'blended': blended,
                'implant_data': implant_data
            }
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                'status': 'fallback',
                'rule_based_risk': rule_based_risk,
                'ml_hazard': None,
                'ml_risk_score': None,
                'blended': None,
                'error': str(e)
            }
    
    def _rule_based_risk(self, implant_data: Dict) -> float:
        """Rule-based risk calculation (existing M2 implementation)"""
        bone_quality = implant_data.get('bone_quality_score', 3)  # 1-4 scale
        insertion_torque = implant_data.get('insertion_torque_ncm', 30)
        patient_age = implant_data.get('patient_age', 50)
        
        # Simple rule-based risk (0-1 scale)
        risk = 0.5  # Baseline risk
        
        # Bone quality factor
        if bone_quality < 2:
            risk += 0.2
        
        # Insertion torque factor
        if insertion_torque < 20:
            risk += 0.15
        
        # Age factor
        if patient_age > 70:
            risk += 0.1
        
        return min(risk, 1.0)  # Cap at 1.0
