"""
Project C: Implant Survival Cox Proportional Hazards Model
Trains survival analysis model for implant success prediction
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from sklearn.preprocessing import StandardScaler
import joblib
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODELS_DIR, DATA_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ImplantModelTrainer:
    """Train and evaluate implant survival model using Cox PH"""
    
    def __init__(self):
        self.model = None
        self.metrics = {}
        self.scaler = StandardScaler()
    
    def load_features(self):
        """Load engineered features and survival data"""
        processed_dir = DATA_DIR / "processed"
        
        X_train = pd.read_csv(processed_dir / "implant_features_train.csv")
        X_test = pd.read_csv(processed_dir / "implant_features_test.csv")
        y_train = pd.read_csv(processed_dir / "implant_target_train.csv")
        y_test = pd.read_csv(processed_dir / "implant_target_test.csv")
        
        # Remove object columns
        object_cols = X_train.select_dtypes(include=['object']).columns
        if len(object_cols) > 0:
            logger.info(f"Dropping object columns: {list(object_cols)}")
            X_train = X_train.drop(columns=object_cols)
            X_test = X_test.drop(columns=object_cols)
        
        logger.info(f"Loaded implant features: {X_train.shape}, {X_test.shape}")
        logger.info(f"Survival data: T and E columns in target")
        return X_train, X_test, y_train, y_test
    
    def scale_features(self, X_train, X_test, fit=True):
        """Scale features for Cox model"""
        if fit:
            X_train_scaled = self.scaler.fit_transform(X_train)
        else:
            X_train_scaled = self.scaler.transform(X_train)
        
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to dataframe to preserve column names
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
        
        return X_train_scaled, X_test_scaled
    
    def prepare_cox_data(self, X_train, y_train):
        """Prepare data for Cox model"""
        # Combine features with survival columns
        cox_train = X_train.copy()
        cox_train['T'] = y_train['T'].values
        cox_train['E'] = y_train['E'].values
        
        # Remove problematic columns for convergence
        problematic_cols = ['bone_quality_score', 'adequate_width', 'failure_time_months',
                           'implant_stability_ratio']  # high correlation columns
        problematic_cols = [c for c in problematic_cols if c in cox_train.columns]
        if problematic_cols:
            logger.info(f"Removing problematic columns: {problematic_cols}")
            cox_train = cox_train.drop(columns=problematic_cols)
        
        return cox_train
    
    def train(self, X_train, y_train):
        """Train Cox Proportional Hazards model"""
        logger.info("Training implant survival model (Cox PH)...")
        
        # Prepare data
        cox_data = self.prepare_cox_data(X_train, y_train)
        
        # Fit Cox model
        self.model = CoxPHFitter(penalizer=0.1)
        self.model.fit(cox_data, duration_col='T', event_col='E', show_progress=False)
        
        logger.info("✓ Model training complete")
        return self.model
    
    def evaluate(self, X_test, y_test):
        """Evaluate model"""
        logger.info("Evaluating model...")
        
        # Remove same problematic columns from test set
        X_test_adj = X_test.copy()
        problematic_cols = ['bone_quality_score', 'adequate_width', 'failure_time_months',
                           'implant_stability_ratio']
        problematic_cols = [c for c in problematic_cols if c in X_test_adj.columns]
        if problematic_cols:
            X_test_adj = X_test_adj.drop(columns=problematic_cols)
        
        # Prepare test data
        cox_test = X_test_adj.copy()
        cox_test['T'] = y_test['T'].values
        cox_test['E'] = y_test['E'].values
        
        # Get concordance index
        concordance = self.model.concordance_index_
        
        # Get predictions (use adjusted X_test)
        partial_hazard = self.model.predict_partial_hazard(X_test_adj)
        
        # Summary stats
        n_events = y_test['E'].sum()
        n_censored = len(y_test) - n_events
        
        self.metrics = {
            'concordance_index': float(concordance),
            'n_samples': len(X_test),
            'n_features': X_test_adj.shape[1],
            'n_events': int(n_events),
            'n_censored': int(n_censored),
            'event_rate': float(n_events / len(y_test)),
        }
        
        logger.info(f"\nTest Set Results:")
        logger.info(f"  Concordance Index: {concordance:.4f} (target: ≥ 0.82)")
        logger.info(f"  Events: {n_events}, Censored: {n_censored}")
        logger.info(f"  Event Rate: {n_events / len(y_test):.2%}")
        
        # Feature significance
        logger.info(f"\nTop Features (by |coeff|):")
        coef_df = self.model.summary[['coef', 'exp(coef)']].sort_values('coef', key=abs, ascending=False)
        for idx, row in coef_df.head(10).iterrows():
            logger.info(f"  {idx}: coef={row['coef']:.4f}, HR={row['exp(coef)']:.4f}")
        
        return partial_hazard
    
    def save_model(self):
        """Save trained model"""
        logger.info("Saving model...")
        
        model_path = MODELS_DIR / "implant_cox_model.joblib"
        joblib.dump(self.model, model_path)
        logger.info(f"✓ Model saved: {model_path}")


def run_project_c():
    """Execute Project C training"""
    print("\n" + "="*60)
    print("PROJECT C: IMPLANT SURVIVAL MODEL (Week 5-6)")
    print("="*60 + "\n")
    
    trainer = ImplantModelTrainer()
    
    # Load features
    X_train, X_test, y_train, y_test = trainer.load_features()
    
    # Scale features
    X_train_scaled, X_test_scaled = trainer.scale_features(X_train, X_test, fit=True)
    
    logger.info(f"\nDataset Summary:")
    logger.info(f"  Train: {X_train_scaled.shape}")
    logger.info(f"  Test: {X_test_scaled.shape}")
    logger.info(f"  Survival data: T (time), E (event indicator)")
    
    # Train and evaluate
    trainer.train(X_train_scaled, y_train)
    trainer.evaluate(X_test_scaled, y_test)
    trainer.save_model()
    
    print("\n" + "="*60)
    print("✓ PROJECT C COMPLETE")
    print("="*60)
    
    return trainer, trainer.metrics


if __name__ == "__main__":
    trainer, metrics = run_project_c()
    print(f"\nFinal Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
