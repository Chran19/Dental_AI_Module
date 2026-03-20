"""
Phase 4: Master Workflow Script
Orchestrates complete dental image analysis training and evaluation pipeline
"""

import sys
from pathlib import Path
import argparse
import logging
import torch

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner(title: str):
    """Print formatted banner"""
    width = 70
    print("\n" + "="*width)
    print(f"{title.center(width)}")
    print("="*width)


def check_dataset():
    """Verify dataset is available and properly formatted"""
    print_banner("CHECKING DATASET")
    
    dataset_root = Path('backend/ml/datasets/dental_images')
    
    if not dataset_root.exists():
        logger.error(f"❌ Dataset not found at {dataset_root}")
        return False
    
    required_files = {
        'raw_images': 'directory',
        'labels.csv': 'file',
        'train_split.txt': 'file',
        'val_split.txt': 'file',
        'test_split.txt': 'file',
    }
    
    for item, item_type in required_files.items():
        path = dataset_root / item
        if item_type == 'directory':
            exists = path.is_dir()
        else:
            exists = path.is_file()
        
        status = "✓" if exists else "❌"
        print(f"{status} {item}")
        
        if not exists:
            logger.error(f"Missing: {item}")
            return False
    
    # Count images
    import pandas as pd
    labels_df = pd.read_csv(dataset_root / 'labels.csv')
    print(f"\n✓ Total images: {len(labels_df)}")
    print(f"  - Train: {len(open(dataset_root / 'train_split.txt').readlines())}")
    print(f"  - Val: {len(open(dataset_root / 'val_split.txt').readlines())}")
    print(f"  - Test: {len(open(dataset_root / 'test_split.txt').readlines())}")
    
    print("\n✅ Dataset verification passed!")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print_banner("CHECKING DEPENDENCIES")
    
    required_packages = {
        'torch': 'PyTorch',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn',
    }
    
    all_available = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"❌ {name} - not installed")
            all_available = False
    
    if all_available:
        print("\n✅ All dependencies available!")
    else:
        logger.warning("⚠️ Some dependencies missing. Install with: pip install torch pandas numpy scikit-learn")
    
    return all_available


def check_gpu():
    """Check GPU availability"""
    print_banner("CHECKING GPU")
    
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        print(f"✓ GPU available")
        for i in range(device_count):
            props = torch.cuda.get_device_properties(i)
            print(f"   Device {i}: {props.name}")
        print(f"✓ Device: CUDA (GPU acceleration enabled)")
    else:
        print(f"⚠️  No GPU found - will use CPU (slower)")
        print(f"✓ Device: CPU")
    
    return torch.cuda.is_available()


def run_tests():
    """Run comprehensive test suite"""
    print_banner("RUNNING TESTS")
    
    import subprocess
    
    print("Running Phase 4 integration tests...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 
         'backend/ml/image_analysis/test_phase4_complete.py', 
         '-v', '--tb=short'],
        cwd=Path('Dental_AI_Module') if Path('Dental_AI_Module').exists() else '.'
    )
    
    return result.returncode == 0


def train_model(epochs: int = 20, batch_size: int = 16):
    """Train the dental image CNN model"""
    print_banner("TRAINING CNN MODEL")
    
    try:
        from ml.image_analysis.phase4_training_pipeline import train_phase4_model
        
        config = {
            'dataset_root': Path('backend/ml/datasets/dental_images'),
            'model_save_path': Path('backend/ml/models/dental_cnn_model_phase4.pth'),
            'results_dir': Path('backend/ml/results'),
            'batch_size': batch_size,
            'num_epochs': epochs,
            'learning_rate': 0.001,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'num_workers': 0 if sys.platform == 'win32' else 2,
        }
        
        logger.info(f"Training configuration:")
        logger.info(f"  Device: {config['device']}")
        logger.info(f"  Batch size: {config['batch_size']}")
        logger.info(f"  Epochs: {config['num_epochs']}")
        logger.info(f"  Learning rate: {config['learning_rate']}")
        
        model, history, test_results = train_phase4_model(config)
        
        print("\n✅ Training completed successfully!")
        print(f"\nTest Results:")
        print(f"  Accuracy:  {test_results['accuracy']:.4f}")
        print(f"  Precision: {test_results['precision']:.4f}")
        print(f"  Recall:    {test_results['recall']:.4f}")
        print(f"  F1-Score:  {test_results['f1']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def evaluate_model():
    """Evaluate trained model on all splits"""
    print_banner("EVALUATING MODEL")
    
    try:
        from ml.image_analysis.phase4_evaluator import evaluate_phase4_model
        
        logger.info("Evaluating on train, validation, and test sets...")
        evaluator = evaluate_phase4_model(
            model_path='backend/ml/models/dental_cnn_model_phase4.pth',
            dataset_root='backend/ml/datasets/dental_images'
        )
        
        print("\n✅ Evaluation completed successfully!")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model not found. Please train the model first.")
        return False
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_status():
    """Show current Phase 4 status"""
    print_banner("PHASE 4 STATUS")
    
    checklist = {
        'Dataset': Path('backend/ml/datasets/dental_images').exists(),
        'Training Script': Path('backend/ml/image_analysis/phase4_training_pipeline.py').exists(),
        'Evaluator': Path('backend/ml/image_analysis/phase4_evaluator.py').exists(),
        'Tests': Path('backend/ml/image_analysis/test_phase4_complete.py').exists(),
        'Model (trained)': Path('backend/ml/models/dental_cnn_model_phase4.pth').exists(),
    }
    
    for item, status in checklist.items():
        icon = "✓" if status else "○"
        print(f"{icon} {item}")
    
    if checklist['Model (trained)']:
        print(f"\n✅ Model available - ready for inference!")
    else:
        print(f"\n⏳ Model needs to be trained")


def main():
    """Main workflow orchestrator"""
    parser = argparse.ArgumentParser(
        description='Phase 4 Dental Image Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python phase4_workflow.py --check-all
  python phase4_workflow.py --train --epochs 20
  python phase4_workflow.py --evaluate
  python phase4_workflow.py --full-pipeline
        """
    )
    
    parser.add_argument('--check-all', action='store_true', 
                       help='Check dataset, dependencies, and GPU')
    parser.add_argument('--check-dataset', action='store_true',
                       help='Check dataset integrity')
    parser.add_argument('--check-dependencies', action='store_true',
                       help='Check required packages')
    parser.add_argument('--check-gpu', action='store_true',
                       help='Check GPU availability')
    parser.add_argument('--tests', action='store_true',
                       help='Run test suite')
    parser.add_argument('--train', action='store_true',
                       help='Train CNN model')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of training epochs (default: 20)')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size (default: 16)')
    parser.add_argument('--evaluate', action='store_true',
                       help='Evaluate trained model')
    parser.add_argument('--full-pipeline', action='store_true',
                       help='Run complete pipeline: check -> train -> evaluate')
    parser.add_argument('--status', action='store_true',
                       help='Show Phase 4 status')
    
    args = parser.parse_args()
    
    # Default action
    if not any(vars(args).values()):
        args.check_all = True
    
    try:
        # Check all
        if args.check_all:
            check_dataset()
            check_dependencies()
            check_gpu()
        
        # Individual checks
        if args.check_dataset:
            check_dataset()
        if args.check_dependencies:
            check_dependencies()
        if args.check_gpu:
            check_gpu()
        
        # Tests
        if args.tests:
            run_tests()
        
        # Train
        if args.train:
            if not check_dataset():
                logger.error("Cannot train: dataset check failed")
                sys.exit(1)
            train_model(epochs=args.epochs, batch_size=args.batch_size)
        
        # Evaluate
        if args.evaluate:
            evaluate_model()
        
        # Full pipeline
        if args.full_pipeline:
            if not check_dataset():
                logger.error("Pipeline aborted: dataset check failed")
                sys.exit(1)
            check_dependencies()
            check_gpu()
            
            print("\n" + "="*70)
            print("Starting full pipeline: train -> evaluate".center(70))
            print("="*70 + "\n")
            
            if train_model(epochs=args.epochs, batch_size=args.batch_size):
                evaluate_model()
            else:
                logger.error("Training failed, skipping evaluation")
        
        # Status
        if args.status:
            show_status()
        
        print_banner("✅ PHASE 4 WORKFLOW COMPLETE")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
