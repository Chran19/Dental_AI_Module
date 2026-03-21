"""
Image Service
Handles file uploads, storage, and database records for medical images.
"""
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.db_models import Image
from app.schemas.images import ImageModality

class ImageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_image(
        self,
        file: UploadFile,
        patient_id: uuid.UUID,
        modality: ImageModality,
        case_id: uuid.UUID | None = None,
        notes: str | None = None
    ) -> Image:
        # Validate file size
        # Note: Content-Length header is checked by middleware, but actual stream size could verify.
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Create patient submodule if needed
        patient_dir = self.upload_dir / str(patient_id)
        patient_dir.mkdir(exist_ok=True)
        
        file_path = patient_dir / unique_filename
        
        # Save file (blocking I/O, acceptable for MVP)
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not save file: {str(e)}"
            )
            
        # calculate size in MB
        size_mb = len(contents) / (1024 * 1024)
        
        # Create DB record
        db_image = Image(
            patient_id=patient_id,
            case_id=case_id,
            modality=modality,
            file_url=f"/static/uploads/{patient_id}/{unique_filename}", # Virtual URL
            file_path=str(file_path),
            file_type=file_ext.strip('.').lower(),
            file_size_mb=round(size_mb, 2),
            notes=notes,
            upload_date=datetime.now(timezone.utc)
        )
        
        self.db.add(db_image)
        await self.db.commit()
        await self.db.refresh(db_image)
        
        return db_image

    async def get_images_by_patient(self, patient_id: uuid.UUID):
        stmt = select(Image).where(Image.patient_id == patient_id).order_by(Image.upload_date.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_image(self, image_id: uuid.UUID) -> Image | None:
        stmt = select(Image).where(Image.id == image_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
