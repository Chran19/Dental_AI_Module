"""
Feature Engineering Module for All 3 ML Projects
Transforms raw clinical data into ML-ready features
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, DIAGNOSIS_CONFIG, TREATMENT_CONFIG, IMPLANT_CONFIG

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Base class for feature engineering"""
    
    def __init__(self, name: str):
        self.name = name
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def encode_categorical(self, X: pd.DataFrame, cat_cols: list, fit=True):
        """One-hot encode categorical features"""
        X_encoded = X.copy()
        
        for col in cat_cols:
            if col in X_encoded.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    X_encoded[col] = self.label_encoders[col].fit_transform(X_encoded[col].astype(str))
                else:
                    X_encoded[col] = self.label_encoders[col].transform(X_encoded[col].astype(str))
        
        return X_encoded
    
    def scale_numeric(self, X: pd.DataFrame, numeric_cols: list, fit=True):
        """Standardize numeric features"""
        X_scaled = X.copy()
        
        if fit:
            X_scaled[numeric_cols] = self.scaler.fit_transform(X[numeric_cols])
        else:
            X_scaled[numeric_cols] = self.scaler.transform(X[numeric_cols])
        
        return X_scaled


class DiagnosisFeatureEngineer(FeatureEngineer):
    """Feature engineering for diagnosis prediction"""
    
    def __init__(self):
        super().__init__("Diagnosis")
    
    def create_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create diagnosis-specific features"""
        X_feat = X.copy()
        
        # 1. Interaction Features
        if 'pain_level' in X_feat.columns and 'swelling_grade' in X_feat.columns:
            # Convert swelling_grade to numeric if needed
            swelling_map = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
            swelling_numeric = X_feat['swelling_grade'].map(swelling_map).fillna(0)
            X_feat['pain_swelling_interaction'] = X_feat['pain_level'] * swelling_numeric
        
        # 2. Pattern Features
        if 'percussion_response' in X_feat.columns and 'vitality_response' in X_feat.columns:
            X_feat['periapical_signs'] = (
                ((X_feat['percussion_response'] == 'high_pitch') | (X_feat['percussion_response'] == 'painful')) &
                (X_feat['vitality_response'] == 'nonvital')
            ).astype(int)
        
        if 'probing_depth_mm' in X_feat.columns and 'bleeding_on_probing' in X_feat.columns:
            X_feat['periodontal_pattern'] = (
                (X_feat['probing_depth_mm'] > 4) &
                (X_feat['bleeding_on_probing'] == 1)
            ).astype(int)
        
        # 3. Temporal Features
        if 'symptom_onset_days' in X_feat.columns:
            X_feat['acute_onset'] = (X_feat['symptom_onset_days'] <= 7).astype(int)
            X_feat['log_onset_days'] = np.log1p(X_feat['symptom_onset_days'])
        
        if 'duration_days' in X_feat.columns:
            X_feat['chronic_presentation'] = (X_feat['duration_days'] > 30).astype(int)
            X_feat['log_duration_days'] = np.log1p(X_feat['duration_days'])
        
        # 4. Risk Profile Features
        if 'age' in X_feat.columns:
            X_feat['advanced_age'] = (X_feat['age'] > 65).astype(int)
        
        # 5. Fever + Systemic interaction
        if 'fever' in X_feat.columns and 'systemic_conditions' in X_feat.columns:
            X_feat['fever_systemic_interaction'] = (
                (X_feat['fever'] == 1) & 
                (X_feat['systemic_conditions'].notna())
            ).astype(int)
        
        return X_feat
    
    def process(self, train_path: str, test_path: str) -> tuple:
        """Full feature engineering pipeline"""
        logger.info(f"Processing diagnosis features from {train_path}")
        
        X_train = pd.read_csv(train_path)
        X_test = pd.read_csv(test_path)
        
        # Separate features and target
        y_train = X_train[['confirmed_diagnosis_1', 'confirmed_diagnosis_2', 'confirmed_diagnosis_3']]
        X_train = X_train.drop(columns=['case_id'] + list(y_train.columns), errors='ignore')
        
        y_test = X_test[['confirmed_diagnosis_1', 'confirmed_diagnosis_2', 'confirmed_diagnosis_3']]
        X_test = X_test.drop(columns=['case_id'] + list(y_test.columns), errors='ignore')
        
        # Create features
        X_train_feat = self.create_features(X_train)
        X_test_feat = self.create_features(X_test)
        
        # Encode categorical
        cat_cols = ['gender', 'swelling_grade', 'tooth_mobility', 'percussion_response', 'vitality_response', 'smoking_status']
        X_train_feat = self.encode_categorical(X_train_feat, cat_cols, fit=True)
        X_test_feat = self.encode_categorical(X_test_feat, cat_cols, fit=False)
        
        # Scale numeric
        numeric_cols = [col for col in X_train_feat.select_dtypes(include=[np.number]).columns]
        X_train_feat = self.scale_numeric(X_train_feat, numeric_cols, fit=True)
        X_test_feat = self.scale_numeric(X_test_feat, numeric_cols, fit=False)
        
        # Drop any remaining object columns (unmapped categoricals)
        object_cols = X_train_feat.select_dtypes(include=['object']).columns.tolist()
        if object_cols:
            logger.info(f"Dropping unmapped categorical columns: {object_cols}")
            X_train_feat = X_train_feat.drop(columns=object_cols)
            X_test_feat = X_test_feat.drop(columns=object_cols)
        
        logger.info(f"✓ Diagnosis features: {X_train_feat.shape[1]} features created")
        logger.info(f"  Train: {X_train_feat.shape[0]} samples")
        logger.info(f"  Test: {X_test_feat.shape[0]} samples")
        
        return X_train_feat, X_test_feat, y_train, y_test


class TreatmentFeatureEngineer(FeatureEngineer):
    """Feature engineering for treatment outcome prediction"""
    
    def __init__(self):
        super().__init__("Treatment")
    
    def create_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create treatment-specific features"""
        X_feat = X.copy()
        
        # 1. Diagnosis complexity (simple scoring)
        if 'diagnosis' in X_feat.columns:
            diagnosis_complexity = {
                'Caries': 1, 'Gingivitis': 1, 'Periodontitis': 2,
                'Pulpitis': 3, 'Periapical_Abscess': 3, 'Pulp_Necrosis': 2
            }
            X_feat['diagnosis_complexity'] = X_feat['diagnosis'].map(diagnosis_complexity).fillna(1)
        
        # 2. Systemic burden (count of conditions)
        if 'systemic_conditions' in X_feat.columns:
            X_feat['systemic_burden'] = X_feat['systemic_conditions'].apply(
                lambda x: len(str(x).split('|')) if pd.notna(x) and str(x) != 'None' else 0
            )
        
        # 3. Pre-treatment severity (pain + swelling combo)
        if 'pre_treatment_pain' in X_feat.columns and 'pre_treatment_swelling' in X_feat.columns:
            X_feat['pre_treatment_severity'] = X_feat['pre_treatment_pain'] + X_feat['pre_treatment_swelling']
        
        # 4. Patient risk profile
        if 'patient_age' in X_feat.columns and 'smoking_status' in X_feat.columns:
            X_feat['patient_risk'] = (X_feat['patient_age'] > 60).astype(int)
        
        return X_feat
    
    def process(self, train_path: str, test_path: str) -> tuple:
        """Full feature engineering pipeline"""
        logger.info(f"Processing treatment features from {train_path}")
        
        X_train = pd.read_csv(train_path)
        X_test = pd.read_csv(test_path)
        
        # Separate features and target
        y_train = X_train['outcome']
        X_train = X_train.drop(columns=['case_id', 'outcome'], errors='ignore')
        
        y_test = X_test['outcome']
        X_test = X_test.drop(columns=['case_id', 'outcome'], errors='ignore')
        
        # Create features
        X_train_feat = self.create_features(X_train)
        X_test_feat = self.create_features(X_test)
        
        # Encode categorical
        cat_cols = ['diagnosis', 'treatment_applied', 'patient_gender', 'smoking_status', 'restoration_type', 'allergy_history']
        X_train_feat = self.encode_categorical(X_train_feat, cat_cols, fit=True)
        X_test_feat = self.encode_categorical(X_test_feat, cat_cols, fit=False)
        
        # Scale numeric
        numeric_cols = [col for col in X_train_feat.select_dtypes(include=[np.number]).columns]
        X_train_feat = self.scale_numeric(X_train_feat, numeric_cols, fit=True)
        X_test_feat = self.scale_numeric(X_test_feat, numeric_cols, fit=False)
        
        # Drop any remaining object columns (unmapped categoricals)
        object_cols = X_train_feat.select_dtypes(include=['object']).columns.tolist()
        if object_cols:
            logger.info(f"Dropping unmapped categorical columns: {object_cols}")
            X_train_feat = X_train_feat.drop(columns=object_cols)
            X_test_feat = X_test_feat.drop(columns=object_cols)
        
        logger.info(f"✓ Treatment features: {X_train_feat.shape[1]} features created")
        logger.info(f"  Train: {X_train_feat.shape[0]} samples")
        logger.info(f"  Test: {X_test_feat.shape[0]} samples")
        
        return X_train_feat, X_test_feat, y_train, y_test


class ImplantFeatureEngineer(FeatureEngineer):
    """Feature engineering for implant survival prediction"""
    
    def __init__(self):
        super().__init__("Implant")
    
    def create_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create implant-specific features"""
        X_feat = X.copy()
        
        # 1. Bone Quality Score
        if 'bone_quality_type' in X_feat.columns:
            bone_quality_map = {'Type1': 1, 'Type2': 2, 'Type3': 3, 'Type4': 4}
            X_feat['bone_quality_score'] = X_feat['bone_quality_type'].map(bone_quality_map).fillna(2)
        
        # 2. Bone metrics ratios
        if 'bone_height_mm' in X_feat.columns and 'bone_width_mm' in X_feat.columns:
            X_feat['bone_height_width_ratio'] = X_feat['bone_height_mm'] / (X_feat['bone_width_mm'] + 0.001)
        
        # 3. Implant stability (torque ratio)
        if 'insertion_torque_ncm' in X_feat.columns and 'implant_diameter_mm' in X_feat.columns:
            X_feat['implant_stability_ratio'] = X_feat['insertion_torque_ncm'] / (X_feat['implant_diameter_mm'] * 10 + 0.001)
        
        # 4. Bone adequacy indicators
        if 'bone_height_mm' in X_feat.columns:
            X_feat['adequate_height'] = (X_feat['bone_height_mm'] >= 10).astype(int)
        
        if 'bone_width_mm' in X_feat.columns:
            X_feat['adequate_width'] = (X_feat['bone_width_mm'] >= 6).astype(int)
        
        # 5. Patient risk (age + smoking + conditions)
        if 'patient_age' in X_feat.columns:
            X_feat['advanced_age_risk'] = (X_feat['patient_age'] > 60).astype(int)
        
        return X_feat
    
    def process(self, train_path: str, test_path: str) -> tuple:
        """Full feature engineering pipeline for survival analysis"""
        logger.info(f"Processing implant features from {train_path}")
        
        X_train = pd.read_csv(train_path)
        X_test = pd.read_csv(test_path)
        
        # Keep T, E for survival analysis
        y_train = X_train[['T', 'E', 'outcome']]
        X_train = X_train.drop(columns=['implant_id', 'outcome', 'T', 'E'], errors='ignore')
        
        y_test = X_test[['T', 'E', 'outcome']]
        X_test = X_test.drop(columns=['implant_id', 'outcome', 'T', 'E'], errors='ignore')
        
        # Create features
        X_train_feat = self.create_features(X_train)
        X_test_feat = self.create_features(X_test)
        
        # Encode categorical
        cat_cols = ['patient_gender', 'smoking_status', 'bone_quality_type', 'implant_type', 'implant_surface', 'jaw_location', 'surgical_technique']
        X_train_feat = self.encode_categorical(X_train_feat, cat_cols, fit=True)
        X_test_feat = self.encode_categorical(X_test_feat, cat_cols, fit=False)
        
        # Scale numeric
        numeric_cols = [col for col in X_train_feat.select_dtypes(include=[np.number]).columns]
        X_train_feat = self.scale_numeric(X_train_feat, numeric_cols, fit=True)
        X_test_feat = self.scale_numeric(X_test_feat, numeric_cols, fit=False)
        
        # Drop any remaining object columns (unmapped categoricals)
        object_cols = X_train_feat.select_dtypes(include=['object']).columns.tolist()
        if object_cols:
            logger.info(f"Dropping unmapped categorical columns: {object_cols}")
            X_train_feat = X_train_feat.drop(columns=object_cols)
            X_test_feat = X_test_feat.drop(columns=object_cols)
        
        logger.info(f"✓ Implant features: {X_train_feat.shape[1]} features created")
        logger.info(f"  Train: {X_train_feat.shape[0]} samples")
        logger.info(f"  Test: {X_test_feat.shape[0]} samples")
        
        return X_train_feat, X_test_feat, y_train, y_test


def process_all_features():
    """Process features for all 3 projects"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("PHASE 3 - WEEK 2-3: FEATURE ENGINEERING")
    print("="*60 + "\n")
    
    processed_dir = DATA_DIR / "processed"
    
    # Diagnosis Features
    print("\n--- Project A: Diagnosis Features ---")
    dx_eng = DiagnosisFeatureEngineer()
    dx_train, dx_test, dy_train, dy_test = dx_eng.process(
        str(processed_dir / "diagnosis_train.csv"),
        str(processed_dir / "diagnosis_test.csv")
    )
    dx_train.to_csv(processed_dir / "diagnosis_features_train.csv", index=False)
    dx_test.to_csv(processed_dir / "diagnosis_features_test.csv", index=False)
    dy_train.to_csv(processed_dir / "diagnosis_target_train.csv", index=False)
    dy_test.to_csv(processed_dir / "diagnosis_target_test.csv", index=False)
    
    # Treatment Features
    print("\n--- Project B: Treatment Features ---")
    tx_eng = TreatmentFeatureEngineer()
    tx_train, tx_test, ty_train, ty_test = tx_eng.process(
        str(processed_dir / "treatment_train.csv"),
        str(processed_dir / "treatment_test.csv")
    )
    tx_train.to_csv(processed_dir / "treatment_features_train.csv", index=False)
    tx_test.to_csv(processed_dir / "treatment_features_test.csv", index=False)
    ty_train.to_csv(processed_dir / "treatment_target_train.csv", index=False)
    ty_test.to_csv(processed_dir / "treatment_target_test.csv", index=False)
    
    # Implant Features
    print("\n--- Project C: Implant Features ---")
    impl_eng = ImplantFeatureEngineer()
    impl_train, impl_test, iy_train, iy_test = impl_eng.process(
        str(processed_dir / "implant_train.csv"),
        str(processed_dir / "implant_test.csv")
    )
    impl_train.to_csv(processed_dir / "implant_features_train.csv", index=False)
    impl_test.to_csv(processed_dir / "implant_features_test.csv", index=False)
    iy_train.to_csv(processed_dir / "implant_target_train.csv", index=False)
    iy_test.to_csv(processed_dir / "implant_target_test.csv", index=False)
    
    print("\n" + "="*60)
    print("✓ ALL FEATURES ENGINEERED & SAVED")
    print("="*60)
    
    return {
        "diagnosis": (dx_train, dx_test, dy_train, dy_test),
        "treatment": (tx_train, tx_test, ty_train, ty_test),
        "implant": (impl_train, impl_test, iy_train, iy_test),
    }


if __name__ == "__main__":
    features = process_all_features()
