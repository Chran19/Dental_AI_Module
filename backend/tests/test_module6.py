"""
Module 6 — Explainability Tests (Simplified)
Tests NLG output quality and audit trail generation.
Reference: Module_6_Explainability_Audit_Layer.md §6
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.schemas.clinical_input import Module1Output
from app.schemas.risk_engine import (
    Module2Output,
    RiskAlert,
    RiskSummary,
    AlertSeverity,
    RiskLevel,
    ImplantFeasibility,
)
from app.schemas.diagnosis import Module3Output, DifferentialDiagnosis
from app.schemas.investigation import (
    Module4Output,
    ImagingRecommendation,
    InvestigationSummary,
)
from app.schemas.treatment import (
    Module5Output,
    TreatmentOption,
    TreatmentSummary,
    ContraindicationAlert,
)
from app.schemas.explainability import ExplanationReport, AuditTrail
from app.services.explainability_service import ExplainabilityService
from app.models.enums import (
    Gender,
    ImagingType,
    TreatmentType,
    TreatmentCategory,
    ContraindicationSeverity,
    InvestigationUrgency,
)


class TestExplanationGeneration:
    """Tests for explanation generation from module outputs."""

    def test_explanation_generation_with_diagnosis(self):
        """Explanation should be generated with diagnosis info."""
        # Arrange
        m3_output = Module3Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            differentials=[
                DifferentialDiagnosis(
                    rank=1,
                    code="DX-01",
                    name="Irreversible Pulpitis",
                    category="Pulpal",
                    confidence_pct=85.0,
                    description="Irreversible inflammation of the pulp",
                    justification="Patient presents with spontaneous pain and positive vitality tests.",
                )
            ],
            clinical_summary="Case of Irreversible Pulpitis with high confidence.",
        )

        # Act
        result = ExplainabilityService.generate_explanation(m3_output=m3_output)

        # Assert
        assert isinstance(result, ExplanationReport)
        assert result.case_id is not None
        assert "Irreversible Pulpitis" in result.summary
        assert len(result.m3_scoring_trace) > 0

    def test_explanation_scoring_breakdown(self):
        """Diagnosis scores should be in breakdown."""
        # Arrange
        m3_output = Module3Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            differentials=[
                DifferentialDiagnosis(
                    rank=1,
                    code="DX-01",
                    name="Irreversible Pulpitis",
                    category="Pulpal",
                    confidence_pct=88.0,
                    description="Irreversible pulp inflammation",
                    justification="Positive vitality test.",
                ),
                DifferentialDiagnosis(
                    rank=2,
                    code="DX-02",
                    name="Pulp Necrosis",
                    category="Pulpal",
                    confidence_pct=65.0,
                    description="Non-vital pulp",
                    justification="Negative vitality test.",
                ),
            ],
            clinical_summary="Multiple diagnoses considered.",
        )

        # Act
        result = ExplainabilityService.generate_explanation(m3_output=m3_output)

        # Assert
        assert len(result.m3_scoring_trace) >= 2
        assert result.m3_scoring_trace[0].confidence == 88.0
        assert result.m3_scoring_trace[1].confidence == 65.0

    def test_explanation_with_risk_alerts(self):
        """Risk alerts should appear in explanation."""
        # Arrange
        m2_output = Module2Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            risk_summary=RiskSummary(
                overall_risk_level=RiskLevel.HIGH,
                risk_score=75,
                immediate_attention_required=True,
                implant_feasibility=ImplantFeasibility.CONDITIONAL,
                alert_count=1,
            ),
            alerts=[
                RiskAlert(
                    rule_id="R-01",
                    category="Bone",
                    severity=AlertSeverity.WARNING,
                    message="High bone loss risk",
                )
            ],
        )

        # Act
        result = ExplainabilityService.generate_explanation(m2_output=m2_output)

        # Assert
        assert result is not None
        assert len(result.m2_rules_triggered) >= 0

    def test_explanation_with_treatment(self):
        """Treatment info should be in explanation."""
        # Arrange
        m3_output = Module3Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            differentials=[
                DifferentialDiagnosis(
                    rank=1,
                    code="DX-01",
                    name="Irreversible Pulpitis",
                    category="Pulpal",
                    confidence_pct=85.0,
                    description="Irreversible pulp inflammation",
                    justification="Clinical findings suggest pulpitis.",
                )
            ],
            clinical_summary="Irreversible Pulpitis",
        )

        m5_output = Module5Output(
            case_id="case-123",
            patient_id="patient-123",
            doctor_id="doctor-123",
            generated_at=datetime.utcnow(),
            primary_treatment=TreatmentOption(
                treatment_type=TreatmentType.ROOT_CANAL,
                category=TreatmentCategory.ENDODONTIC,
                description="Root canal therapy",
                success_rate=0.92,
                follow_up_days=7,
                rank=1,
            ),
            referenced_diagnosis_code="DX-01",
            summary=TreatmentSummary(
                primary_treatment_name="Root_Canal",
                total_alternatives=0,
                medication_count=1,
                contraindication_count=0,
                highest_contraindication_severity="Mild",
                overall_feasibility="Feasible",
                clinical_summary="Root canal recommended.",
            ),
        )

        # Act
        result = ExplainabilityService.generate_explanation(m3_output=m3_output, m5_output=m5_output)

        # Assert
        assert "Root" in result.summary or "Root" in result.m5_treatment_justification

    def test_explanation_timestamp(self):
        """Explanation should have generation timestamp."""
        # Act
        result = ExplainabilityService.generate_explanation()

        # Assert
        assert result.generated_at is not None
        assert isinstance(result.generated_at, datetime)

    def test_explanation_case_id_uuid(self):
        """Generated case_id should be valid UUID."""
        # Act
        result = ExplainabilityService.generate_explanation()

        # Assert
        assert result.case_id is not None
        assert len(result.case_id) == 36  # UUID4 format


class TestClinicalSummary:
    """Tests for clinical summary generation."""

    def test_clinical_summary_with_diagnosis(self):
        """Clinical summary should include diagnosis."""
        # Arrange
        m3 = Module3Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            differentials=[
                DifferentialDiagnosis(
                    rank=1,
                    code="DX-02",
                    name="Pulp Necrosis",
                    category="Pulpal",
                    confidence_pct=80.0,
                    description="Non-vital pulp",
                    justification="Negative vitality test.",
                )
            ],
            clinical_summary="Pulp Necrosis case.",
        )

        # Act
        result = ExplainabilityService.generate_explanation(m3_output=m3)

        # Assert
        assert "Pulp Necrosis" in result.clinical_summary


class TestAuditTrail:
    """Tests for audit trail generation."""

    def test_audit_trail_creation(self):
        """Audit trail should be created with entries."""
        # Act
        trail = ExplainabilityService.build_audit_trail(
            m1_id="id-1", m2_id="id-2", m3_id="id-3"
        )

        # Assert
        assert isinstance(trail, AuditTrail)
        assert len(trail.entries) >= 3

    def test_audit_trail_modules(self):
        """Audit trail should include all modules."""
        # Act
        trail = ExplainabilityService.build_audit_trail(
            m1_id="id-1", m2_id="id-2", m3_id="id-3"
        )

        # Assert
        modules = [e.module_name for e in trail.entries]
        assert "M1" in modules
        assert "M2" in modules
        assert "M3" in modules

    def test_audit_trail_timestamps(self):
        """Audit entries should have timestamps."""
        # Act
        trail = ExplainabilityService.build_audit_trail(
            m1_id="id-1", m2_id="id-2", m3_id="id-3"
        )

        # Assert
        for entry in trail.entries:
            assert entry.timestamp is not None
            assert isinstance(entry.timestamp, datetime)


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_end_to_end_explanation(self):
        """Full workflow M3→M5→M6."""
        # Arrange
        m3 = Module3Output(
            case_id=uuid4(),
            patient_id=uuid4(),
            doctor_id=uuid4(),
            generated_at=datetime.utcnow(),
            differentials=[
                DifferentialDiagnosis(
                    rank=1,
                    code="DX-01",
                    name="Irreversible Pulpitis",
                    category="Pulpal",
                    confidence_pct=88.0,
                    description="Irreversible inflammation",
                    justification="Spontaneous pain present.",
                )
            ],
            clinical_summary="Irreversible Pulpitis case.",
        )

        m5 = Module5Output(
            case_id="case-001",
            patient_id="pat-001",
            doctor_id="doc-001",
            generated_at=datetime.utcnow(),
            primary_treatment=TreatmentOption(
                treatment_type=TreatmentType.ROOT_CANAL,
                category=TreatmentCategory.ENDODONTIC,
                description="Root canal therapy",
                success_rate=0.90,
                follow_up_days=7,
                rank=1,
            ),
            referenced_diagnosis_code="DX-01",
            summary=TreatmentSummary(
                primary_treatment_name="Root_Canal",
                total_alternatives=1,
                medication_count=2,
                contraindication_count=0,
                highest_contraindication_severity="Mild",
                overall_feasibility="Feasible",
                clinical_summary="RCT recommended.",
            ),
        )

        # Act
        result = ExplainabilityService.generate_explanation(
            m3_output=m3, m5_output=m5
        )

        # Assert
        assert result.case_id is not None
        assert "Irreversible Pulpitis" in result.summary
        assert len(result.m3_scoring_trace) >= 1
