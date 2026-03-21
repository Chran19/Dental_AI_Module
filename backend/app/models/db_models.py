"""
SQLAlchemy ORM Models
Maps to the production database schema defined in SRS §4.2 and Module 1 §9.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ═════════════════════════════════════════════════════════════════════════════════
#  USERS TABLE  (SRS §4.2)
# ═════════════════════════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum("Doctor", "Admin", name="user_role_enum"),
        nullable=False,
        default="Doctor",
    )
    license_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    patients: Mapped[list["Patient"]] = relationship(back_populates="doctor", lazy="selectin")
    clinical_cases: Mapped[list["ClinicalCase"]] = relationship(back_populates="doctor", lazy="selectin")


# ═════════════════════════════════════════════════════════════════════════════════
#  PATIENTS TABLE  (SRS §4.2)
# ═════════════════════════════════════════════════════════════════════════════════

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    dob: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    gender: Mapped[str] = mapped_column(
        SAEnum("Male", "Female", "Other", name="gender_enum"),
        nullable=False,
    )
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    medical_history: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    doctor: Mapped["User"] = relationship(back_populates="patients")
    clinical_cases: Mapped[list["ClinicalCase"]] = relationship(back_populates="patient", lazy="selectin")
    images: Mapped[list["Image"]] = relationship(back_populates="patient", lazy="selectin")
    implant_plans: Mapped[list["ImplantPlan"]] = relationship(back_populates="patient", lazy="selectin")


# ═════════════════════════════════════════════════════════════════════════════════
#  CLINICAL CASES TABLE  (SRS §4.2 + Module 1 §9 DB Mapping)
# ═════════════════════════════════════════════════════════════════════════════════

class ClinicalCase(Base):
    """
    Central table for clinical cases. Stores Module 1 output JSON
    and denormalized fields for indexing/filtering.
    """
    __tablename__ = "clinical_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # ── Module 1 Output ──────────────────────────────────────────────────────
    clinical_input_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Complete Module 1 output JSON"
    )
    chief_complaint: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Denormalized for search/indexing"
    )
    urgency_flag: Mapped[str | None] = mapped_column(
        SAEnum("Low", "Medium", "High", name="urgency_flag_enum"),
        nullable=True,
        index=True,
        comment="Indexed for dashboard filtering",
    )
    input_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ── Module 2 Output (Risk Engine) ────────────────────────────────────────
    risk_assessment_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Complete Module 2 output JSON"
    )
    risk_level: Mapped[str | None] = mapped_column(
        SAEnum("Low", "Medium", "High", "Critical", name="risk_level_enum"),
        nullable=True,
        index=True,
    )
    complexity_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complexity_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    alert_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    immediate_attention: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, index=True
    )
    implant_feasibility: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── AI Diagnosis (Module 3) ──────────────────────────────────────────────
    ai_diagnosis_log: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Module 3 diagnosis output"
    )

    # ── Investigation & Imaging (Module 4) ────────────────────────────────────
    investigation_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Module 4 investigation recommendations output"
    )
    investigations_completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ── Treatment Suggestion (Module 5) ───────────────────────────────────────
    treatment_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Module 5 treatment suggestions output"
    )
    contraindications_flagged: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ── Explainability & Audit (Module 6) ─────────────────────────────────────
    explainability_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Module 6 explanation report output"
    )
    clinical_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status & Timestamps ──────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        SAEnum("Draft", "Validated", "Analyzed", "Confirmed", name="case_status_enum"),
        nullable=False,
        default="Draft",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="clinical_cases")
    doctor: Mapped["User"] = relationship(back_populates="clinical_cases")
    images: Mapped[list["Image"]] = relationship(back_populates="clinical_case", lazy="selectin")


# ═════════════════════════════════════════════════════════════════════════════════
#  IMAGES TABLE  (SRS §4.2)
# ═════════════════════════════════════════════════════════════════════════════════

class Image(Base):
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=True
    )
    modality: Mapped[str] = mapped_column(
        SAEnum("CBCT", "Radiograph", "Photo", "STL", "Other", name="image_modality_enum"),
        nullable=False,
        default="Other"
    )
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, comment="Local filesystem path")
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # dcm, stl, jpg, png
    file_size_mb: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="images")
    clinical_case: Mapped["ClinicalCase"] = relationship(back_populates="images")


# ═════════════════════════════════════════════════════════════════════════════════
#  IMPLANT PLANS TABLE  (SRS §4.2)
# ═════════════════════════════════════════════════════════════════════════════════

class ImplantPlan(Base):
    __tablename__ = "implant_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=True
    )
    tooth_site: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Clinical Data
    bone_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    bone_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    implant_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    diameter: Mapped[float | None] = mapped_column(Float, nullable=True)
    length: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Workflow Tracking
    status: Mapped[str] = mapped_column(
        SAEnum("Draft", "Final", name="implant_plan_status_enum", create_type=False),
        nullable=False,
        default="Draft",
    )
    clinical_stage: Mapped[str] = mapped_column(
        SAEnum("Planning", "Surgery_Scheduled", "Implant_Placed", "Osseointegration", 
               "Restoration_Phase", "Completed", "Failed", name="implant_stage_enum"),
        nullable=False,
        default="Planning"
    )
    surgery_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    restoration_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    risk_flags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="implant_plans")


# ═════════════════════════════════════════════════════════════════════════════════
#  AUDIT LOG TABLE  (SRS NFR §5.5)
# ═════════════════════════════════════════════════════════════════════════════════

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "ClinicalCase"
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
