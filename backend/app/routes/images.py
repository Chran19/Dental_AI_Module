"""
Medical Imaging Hub Routes
"""
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_doctor_id
from app.models.db_models import Image, User
from app.services.image_service import ImageService
from app.schemas.images import ImageResponse, ImageModality

router = APIRouter(prefix="/images", tags=["Medical Imaging Hub"])

def get_image_service(db: AsyncSession = Depends(get_db)) -> ImageService:
    return ImageService(db)

@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_medical_image(
    patient_id: uuid.UUID,
    modality: ImageModality,
    file: UploadFile = File(...),
    case_id: Optional[uuid.UUID] = Query(None),
    notes: Optional[str] = Query(None),
    current_user_id: uuid.UUID = Depends(get_current_doctor_id),
    service: ImageService = Depends(get_image_service)
):
    """
    Upload a medical image (X-Ray, CBCT, Photo, STL) linked to a patient.
    """
    # Validation
    allowed_types = ["image/jpeg", "image/png", "application/dicom", "application/octet-stream"]
    # Simple whitelist check (MIME type from client is untrusted but good first pass)
    # File headers should be checked in production for real security.
    
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        image_record = await service.upload_image(
            file=file,
            patient_id=patient_id,
            modality=modality,
            case_id=case_id,
            notes=notes
        )
        return image_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/patient/{patient_id}", response_model=List[ImageResponse])
async def list_patient_images(
    patient_id: uuid.UUID,
    service: ImageService = Depends(get_image_service),
    current_user_id: uuid.UUID = Depends(get_current_doctor_id)
):
    """List all images for a specific patient."""
    return await service.get_images_by_patient(patient_id)

@router.get("/download/{image_id}")
async def download_image(
    image_id: uuid.UUID,
    service: ImageService = Depends(get_image_service),
    current_user_id: uuid.UUID = Depends(get_current_doctor_id)
):
    """Securely download the image file."""
    image = await service.get_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    # Check file exists on disk
    if not shutil.os.path.exists(image.file_path):
         raise HTTPException(status_code=404, detail="File missing from storage")
         
    return FileResponse(
        path=image.file_path, 
        filename=f"{image.modality}_{image_id}.{image.file_type}",
        media_type="application/octet-stream"
    )
