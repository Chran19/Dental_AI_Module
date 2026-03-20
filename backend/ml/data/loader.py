"""
Data Loading and Preprocessing Module
Handles loading, exploration, and preparation of all 3 datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import sys
import logging
from typing import Tuple, Dict, Any

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import (
    DATA_DIR,
    DIAGNOSIS_CONFIG,
    TREATMENT_CONFIG,
    IMPLANT_CONFIG,
    TRAINING_CONFIG,
)


class DataLoader:
    """Base class for loading and preprocessing datasets"""
    
    def __init__(self, config: Dict[str, Any], name: str):
        self.config = config
        self.name = name
        self.raw_data = None
        self.processed_data = None
        self.train_data = None
        self.test_data = None
        
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw dataset from CSV"""
        path = self.config["dataset_path"]
        logger.info(f"Loading {self.name} data from {path}")
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        
        self.raw_data = pd.read_csv(path)
        logger.info(f"Loaded {len(self.raw_data)} rows, {len(self.raw_data.columns)} columns")
        logger.info(f"Columns: {list(self.raw_data.columns)}")
        
        return self.raw_data
    
    def explore_data(self) -> Dict[str, Any]:
        """Exploratory data analysis"""
        if self.raw_data is None:
            self.load_raw_data()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"EXPLORATORY DATA ANALYSIS: {self.name}")
        logger.info(f"{'='*60}")
        
        stats = {
            "rows": len(self.raw_data),
            "columns": len(self.raw_data.columns),
            "memory_mb": self.raw_data.memory_usage(deep=True).sum() / 1024**2,
            "missing_values": self.raw_data.isnull().sum().sum(),
            "missing_percentage": (self.raw_data.isnull().sum().sum() / 
                                  (len(self.raw_data) * len(self.raw_data.columns)) * 100),
            "dtypes": self.raw_data.dtypes.value_counts().to_dict(),
        }
        
        logger.info(f"Shape: {stats['rows']} rows × {stats['columns']} columns")
        logger.info(f"Memory: {stats['memory_mb']:.2f} MB")
        logger.info(f"Missing values: {stats['missing_values']} ({stats['missing_percentage']:.2f}%)")
        logger.info(f"Data types: {stats['dtypes']}")
        
        # Summary statistics
        logger.info(f"\nNumeric features summary:")
        logger.info(self.raw_data.describe())
        
        logger.info(f"\nMissing values per column:")
        nulls = self.raw_data.isnull().sum()
        if nulls.sum() > 0:
            logger.info(nulls[nulls > 0])
        else:
            logger.info("No missing values!")
        
        return stats
    
    def handle_missing_values(self):
        """Handle missing values in dataset"""
        logger.info("Handling missing values...")
        
        numeric_cols = self.raw_data.select_dtypes(include=[np.number]).columns
        categorical_cols = self.raw_data.select_dtypes(include=['object']).columns
        
        # Numeric: fill with median
        for col in numeric_cols:
            if self.raw_data[col].isnull().any():
                median = self.raw_data[col].median()
                self.raw_data[col].fillna(median, inplace=True)
                logger.info(f"  {col}: filled {self.raw_data[col].isnull().sum()} nulls with median {median:.2f}")
        
        # Categorical: fill with mode or 'Unknown'
        for col in categorical_cols:
            if self.raw_data[col].isnull().any():
                mode = self.raw_data[col].mode()
                if len(mode) > 0:
                    self.raw_data[col].fillna(mode[0], inplace=True)
                else:
                    self.raw_data[col].fillna('Unknown', inplace=True)
                logger.info(f"  {col}: filled {self.raw_data[col].isnull().sum()} nulls")
        
        logger.info(f"Final missing values: {self.raw_data.isnull().sum().sum()}")
    
    def split_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into train and test sets"""
        logger.info("Splitting data into train/test...")
        
        X = self.raw_data.drop(columns=[self.config["target"]], errors='ignore')
        y = self.raw_data[self.config["target"]]
        
        test_size = self.config.get("test_size", 0.15)
        stratify = self.config.get("stratify", True)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.config.get("random_state", 42),
            stratify=y if stratify else None
        )
        
        self.train_data = pd.concat([X_train, y_train], axis=1)
        self.test_data = pd.concat([X_test, y_test], axis=1)
        
        logger.info(f"Train set: {len(self.train_data)} rows")
        logger.info(f"Test set: {len(self.test_data)} rows")
        
        return self.train_data, self.test_data
    
    def save_processed_data(self, output_dir: Path = None):
        """Save processed train and test datasets"""
        if output_dir is None:
            output_dir = DATA_DIR / "processed"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        prefix = self.name.lower().replace(' ', '_').split('_')[0]
        
        train_path = output_dir / f"{prefix}_train.csv"
        test_path = output_dir / f"{prefix}_test.csv"
        
        self.train_data.to_csv(train_path, index=False)
        self.test_data.to_csv(test_path, index=False)
        
        logger.info(f"Saved train data: {train_path}")
        logger.info(f"Saved test data: {test_path}")


class DiagnosisDataLoader(DataLoader):
    """Loader for diagnosis dataset"""
    
    def __init__(self):
        super().__init__(DIAGNOSIS_CONFIG, "Diagnosis")
    
    def process(self):
        """Full processing pipeline"""
        self.load_raw_data()
        self.explore_data()
        self.handle_missing_values()
        self.split_data()
        self.save_processed_data()
        return self.train_data, self.test_data


class TreatmentDataLoader(DataLoader):
    """Loader for treatment outcomes dataset"""
    
    def __init__(self):
        super().__init__(TREATMENT_CONFIG, "Treatment")
    
    def process(self):
        """Full processing pipeline"""
        self.load_raw_data()
        self.explore_data()
        self.handle_missing_values()
        self.split_data()
        self.save_processed_data()
        return self.train_data, self.test_data


class ImplantDataLoader(DataLoader):
    """Loader for implant survival dataset"""
    
    def __init__(self):
        super().__init__(IMPLANT_CONFIG, "Implant")
    
    def split_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Override split_data for survival analysis"""
        logger.info("Splitting data into train/test...")
        
        # For survival analysis, keep all columns
        test_size = self.config.get("test_size", 0.15)
        
        self.train_data, self.test_data = train_test_split(
            self.raw_data,
            test_size=test_size,
            random_state=self.config.get("random_state", 42)
        )
        
        logger.info(f"Train set: {len(self.train_data)} rows")
        logger.info(f"Test set: {len(self.test_data)} rows")
        
        return self.train_data, self.test_data
    
    def process(self):
        """Full processing pipeline"""
        self.load_raw_data()
        self.explore_data()
        self.handle_missing_values()
        
        # For survival analysis, ensure T and E columns exist
        if "T" not in self.raw_data.columns:
            # Compute T = min(follow_up_months, failure_time_months)
            self.raw_data["T"] = self.raw_data[[
                "follow_up_months", "failure_time_months"
            ]].min(axis=1)
        
        if "E" not in self.raw_data.columns:
            # Compute E: 1 if failure, 0 if censored (success)
            self.raw_data["E"] = (
                self.raw_data["outcome"] == "Failure"
            ).astype(int)
        
        self.split_data()
        self.save_processed_data()
        return self.train_data, self.test_data


def prepare_all_datasets():
    """Load and prepare all 3 datasets"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 3 - WEEK 1-2: DATA PREPARATION")
    logger.info("="*60 + "\n")
    
    datasets = {}
    
    # Load Diagnosis
    logger.info("\n--- Diagnosis Dataset ---")
    dx_loader = DiagnosisDataLoader()
    dx_train, dx_test = dx_loader.process()
    datasets["diagnosis"] = {"train": dx_train, "test": dx_test, "loader": dx_loader}
    
    # Load Treatment
    logger.info("\n--- Treatment Dataset ---")
    tx_loader = TreatmentDataLoader()
    tx_train, tx_test = tx_loader.process()
    datasets["treatment"] = {"train": tx_train, "test": tx_test, "loader": tx_loader}
    
    # Load Implant
    logger.info("\n--- Implant Dataset ---")
    impl_loader = ImplantDataLoader()
    impl_train, impl_test = impl_loader.process()
    datasets["implant"] = {"train": impl_train, "test": impl_test, "loader": impl_loader}
    
    logger.info("\n" + "="*60)
    logger.info("✓ ALL DATASETS PREPARED AND SAVED")
    logger.info("="*60)
    
    return datasets


if __name__ == "__main__":
    # Run data preparation
    datasets = prepare_all_datasets()
    
    print("\nSummary:")
    print(f"Diagnosis: {len(datasets['diagnosis']['train'])} train, {len(datasets['diagnosis']['test'])} test")
    print(f"Treatment: {len(datasets['treatment']['train'])} train, {len(datasets['treatment']['test'])} test")
    print(f"Implant: {len(datasets['implant']['train'])} train, {len(datasets['implant']['test'])} test")
