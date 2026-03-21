"""
Phase 4 Dataset Preparation Script
Converts existing Dental OPG classification dataset into Phase 4 format
"""

import os
import csv
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import random

# Set random seed for reproducibility
random.seed(42)

# Define paths
DATASET_ROOT = Path(__file__).parent.parent / "datasets" / "Dental OPG XRAY Dataset" / "Dental OPG (Classification)"
OUTPUT_DIR = Path(__file__).parent.parent / "datasets" / "dental_images"
RAW_IMAGES_DIR = OUTPUT_DIR / "raw_images"

# Mapping of folder names to pathology classes and default severity
PATHOLOGY_MAPPING = {
    "Healthy Teeth": ("Normal", 0.0),
    "Caries": ("Caries", 4.0),
    "Fractured Teeth": ("Fracture", 6.5),
    "Impacted teeth": ("Implant", 3.0),  # Could be Periapical_Lesion
    "Infection": ("Periapical_Lesion", 7.0),
    "BDC-BDR": ("Bone_Loss", 5.5),
}

# Tooth region mapping (randomly assigned for now - can be refined)
TOOTH_REGIONS = [
    "Anterior_Upper", "Anterior_Lower", 
    "Premolar_Upper", "Premolar_Lower",
    "Molar_Upper", "Molar_Lower"
]

def prepare_dataset():
    """Prepare dataset in Phase 4 format"""
    
    print("=" * 60)
    print("PHASE 4 DATASET PREPARATION")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✓ Created output directories")
    print(f"  - {OUTPUT_DIR}")
    print(f"  - {RAW_IMAGES_DIR}")
    
    # Collect all images
    labels_data = []
    image_count = 0
    
    print(f"\n📂 Scanning source dataset: {DATASET_ROOT}")
    print("-" * 60)
    
    for pathology_folder in DATASET_ROOT.iterdir():
        if not pathology_folder.is_dir():
            continue
        
        folder_name = pathology_folder.name
        if folder_name not in PATHOLOGY_MAPPING:
            print(f"⚠️  Skipping unknown folder: {folder_name}")
            continue
        
        pathology_class, default_severity = PATHOLOGY_MAPPING[folder_name]
        
        # Get all images from this folder
        image_files = list(pathology_folder.glob("*.jpg")) + list(pathology_folder.glob("*.png"))
        
        print(f"\n📸 {folder_name}")
        print(f"   Pathology Class: {pathology_class}")
        print(f"   Default Severity: {default_severity}")
        print(f"   Images Found: {len(image_files)}")
        
        # Process each image
        for img_file in image_files:
            # Generate unique filename
            new_filename = f"case_{image_count:04d}{img_file.suffix}"
            
            # Copy image to raw_images folder
            dst_path = RAW_IMAGES_DIR / new_filename
            shutil.copy2(img_file, dst_path)
            
            # Randomly assign tooth region (can be refined later)
            tooth_region = random.choice(TOOTH_REGIONS)
            
            # Add some variation to severity (±10%)
            severity = default_severity + random.uniform(-1.0, 1.0)
            severity = max(0.0, min(10.0, severity))  # Clamp to 0-10
            
            labels_data.append({
                'filename': new_filename,
                'pathology_class': pathology_class,
                'tooth_region': tooth_region,
                'severity_score': round(severity, 2)
            })
            
            image_count += 1
    
    print(f"\n✓ Copied {image_count} images to {RAW_IMAGES_DIR}")
    
    # Write labels.csv
    labels_file = OUTPUT_DIR / "labels.csv"
    with open(labels_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'pathology_class', 'tooth_region', 'severity_score'])
        writer.writeheader()
        writer.writerows(labels_data)
    
    print(f"\n✓ Created labels.csv: {labels_file}")
    print(f"  Total labels: {len(labels_data)}")
    
    # Create train/val/test splits
    filenames = [item['filename'] for item in labels_data]
    
    train, temp = train_test_split(filenames, test_size=0.30, random_state=42)
    val, test = train_test_split(temp, test_size=0.50, random_state=42)
    
    # Write split files
    with open(OUTPUT_DIR / "train_split.txt", 'w') as f:
        f.write('\n'.join(train))
    
    with open(OUTPUT_DIR / "val_split.txt", 'w') as f:
        f.write('\n'.join(val))
    
    with open(OUTPUT_DIR / "test_split.txt", 'w') as f:
        f.write('\n'.join(test))
    
    print(f"\n✓ Created train/val/test splits:")
    print(f"  - train_split.txt: {len(train)} images ({len(train)*100/len(filenames):.1f}%)")
    print(f"  - val_split.txt: {len(val)} images ({len(val)*100/len(filenames):.1f}%)")
    print(f"  - test_split.txt: {len(test)} images ({len(test)*100/len(filenames):.1f}%)")
    
    # Print statistics
    print(f"\n📊 Dataset Statistics:")
    print("-" * 60)
    
    pathology_counts = {}
    region_counts = {}
    
    for item in labels_data:
        pathology = item['pathology_class']
        region = item['tooth_region']
        
        pathology_counts[pathology] = pathology_counts.get(pathology, 0) + 1
        region_counts[region] = region_counts.get(region, 0) + 1
    
    print("\nPathology Distribution:")
    for pathology, count in sorted(pathology_counts.items(), key=lambda x: x[1], reverse=True):
        pct = count * 100 / len(labels_data)
        print(f"  {pathology:20s}: {count:4d} images ({pct:5.1f}%)")
    
    print("\nTooth Region Distribution:")
    for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
        pct = count * 100 / len(labels_data)
        print(f"  {region:20s}: {count:4d} images ({pct:5.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ DATASET PREPARATION COMPLETE!")
    print("=" * 60)
    print(f"\nOutput Location: {OUTPUT_DIR}")
    print(f"\nReady for Phase 4 training!")

if __name__ == "__main__":
    prepare_dataset()
