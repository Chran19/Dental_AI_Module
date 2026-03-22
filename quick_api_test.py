"""
Quick test: Upload single image and show results
"""
import requests
import json
import sys
from pathlib import Path

def test_upload():
    print('[TESTING] Image Analysis API')
    print('=' * 80)

    # Test status endpoint
    print('[1] Checking API status...')
    try:
        response = requests.get('http://127.0.0.1:8000/image-analysis/status', timeout=5)
        if response.status_code == 200:
            print('[OK] API is running!')
            status = response.json()
            print(f'     Service: {status.get("service", "N/A")}')
            print(f'     Device: {status.get("device", "N/A")}')
        else:
            print(f'[ERROR] Status code: {response.status_code}')
            return False
    except Exception as e:
        print(f'[ERROR] Cannot connect: {e}')
        print('[TIP] Make sure the server is running on port 8000')
        return False

    print()
    print('[2] Uploading test image...')

    # Upload test image
    image_path = Path('backend/ml/datasets/dental_images/raw_images/case_0000.jpg')
    
    if not image_path.exists():
        print(f'[ERROR] Image not found: {image_path}')
        return False
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        data = {'patient_id': 'DEMO_TEST'}
        
        try:
            response = requests.post('http://127.0.0.1:8000/image-analysis/upload', 
                                    files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print('[SUCCESS] Image analyzed!\n')
                
                print('=' * 80)
                print('PATHOLOGY ANALYSIS')
                print('=' * 80)
                
                path = result['pathology_analysis']
                print(f"Primary Pathology: {path['primary_pathology']['name']}")
                print(f"Confidence: {path['primary_pathology']['confidence']:.1%}")
                print(f"Severity: {path['severity_level']} ({path['severity_score']:.1f}/10)")
                print(f"Location: {path['tooth_region']['name']}")
                is_abnormal = 'YES' if path['is_abnormal'] else 'NO'
                print(f"Abnormal: {is_abnormal}")
                
                print()
                print('=' * 80)
                print('BONE ANALYSIS')
                print('=' * 80)
                
                bone = result['bone_analysis']
                print(f"Bone Type: {bone['bone_density']['bone_type']}")
                print(f"Bone Loss: {bone['alveolar_crest']['bone_loss_percentage']:.1f}%")
                print(f"Overall: {bone['overall_bone_quality']}")
                
                print()
                print('=' * 80)
                print('CLINICAL RECOMMENDATIONS')
                print('=' * 80)
                
                for i, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"{i}. {rec}")
                
                print()
                print('[SAVED] Full response to response.json')
                
                with open('response.json', 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                
                return True
            else:
                print(f'[ERROR] Upload failed: {response.status_code}')
                print(response.text)
                return False
        except Exception as e:
            print(f'[ERROR] {e}')
            return False

if __name__ == '__main__':
    success = test_upload()
    sys.exit(0 if success else 1)
