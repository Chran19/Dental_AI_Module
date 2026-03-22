"""
Manual Image Upload Testing Script
Tests the Image Analysis API with sample dental radiographs
Shows: Pathology Analysis, Bone Analysis, Clinical Guidance, and Recommendations
"""

import requests
import json
import sys
from pathlib import Path
from typing import Dict, Any
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"
IMAGE_UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/image-analysis/upload"
STATUS_ENDPOINT = f"{API_BASE_URL}/api/v1/image-analysis/status"

# Test Images Directory
DENTAL_IMAGES_DIR = Path("backend/ml/datasets/dental_images/raw_images")


def print_header(title: str, width: int = 80):
    """Print formatted header"""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title: str):
    """Print formatted section"""
    print(f"\n--- {title} ---")


def pretty_print_json(data: Dict[Any, Any], indent: int = 2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def check_api_health() -> bool:
    """Check if API is running and healthy"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            print("[OK] API is running and healthy")
            status_data = response.json()
            print(f"     Service: {status_data.get('service', 'N/A')}")
            print(f"     Device: {status_data.get('device', 'N/A')}")
            return True
        else:
            print(f"[ERROR] API returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("[ERROR] Cannot connect to API. Make sure the server is running:")
        print("        python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"[ERROR] API health check failed: {e}")
        return False


def upload_image(image_path: Path, patient_id: str = None) -> Dict[Any, Any]:
    """Upload image and get analysis results"""
    if not image_path.exists():
        print(f"[ERROR] Image not found: {image_path}")
        return None
    
    print(f"\n[UPLOADING] {image_path.name}...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            data = {'patient_id': patient_id or 'TEST_PATIENT'}
            
            response = requests.post(IMAGE_UPLOAD_ENDPOINT, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Upload failed with status {response.status_code}")
                print(response.text)
                return None
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return None


def display_pathology_analysis(result: Dict[Any, Any]):
    """Display pathology analysis results"""
    print_section("PATHOLOGY ANALYSIS")
    
    if 'pathology_analysis' in result:
        path = result['pathology_analysis']
        
        # Primary Pathology
        print(f"\nPrimary Finding:")
        print(f"  • Pathology: {path['primary_pathology']['name']}")
        print(f"  • Confidence: {path['primary_pathology']['confidence']:.1%}")
        print(f"  • Confidence Level: {path['primary_pathology']['confidence_level']}")
        
        # Location
        print(f"\nLocation:")
        print(f"  • Region: {path['tooth_region']['name']}")
        print(f"  • Region Confidence: {path['tooth_region']['confidence']:.1%}")
        
        # Severity
        print(f"\nSeverity Assessment:")
        print(f"  • Severity Level: {path['severity_level']}")
        print(f"  • Severity Score: {path['severity_score']:.1f}/10")
        print(f"  • Model Confidence: {path['model_confidence']:.1%}")
        
        # Is Abnormal
        print(f"\nAbnormality Status:")
        print(f"  • Is Abnormal: {'YES' if path['is_abnormal'] else 'NO'}")
        
        # All Detected Pathologies
        if path['all_pathologies']:
            print(f"\nAll Detected Pathologies:")
            for i, p in enumerate(path['all_pathologies'], 1):
                print(f"  {i}. {p['name']}: {p['probability']:.1%}")


def display_bone_analysis(result: Dict[Any, Any]):
    """Display bone analysis results"""
    print_section("BONE ANALYSIS")
    
    if 'bone_analysis' in result:
        bone = result['bone_analysis']
        
        # Bone Density
        print(f"\nBone Density:")
        print(f"  • Type: {bone['bone_density']['bone_type']}")
        print(f"  • Density Ratio: {bone['bone_density']['density_ratio']:.1%}")
        print(f"  • Assessment: {bone['bone_density']['assessment']}")
        
        # Alveolar Crest
        print(f"\nAlveolar Bone Crest:")
        print(f"  • Crest Level: {bone['alveolar_crest']['crest_level_pixels']:.1f} pixels")
        print(f"  • Bone Loss: {bone['alveolar_crest']['bone_loss_percentage']:.1f}%")
        print(f"  • Assessment: {bone['alveolar_crest']['assessment']}")
        
        # Cortication
        print(f"\nCortication (Bone Outline Quality):")
        print(f"  • Present: {'YES' if bone['cortication']['present'] else 'NO'}")
        print(f"  • Quality: {bone['cortication']['quality']}")
        print(f"  • Assessment: {bone['cortication']['assessment']}")
        
        # Overall Quality
        print(f"\nOverall Bone Quality:")
        print(f"  • {bone['overall_bone_quality']}")


def display_clinical_guidance(result: Dict[Any, Any]):
    """Display clinical guidance and recommendations"""
    print_section("CLINICAL GUIDANCE & RECOMMENDATIONS")
    
    if 'clinical_summary' in result:
        print(f"\nClinical Summary:")
        print(result['clinical_summary'])
    
    if 'recommendations' in result:
        print(f"\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Intervention Status
    if 'pathology_analysis' in result:
        path = result['pathology_analysis']
        intervention = path.get('requires_intervention', {})
        
        print(f"\nIntervention Status:")
        print(f"  • Intervention Needed: {'YES' if intervention.get('needed') else 'NO'}")
        if intervention.get('needed'):
            print(f"  • Urgency: {intervention.get('urgency')}")
            print(f"  • Recommended Action: {intervention.get('recommended_action')}")


def display_annotated_image(result: Dict[Any, Any]):
    """Show info about annotated image"""
    if 'annotated_image_base64' in result:
        print_section("ANNOTATED IMAGE")
        print(f"\nBase64 encoded annotated image is available in the full response")
        print(f"Image Size: {len(result['annotated_image_base64'])} bytes")
        print(f"(Can be displayed in HTML or saved to file)")


def display_file_info(result: Dict[Any, Any]):
    """Display file information"""
    print_section("FILE INFORMATION")
    
    if 'file_info' in result:
        info = result['file_info']
        print(f"\n  • Filename: {info.get('filename', 'N/A')}")
        print(f"  • Size: {info.get('size', 'N/A')} bytes")
        print(f"  • Format: {info.get('format', 'N/A')}")
        print(f"  • Dimensions: {info.get('width', 'N/A')} x {info.get('height', 'N/A')} pixels")


def display_full_response(result: Dict[Any, Any]):
    """Display full response as JSON"""
    print_section("FULL RESPONSE (JSON)")
    pretty_print_json(result)


def test_single_image(image_name: str = "case_0000.jpg", show_full_response: bool = False):
    """Test a single image"""
    image_path = DENTAL_IMAGES_DIR / image_name
    
    print_header(f"Testing Image: {image_name}")
    
    result = upload_image(image_path, patient_id="TEST_001")
    
    if result and result.get('status') == 'success':
        print("\n[SUCCESS] Image analyzed successfully!\n")
        
        # Display all analysis results
        display_file_info(result)
        display_pathology_analysis(result)
        display_bone_analysis(result)
        display_clinical_guidance(result)
        display_annotated_image(result)
        
        if show_full_response:
            display_full_response(result)
        
        return result
    else:
        print("\n[FAILED] Image analysis failed")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
        return None


def test_multiple_images(count: int = 5):
    """Test multiple images"""
    print_header(f"Testing Multiple Images ({count} images)")
    
    images = list(DENTAL_IMAGES_DIR.glob("case_*.jpg"))[:count]
    
    results = []
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Testing {image_path.name}...")
        result = upload_image(image_path, patient_id=f"TEST_{i:03d}")
        
        if result and result.get('status') == 'success':
            results.append({
                'filename': image_path.name,
                'pathology': result['pathology_analysis']['primary_pathology']['name'],
                'confidence': result['pathology_analysis']['primary_pathology']['confidence'],
                'severity': result['pathology_analysis']['severity_level'],
                'abnormal': result['pathology_analysis']['is_abnormal']
            })
            print(f"     ✓ {result['pathology_analysis']['primary_pathology']['name']} "
                  f"({result['pathology_analysis']['primary_pathology']['confidence']:.1%})")
        else:
            print(f"     ✗ Analysis failed")
        
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print_header("BATCH ANALYSIS SUMMARY")
    print(f"\nTotal Images: {len(results)}")
    
    if results:
        print(f"\nPathology Distribution:")
        pathologies = {}
        for r in results:
            pathologies[r['pathology']] = pathologies.get(r['pathology'], 0) + 1
        
        for pathology, count in sorted(pathologies.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {pathology}: {count}")
        
        print(f"\nSeverity Distribution:")
        severities = {}
        for r in results:
            severities[r['severity']] = severities.get(r['severity'], 0) + 1
        
        for severity, count in sorted(severities.items()):
            print(f"  • {severity}: {count}")
        
        print(f"\nAbnormal Cases: {sum(1 for r in results if r['abnormal'])}")
        print(f"Normal Cases: {sum(1 for r in results if not r['abnormal'])}")


def main():
    """Main test function"""
    print_header("DENTAL AI IMAGE ANALYSIS - MANUAL TESTING")
    
    # Check API health
    if not check_api_health():
        sys.exit(1)
    
    # Test menu
    while True:
        print("\n" + "=" * 80)
        print("TEST OPTIONS:")
        print("=" * 80)
        print("1. Test Single Image (case_0000.jpg)")
        print("2. Test Single Image with Full Response (JSON)")
        print("3. Test Multiple Images (5 images)")
        print("4. Test Custom Image")
        print("5. List Available Images")
        print("0. Exit")
        print("=" * 80)
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            test_single_image("case_0000.jpg", show_full_response=False)
        
        elif choice == "2":
            test_single_image("case_0000.jpg", show_full_response=True)
        
        elif choice == "3":
            count = input("\nHow many images to test? (default: 5): ").strip()
            try:
                count = int(count) if count else 5
                test_multiple_images(count)
            except ValueError:
                print("[ERROR] Invalid number")
        
        elif choice == "4":
            image_name = input("\nEnter image filename (e.g., case_0003.jpg): ").strip()
            if image_name:
                test_single_image(image_name, show_full_response=False)
            else:
                print("[ERROR] Invalid filename")
        
        elif choice == "5":
            print("\nAvailable Test Images:")
            images = sorted(DENTAL_IMAGES_DIR.glob("case_*.jpg"))
            for i, img in enumerate(images[:20], 1):
                print(f"  {i:2d}. {img.name}")
            if len(images) > 20:
                print(f"  ... and {len(images) - 20} more")
        
        elif choice == "0":
            print("\nExiting...")
            break
        
        else:
            print("[ERROR] Invalid choice")


if __name__ == "__main__":
    main()
