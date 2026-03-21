"""
Image Analysis Routes: API endpoints for Phase 4 dental image analysis
Handles radiograph upload, analysis, and integration with diagnosis engine
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.image_analysis.inference.image_analyzer_service import create_image_analyzer_service
from app.utils import convert_to_serializable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/image-analysis", tags=["Image Analysis"])

# Global analyzer service (initialized once)
image_analyzer = None


def get_analyzer():
    """Get or create image analyzer service"""
    global image_analyzer
    if image_analyzer is None:
        try:
            model_path = Path(__file__).parent.parent.parent / 'ml' / 'models' / 'dental_cnn_model_phase4.pth'
            device = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'
            image_analyzer = create_image_analyzer_service(
                model_path=str(model_path),
                device=device
            )
            logger.info(f"✅ Image analyzer initialized on {device}")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
    return image_analyzer


class ImageAnalysisRequest(BaseModel):
    """Request model for URL-based image analysis"""
    image_url: str
    patient_id: Optional[str] = None
    with_diagnosis: bool = False


@router.post("/upload")
async def upload_and_analyze(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    with_diagnosis: bool = Form(False)
):
    """
    Upload radiograph and analyze for pathologies
    
    Parameters:
    - file: Image file (JPG, PNG, TIFF)
    - patient_id: Optional patient identifier
    - with_diagnosis: Boolean to also integrate with diagnosis engine
        
    Returns:
    - Analysis results including pathology, bone analysis, annotations
    """
    try:
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f'File type {file_ext} not supported. Use: {allowed_extensions}'
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            filepath = tmp.name
        
        logger.info(f"Uploaded file: {filepath}")
        
        try:
            # Get analyzer service
            analyzer = get_analyzer()
            
            # Analyze image
            logger.info(f"Analyzing image: {filepath}")
            analysis_result = analyzer.analyze_image(filepath)
            
            if analysis_result.get('status') == 'error':
                raise HTTPException(status_code=400, detail=analysis_result.get('error'))
            
            # Optionally integrate with diagnosis engine
            if with_diagnosis and patient_id:
                logger.info(f"Integrating with diagnosis engine for patient {patient_id}")
                try:
                    from app.services.diagnosis_service import get_diagnosis_with_image_evidence
                    diagnosis_result = get_diagnosis_with_image_evidence(
                        patient_id=patient_id,
                        image_analysis=analysis_result
                    )
                    analysis_result['diagnosis_integration'] = diagnosis_result
                except Exception as e:
                    logger.warning(f"Could not integrate with diagnosis: {e}")
                    analysis_result['diagnosis_integration'] = {
                        'error': str(e),
                        'note': 'Analysis complete but diagnosis integration failed'
                    }
            
            return convert_to_serializable(analysis_result)
            
        finally:
            # Clean up temp file
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Cleaned up temp file: {filepath}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_and_analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-url")
async def analyze_from_url(request: ImageAnalysisRequest):
    """
    Analyze radiograph from URL
    
    Body:
    - image_url: URL to radiograph image
    - patient_id: Optional patient identifier
    - with_diagnosis: Optional integration with diagnosis engine
    """
    try:
        import requests
        
        # Download image
        try:
            response = requests.get(request.image_url, timeout=10)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(response.content)
                filepath = tmp.name
            
            # Analyze
            analyzer = get_analyzer()
            analysis_result = analyzer.analyze_image(filepath)
            
            # Clean up
            os.unlink(filepath)
            
            # Integrate with diagnosis if requested
            if request.with_diagnosis and request.patient_id:
                try:
                    from app.services.diagnosis_service import get_diagnosis_with_image_evidence
                    diagnosis_result = get_diagnosis_with_image_evidence(
                        patient_id=request.patient_id,
                        image_analysis=analysis_result
                    )
                    analysis_result['diagnosis_integration'] = diagnosis_result
                except Exception as e:
                    logger.warning(f"Diagnosis integration failed: {e}")
            
            return convert_to_serializable(analysis_result)
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f'Failed to download image: {str(e)}'
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_from_url: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze(files: List[UploadFile] = File(...)):
    """
    Analyze multiple radiographs
    
    Parameters:
    - files: Multiple image files
        
    Returns:
    - Batch analysis results for all files
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        analyzer = get_analyzer()
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(files),
            'analyses': [],
            'errors': []
        }
        
        for file in files:
            try:
                # Check file extension
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'}
                file_ext = Path(file.filename).suffix.lower()
                if file_ext not in allowed_extensions:
                    results['errors'].append({
                        'filename': file.filename,
                        'error': f'File type {file_ext} not supported'
                    })
                    continue
                
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    filepath = tmp.name
                
                # Analyze
                analysis = analyzer.analyze_image(filepath)
                
                if analysis.get('status') == 'success':
                    results['analyses'].append({
                        'filename': file.filename,
                        **analysis
                    })
                else:
                    results['errors'].append({
                        'filename': file.filename,
                        'error': analysis.get('error', 'Unknown error')
                    })
                
                # Clean up
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
            except Exception as e:
                logger.error(f"Error analyzing {file.filename}: {e}")
                results['errors'].append({
                    'filename': file.filename,
                    'error': str(e)
                })
        
        results['successful'] = len(results['analyses'])
        results['failed'] = len(results['errors'])
        
        return convert_to_serializable(results)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch_analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Check if image analysis service is available"""
    try:
        analyzer = get_analyzer()
        return {
            'status': 'available',
            'service': 'Phase 4 Image Analysis (M8)',
            'model': 'ResNet50 CNN',
            'device': analyzer.device,
            'pathologies_supported': [
                'Normal', 'Caries', 'Periapical_Lesion', 'Bone_Loss',
                'Abscess', 'Fracture', 'Restoration', 'Implant'
            ],
            'regions_supported': [
                'Anterior_Upper', 'Anterior_Lower', 'Premolar_Upper',
                'Premolar_Lower', 'Molar_Upper', 'Molar_Lower'
            ],
            'bone_types': ['D1_Very_Dense', 'D2_Dense', 'D3_Moderate', 'D4_Low_Density']
        }
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        raise HTTPException(status_code=503, detail=str(e))
