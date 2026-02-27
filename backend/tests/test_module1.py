"""
Module 1 — Unit Tests for Clinical Input Processing
Tests validation rules (§4.1), cross-field rules (§4.2),
sanitization (§4.3), computed flags (§5.3), and API endpoint (§7).
"""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.enums import (
    Gender,
    JawRegion,
    SmokingStatus,
    SwellingGrade,
    UrgencyFlag,
)
from app.schemas.clinical_input import ClinicalInputRequest
from app.services.clinical_input_service import ClinicalInputService
from app.services.sanitization import sanitize_string, strip_html


# ═════════════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═════════════════════════════════════════════════════════════════════════════════

def _valid_payload() -> dict:
    """Returns a minimal valid payload for Module 1."""
    return {
        "patient_id": str(uuid.uuid4()),
        "age": 54,
        "gender": "Male",
        "weight_kg": 72.5,
        "systemic_conditions": ["Diabetes_Type2"],
        "allergies": ["Penicillin"],
        "current_medications": ["Metformin 500mg"],
        "bleeding_disorder": False,
        "immunocompromised": False,
        "smoking_status": "Current_Smoker",
        "bisphosphonate_therapy": False,
        "radiation_therapy_head_neck": False,
        "chief_complaint": "Patient reports pain in lower right molar region for 3 days",
        "symptoms": ["Toothache", "Swelling_Localized"],
        "symptom_duration_days": 3,
        "symptom_onset": "Gradual",
        "pain_level": 7,
        "swelling_grade": "Moderate",
        "fever_present": True,
        "temperature_celsius": 38.5,
        "lymphadenopathy": True,
        "tooth_mobility_grade": "Grade_1",
        "percussion_test": "Positive_Severe",
        "vitality_test": "Non_Vital",
        "probing_depth_mm": 6.5,
        "tooth_site": "36",
        "jaw_region": "Posterior_Mandible",
        "bone_height_mm": 8.5,
        "bone_width_mm": 6.0,
        "bone_density": "D3",
        "adjacent_teeth_status": "Healthy",
        "sinus_proximity_mm": None,
        "nerve_proximity_mm": 3.5,
        "clinical_notes": "Patient anxious. Previous failed RCT on #36.",
    }


# ═════════════════════════════════════════════════════════════════════════════════
#  SANITIZATION TESTS  (§4.3)
# ═════════════════════════════════════════════════════════════════════════════════

class TestSanitization:
    """Tests for S-01 through S-05."""

    def test_s01_trim_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_s02_strip_html_tags(self):
        assert strip_html("<b>bold</b> text") == "bold text"
        assert strip_html('<script>alert("xss")</script>') == 'alert("xss")'

    def test_s02_sanitize_rejects_script(self):
        with pytest.raises(ValueError, match="unsafe"):
            sanitize_string("<script>alert('xss')</script>")

    def test_s03_sql_injection_detected(self):
        with pytest.raises(ValueError, match="unsafe"):
            sanitize_string("'; DROP TABLE patients; --")

    def test_s04_unicode_normalization(self):
        # NFC normalization: é (decomposed) should equal é (composed)
        result = sanitize_string("caf\u0065\u0301")  # decomposed é
        assert result == "café"

    def test_sanitize_none_returns_none(self):
        assert sanitize_string(None) is None


# ═════════════════════════════════════════════════════════════════════════════════
#  FIELD-LEVEL VALIDATION TESTS  (§4.1)
# ═════════════════════════════════════════════════════════════════════════════════

class TestFieldValidation:
    """Tests for V-01 through V-16."""

    def test_v01_age_out_of_range(self):
        data = _valid_payload()
        data["age"] = 0
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v01_age_upper_bound(self):
        data = _valid_payload()
        data["age"] = 121
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v03_chief_complaint_too_short(self):
        data = _valid_payload()
        data["chief_complaint"] = "Hi"
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v04_pain_level_out_of_range(self):
        data = _valid_payload()
        data["pain_level"] = 11
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v05_empty_symptoms(self):
        data = _valid_payload()
        data["symptoms"] = []
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v08_invalid_tooth_site(self):
        data = _valid_payload()
        data["tooth_site"] = "99"
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v08_valid_tooth_site(self):
        data = _valid_payload()
        data["tooth_site"] = "16"
        req = ClinicalInputRequest(**data)
        assert req.tooth_site == "16"

    def test_v09_bone_height_out_of_range(self):
        data = _valid_payload()
        data["bone_height_mm"] = 35.0
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v13_too_many_allergies(self):
        data = _valid_payload()
        data["allergies"] = [f"Allergy_{i}" for i in range(25)]
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)

    def test_v16_duration_out_of_range(self):
        data = _valid_payload()
        data["symptom_duration_days"] = 4000
        with pytest.raises(Exception):
            ClinicalInputRequest(**data)


# ═════════════════════════════════════════════════════════════════════════════════
#  CROSS-FIELD VALIDATION TESTS  (§4.2)
# ═════════════════════════════════════════════════════════════════════════════════

class TestCrossFieldValidation:
    """Tests for XV-01 through XV-05."""

    def test_v07_fever_without_temperature(self):
        data = _valid_payload()
        data["fever_present"] = True
        data["temperature_celsius"] = None
        with pytest.raises(Exception, match="temperature"):
            ClinicalInputRequest(**data)

    def test_v07_no_fever_no_temperature_ok(self):
        data = _valid_payload()
        data["fever_present"] = False
        data["temperature_celsius"] = None
        req = ClinicalInputRequest(**data)
        assert req.fever_present is False


# ═════════════════════════════════════════════════════════════════════════════════
#  COMPUTED FLAGS TESTS  (§5.3)
# ═════════════════════════════════════════════════════════════════════════════════

class TestComputedFlags:
    """Tests for urgency flags and risk flags."""

    def test_urgency_high(self):
        """HIGH: fever + Severe swelling + pain ≥ 8"""
        data = _valid_payload()
        data["fever_present"] = True
        data["temperature_celsius"] = 39.0
        data["swelling_grade"] = "Severe"
        data["pain_level"] = 9
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.urgency_flag == UrgencyFlag.HIGH

    def test_urgency_medium_by_pain(self):
        """MEDIUM: pain ≥ 6"""
        data = _valid_payload()
        data["fever_present"] = False
        data["temperature_celsius"] = None
        data["swelling_grade"] = "None"
        data["pain_level"] = 7
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.urgency_flag == UrgencyFlag.MEDIUM

    def test_urgency_low(self):
        """LOW: pain < 6, swelling None/Mild, no fever"""
        data = _valid_payload()
        data["fever_present"] = False
        data["temperature_celsius"] = None
        data["swelling_grade"] = "Mild"
        data["pain_level"] = 3
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.urgency_flag == UrgencyFlag.LOW

    def test_bisphosphonate_risk_flag(self):
        """XV-03: bisphosphonate + implant data → risk flag"""
        data = _valid_payload()
        data["bisphosphonate_therapy"] = True
        data["bone_height_mm"] = 10.0
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.bisphosphonate_risk is True

    def test_age_contraindication(self):
        """XV-04: age < 18 + implant data → contraindication"""
        data = _valid_payload()
        data["age"] = 15
        data["bone_height_mm"] = 12.0
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.age_contraindication is True

    def test_implant_data_present(self):
        """implant_data_present when any bone field is provided"""
        data = _valid_payload()
        data["bone_height_mm"] = None
        data["bone_width_mm"] = None
        data["bone_density"] = None
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.implant_data_present is False

    def test_implant_data_present_with_bone_density(self):
        data = _valid_payload()
        data["bone_height_mm"] = None
        data["bone_width_mm"] = None
        data["bone_density"] = "D3"
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        assert output.computed_flags.implant_data_present is True


# ═════════════════════════════════════════════════════════════════════════════════
#  OUTPUT JSON STRUCTURE TESTS  (§5.1)
# ═════════════════════════════════════════════════════════════════════════════════

class TestOutputStructure:
    """Verify the output JSON matches the Module 1 contract."""

    def test_output_has_all_required_sections(self):
        data = _valid_payload()
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())

        assert output.module == "M1_Clinical_Input"
        assert output.version == "1.0"
        assert output.generated_at is not None
        assert output.case_id is not None
        assert output.patient_id is not None
        assert output.doctor_id is not None
        assert output.demographics is not None
        assert output.medical_history is not None
        assert output.chief_complaint is not None
        assert output.clinical_assessment is not None
        assert output.site_assessment is not None
        assert output.computed_flags is not None
        assert output.validation_status is not None
        assert output.validation_status.is_valid is True

    def test_output_serializes_to_json(self):
        data = _valid_payload()
        req = ClinicalInputRequest(**data)
        svc = ClinicalInputService()
        output = svc.process(req, uuid.uuid4())
        json_str = output.model_dump_json()
        assert '"M1_Clinical_Input"' in json_str


# ═════════════════════════════════════════════════════════════════════════════════
#  API ENDPOINT TESTS  (§7)
# ═════════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
class TestAPIEndpoint:
    """Integration tests for POST /api/clinical-input/validate."""

    async def test_valid_payload_returns_200(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/clinical-input/validate",
                json=_valid_payload(),
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["module"] == "M1_Clinical_Input"

    async def test_missing_required_field_returns_422(self):
        payload = _valid_payload()
        del payload["chief_complaint"]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/clinical-input/validate",
                json=payload,
            )
        assert resp.status_code == 422
        body = resp.json()
        assert body["status"] == "error"
        assert any("chief_complaint" in e["field"] for e in body["errors"])

    async def test_invalid_enum_returns_422(self):
        payload = _valid_payload()
        payload["gender"] = "InvalidGender"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/clinical-input/validate",
                json=payload,
            )
        assert resp.status_code == 422

    async def test_health_check(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
