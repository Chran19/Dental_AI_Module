"""
Module 3 — Unit Tests for Differential Diagnosis Engine
Tests symptom matching, findings scoring, onset/duration,
M2 modifier, contradictions, ranking, and the API endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.diagnosis import DiagnosisRequest
from app.services.diagnosis_service import DiagnosisService


# ═════════════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═════════════════════════════════════════════════════════════════════════════════

_CASE_ID = str(uuid.uuid4())
_PATIENT_ID = str(uuid.uuid4())
_DOCTOR_ID = str(uuid.uuid4())
_NOW = datetime.now(timezone.utc).isoformat()


def _m1(**overrides) -> dict:
    """Base M1 payload."""
    base = {
        "module": "M1_Clinical_Input",
        "version": "1.0",
        "generated_at": _NOW,
        "case_id": _CASE_ID,
        "patient_id": _PATIENT_ID,
        "doctor_id": _DOCTOR_ID,
        "demographics": {"age": 45, "gender": "Male", "weight_kg": 75.0},
        "medical_history": {
            "systemic_conditions": ["None"],
            "allergies": [],
            "current_medications": [],
            "bleeding_disorder": False,
            "immunocompromised": False,
            "smoking_status": "Non-Smoker",
            "bisphosphonate_therapy": False,
            "radiation_therapy_head_neck": False,
        },
        "chief_complaint": {
            "description": "Toothache on lower right",
            "symptoms": ["Toothache"],
            "duration_days": 3,
            "onset": "Gradual",
        },
        "clinical_assessment": {
            "pain_level": 5,
            "swelling_grade": "None",
            "fever": {"present": False},
            "lymphadenopathy": False,
        },
        "site_assessment": {
            "tooth_site": "36",
            "jaw_region": "Posterior_Mandible",
        },
        "clinical_notes": "",
        "computed_flags": {
            "urgency_flag": "Low",
            "bisphosphonate_risk": False,
            "radiation_risk": False,
            "age_contraindication": False,
            "implant_data_present": False,
        },
        "validation_status": {"is_valid": True, "errors": [], "warnings": []},
    }
    _deep_merge(base, overrides)
    return base


def _m2(**overrides) -> dict:
    """Base M2 payload (low risk, no alerts)."""
    base = {
        "module": "M2_Risk_Engine",
        "version": "1.0",
        "generated_at": _NOW,
        "case_id": _CASE_ID,
        "patient_id": _PATIENT_ID,
        "doctor_id": _DOCTOR_ID,
        "risk_summary": {
            "overall_risk_level": "Low",
            "risk_score": 10,
            "immediate_attention_required": False,
            "implant_feasibility": "Insufficient_Data",
            "alert_count": 0,
        },
        "alerts": [],
        "infection_analysis": None,
        "surgical_complexity": None,
    }
    _deep_merge(base, overrides)
    return base


def _deep_merge(base: dict, overrides: dict):
    for key, value in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _payload(**m1_overrides) -> dict:
    """Full M3 request payload with optional M1 overrides."""
    return {"m1": _m1(**m1_overrides), "m2": _m2()}


def _payload_full(m1_overrides: dict | None = None, m2_overrides: dict | None = None) -> dict:
    return {
        "m1": _m1(**(m1_overrides or {})),
        "m2": _m2(**(m2_overrides or {})),
    }


@pytest.fixture
def service():
    return DiagnosisService()


def _make_request(**m1_overrides) -> DiagnosisRequest:
    return DiagnosisRequest(**_payload(**m1_overrides))


def _make_request_full(
    m1_overrides: dict | None = None,
    m2_overrides: dict | None = None,
) -> DiagnosisRequest:
    return DiagnosisRequest(**_payload_full(m1_overrides, m2_overrides))


# ═════════════════════════════════════════════════════════════════════════════════
#  BASIC SMOKE TESTS
# ═════════════════════════════════════════════════════════════════════════════════

class TestBasicDiagnosis:

    def test_returns_differentials(self, service):
        """Should return at least 1 differential for any input with symptoms."""
        req = _make_request()
        result = service.diagnose(req)
        assert len(result.differentials) >= 1
        assert result.profiles_evaluated > 0

    def test_max_results_respected(self, service):
        """max_results=2 should cap output at 2."""
        req = DiagnosisRequest(**{**_payload(), "max_results": 2})
        result = service.diagnose(req)
        assert len(result.differentials) <= 2

    def test_confidence_range(self, service):
        """All confidence values should be 0-100."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Spontaneous_Pain", "Swelling_Localized"],
                "description": "Severe pain",
                "duration_days": 2,
            },
        )
        result = service.diagnose(req)
        for dx in result.differentials:
            assert 0 <= dx.confidence_pct <= 100

    def test_ranks_sequential(self, service):
        """Ranks should be 1, 2, 3, ..."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Swelling_Localized", "Pus_Discharge"],
                "description": "Pain and swelling",
                "duration_days": 3,
            },
        )
        result = service.diagnose(req)
        for i, dx in enumerate(result.differentials, start=1):
            assert dx.rank == i

    def test_clinical_summary_populated(self, service):
        """Clinical summary should contain patient info."""
        req = _make_request()
        result = service.diagnose(req)
        assert "45-year-old" in result.clinical_summary
        assert "male" in result.clinical_summary.lower()


# ═════════════════════════════════════════════════════════════════════════════════
#  SPECIFIC DIAGNOSIS MATCHING
# ═════════════════════════════════════════════════════════════════════════════════

class TestDiagnosisMatching:

    def test_irreversible_pulpitis_profile(self, service):
        """Classic irreversible pulpitis presentation → DX-01 should rank high."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Spontaneous_Pain", "Thermal_Sensitivity_Hot"],
                "description": "Severe spontaneous throbbing pain, worse at night",
                "duration_days": 3,
                "onset": "Sudden",
            },
            clinical_assessment={
                "pain_level": 8,
                "swelling_grade": "None",
                "fever": {"present": False},
                "lymphadenopathy": False,
                "vitality_test": "Vital",
                "percussion_test": "Positive_Severe",
            },
        )
        result = service.diagnose(req)
        codes = [dx.code for dx in result.differentials]
        assert "DX-01" in codes
        # Should be top 2
        dx01_rank = next(dx.rank for dx in result.differentials if dx.code == "DX-01")
        assert dx01_rank <= 2

    def test_acute_periapical_abscess(self, service):
        """Acute abscess presentation → DX-03 should rank #1."""
        req = _make_request(
            chief_complaint={
                "symptoms": [
                    "Toothache", "Spontaneous_Pain", "Swelling_Localized",
                    "Pus_Discharge", "Pain_On_Biting",
                ],
                "description": "Severe pain with swelling and pus",
                "duration_days": 2,
                "onset": "Sudden",
            },
            clinical_assessment={
                "pain_level": 8,
                "swelling_grade": "Moderate",
                "fever": {"present": True, "temperature_celsius": 38.5},
                "lymphadenopathy": True,
                "vitality_test": "Non_Vital",
                "percussion_test": "Positive_Severe",
                "tooth_mobility_grade": "Grade_1",
            },
        )
        result = service.diagnose(req)
        assert result.differentials[0].code == "DX-03"
        assert result.differentials[0].confidence_pct >= 70

    def test_periodontal_abscess(self, service):
        """Deep pocket + bleeding + vital → DX-05 should be top 2."""
        req = _make_request(
            chief_complaint={
                "symptoms": [
                    "Swelling_Localized", "Gum_Bleeding", "Pus_Discharge",
                    "Tooth_Mobility", "Pain_On_Biting",
                ],
                "description": "Gum swelling with bleeding",
                "duration_days": 5,
                "onset": "Gradual",
            },
            clinical_assessment={
                "pain_level": 6,
                "swelling_grade": "Moderate",
                "fever": {"present": False},
                "lymphadenopathy": False,
                "vitality_test": "Vital",
                "percussion_test": "Positive_Mild",
                "tooth_mobility_grade": "Grade_2",
                "probing_depth_mm": 7.0,
            },
        )
        result = service.diagnose(req)
        codes = [dx.code for dx in result.differentials[:2]]
        assert "DX-05" in codes

    def test_cellulitis_with_spreading_infection(self, service):
        """Diffuse swelling + trismus + high fever → DX-06 cellulitis."""
        req = _make_request_full(
            m1_overrides={
                "chief_complaint": {
                    "symptoms": [
                        "Swelling_Diffuse", "Swelling_Extraoral",
                        "Limited_Mouth_Opening", "Difficulty_Chewing",
                    ],
                    "description": "Severe spreading swelling",
                    "duration_days": 2,
                    "onset": "Sudden",
                },
                "clinical_assessment": {
                    "pain_level": 9,
                    "swelling_grade": "Severe",
                    "fever": {"present": True, "temperature_celsius": 39.0},
                    "lymphadenopathy": True,
                    "percussion_test": "Positive_Severe",
                },
            },
            m2_overrides={
                "risk_summary": {
                    "overall_risk_level": "Critical",
                    "risk_score": 82,
                    "immediate_attention_required": True,
                    "implant_feasibility": "Insufficient_Data",
                    "alert_count": 3,
                },
                "infection_analysis": {
                    "pattern": "Spreading_Infection",
                    "indicators": ["Swelling_Diffuse", "Fever", "Lymphadenopathy"],
                    "spread_risk": "High",
                },
                "surgical_complexity": {
                    "score": 55,
                    "complexity_class": "Complex",
                    "factors": ["Severe swelling"],
                },
            },
        )
        result = service.diagnose(req)
        assert result.differentials[0].code == "DX-06"

    def test_chronic_periapical_with_fistula(self, service):
        """Fistula + non-vital + gradual → DX-04 chronic periapical."""
        req = _make_request_full(
            m1_overrides={
                "chief_complaint": {
                    "symptoms": ["Fistula_Sinus_Tract", "Bad_Breath"],
                    "description": "Draining fistula for weeks",
                    "duration_days": 30,
                    "onset": "Gradual",
                },
                "clinical_assessment": {
                    "pain_level": 2,
                    "swelling_grade": "None",
                    "fever": {"present": False},
                    "lymphadenopathy": False,
                    "vitality_test": "Non_Vital",
                },
            },
            m2_overrides={
                "infection_analysis": {
                    "pattern": "Chronic_Infection",
                    "indicators": ["Fistula_Sinus_Tract"],
                    "spread_risk": "Low",
                },
            },
        )
        result = service.diagnose(req)
        codes = [dx.code for dx in result.differentials[:2]]
        assert "DX-04" in codes

    def test_reversible_pulpitis(self, service):
        """Cold sensitivity only, vital, low pain → DX-07."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Thermal_Sensitivity_Cold"],
                "description": "Sharp pain with cold drinks",
                "duration_days": 7,
                "onset": "Intermittent",
            },
            clinical_assessment={
                "pain_level": 3,
                "swelling_grade": "None",
                "fever": {"present": False},
                "lymphadenopathy": False,
                "vitality_test": "Vital",
                "percussion_test": "Negative",
            },
        )
        result = service.diagnose(req)
        codes = [dx.code for dx in result.differentials[:2]]
        assert "DX-07" in codes

    def test_tmj_disorder(self, service):
        """Jaw pain + clicking + limited opening → DX-13 TMJ."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Jaw_Pain", "Jaw_Clicking", "Limited_Mouth_Opening", "Difficulty_Chewing"],
                "description": "Jaw pain and clicking when eating",
                "duration_days": 30,
                "onset": "Gradual",
            },
            clinical_assessment={
                "pain_level": 5,
                "swelling_grade": "None",
                "fever": {"present": False},
                "lymphadenopathy": False,
                "vitality_test": "Vital",
                "percussion_test": "Negative",
            },
        )
        result = service.diagnose(req)
        assert result.differentials[0].code == "DX-13"


# ═════════════════════════════════════════════════════════════════════════════════
#  EVIDENCE & JUSTIFICATION
# ═════════════════════════════════════════════════════════════════════════════════

class TestEvidenceChain:

    def test_supporting_evidence_populated(self, service):
        """Top diagnosis should have supporting evidence."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Spontaneous_Pain", "Swelling_Localized"],
                "description": "Pain",
                "duration_days": 2,
            },
            clinical_assessment={
                "pain_level": 7,
                "swelling_grade": "Moderate",
                "fever": {"present": True, "temperature_celsius": 38.0},
                "lymphadenopathy": True,
                "vitality_test": "Non_Vital",
                "percussion_test": "Positive_Severe",
            },
        )
        result = service.diagnose(req)
        top = result.differentials[0]
        assert len(top.supporting_evidence) > 0
        assert any(e.weight == "Strong" for e in top.supporting_evidence)

    def test_contradicting_evidence_when_present(self, service):
        """Fistula present for irreversible pulpitis → should have contradiction."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Spontaneous_Pain", "Fistula_Sinus_Tract"],
                "description": "Pain with fistula",
                "duration_days": 3,
                "onset": "Sudden",
            },
            clinical_assessment={
                "pain_level": 7,
                "swelling_grade": "None",
                "fever": {"present": False},
                "vitality_test": "Vital",
                "percussion_test": "Positive_Mild",
            },
        )
        result = service.diagnose(req)
        # DX-01 should have fistula as contradicting
        dx01 = next((dx for dx in result.differentials if dx.code == "DX-01"), None)
        if dx01:
            contra_findings = [c.finding for c in dx01.contradicting_evidence]
            assert any("Fistula" in f for f in contra_findings)

    def test_justification_not_empty(self, service):
        """Every differential should have a non-empty justification."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache", "Swelling_Localized"],
                "description": "Pain and swelling",
                "duration_days": 3,
            },
        )
        result = service.diagnose(req)
        for dx in result.differentials:
            assert dx.justification
            assert len(dx.justification) > 20


# ═════════════════════════════════════════════════════════════════════════════════
#  M2 MODIFIER TESTS
# ═════════════════════════════════════════════════════════════════════════════════

class TestM2Modifiers:

    def test_spreading_infection_boosts_cellulitis(self, service):
        """M2 spreading infection should boost DX-06 ranking."""
        base_symptoms = {
            "chief_complaint": {
                "symptoms": ["Swelling_Diffuse", "Swelling_Extraoral", "Toothache"],
                "description": "Spreading swelling",
                "duration_days": 2,
                "onset": "Sudden",
            },
            "clinical_assessment": {
                "pain_level": 8,
                "swelling_grade": "Severe",
                "fever": {"present": True, "temperature_celsius": 39.0},
                "lymphadenopathy": True,
            },
        }
        # Without M2 infection data
        req_no_m2 = _make_request_full(m1_overrides=base_symptoms)
        result_no = service.diagnose(req_no_m2)

        # With M2 spreading infection
        req_m2 = _make_request_full(
            m1_overrides=base_symptoms,
            m2_overrides={
                "infection_analysis": {
                    "pattern": "Spreading_Infection",
                    "indicators": ["Swelling_Diffuse", "Fever"],
                    "spread_risk": "High",
                },
                "risk_summary": {
                    "overall_risk_level": "Critical",
                    "risk_score": 80,
                    "immediate_attention_required": True,
                    "implant_feasibility": "Insufficient_Data",
                    "alert_count": 3,
                },
            },
        )
        result_m2 = service.diagnose(req_m2)

        # DX-06 should rank better with M2 data
        dx06_rank_no = next(
            (dx.rank for dx in result_no.differentials if dx.code == "DX-06"), 99
        )
        dx06_rank_m2 = next(
            (dx.rank for dx in result_m2.differentials if dx.code == "DX-06"), 99
        )
        assert dx06_rank_m2 <= dx06_rank_no


# ═════════════════════════════════════════════════════════════════════════════════
#  API ENDPOINT TESTS
# ═════════════════════════════════════════════════════════════════════════════════

class TestDiagnosisEndpoint:

    @pytest.mark.anyio
    async def test_success(self):
        """POST /api/diagnosis/differential with valid payload → 200."""
        payload = _payload_full()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/diagnosis/differential", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["module"] == "M3_Differential_Diagnosis"
        assert "differentials" in body["data"]
        assert len(body["data"]["differentials"]) >= 1

    @pytest.mark.anyio
    async def test_invalid_payload(self):
        """POST /api/diagnosis/differential with bad data → 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/diagnosis/differential", json={"bad": "data"})
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_abscess_case_via_api(self):
        """Full abscess case through the API returns DX-03 as top."""
        payload = _payload_full(
            m1_overrides={
                "chief_complaint": {
                    "symptoms": [
                        "Toothache", "Spontaneous_Pain",
                        "Swelling_Localized", "Pus_Discharge",
                    ],
                    "description": "Severe pain with pus",
                    "duration_days": 2,
                    "onset": "Sudden",
                },
                "clinical_assessment": {
                    "pain_level": 9,
                    "swelling_grade": "Moderate",
                    "fever": {"present": True, "temperature_celsius": 38.8},
                    "lymphadenopathy": True,
                    "vitality_test": "Non_Vital",
                    "percussion_test": "Positive_Severe",
                    "tooth_mobility_grade": "Grade_1",
                },
            },
            m2_overrides={
                "risk_summary": {
                    "overall_risk_level": "High",
                    "risk_score": 65,
                    "immediate_attention_required": True,
                    "implant_feasibility": "Insufficient_Data",
                    "alert_count": 2,
                },
                "infection_analysis": {
                    "pattern": "Acute_Localized",
                    "indicators": ["Pus_Discharge", "Fever"],
                    "spread_risk": "Medium",
                },
            },
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/diagnosis/differential", json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["differentials"][0]["code"] == "DX-03"
        assert data["differentials"][0]["confidence_pct"] >= 70
        assert len(data["differentials"][0]["supporting_evidence"]) > 0
