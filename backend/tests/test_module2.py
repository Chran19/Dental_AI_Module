"""
Module 2 — Unit Tests for Rule-Based Risk Engine
Tests bone rules (R-01 to R-05), systemic rules (R-06 to R-08),
infection detection (R-09 to R-12), surgical complexity (R-13 to R-16),
composite scoring, and the API endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.risk_engine import (
    AlertSeverity,
    ComplexityClass,
    ImplantFeasibility,
    RiskEngineRequest,
    RiskLevel,
)
from app.services.risk_engine_service import RiskEngineService


# ═════════════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═════════════════════════════════════════════════════════════════════════════════

def _base_m1_payload(**overrides) -> dict:
    """Returns a valid Module 1 output payload for risk engine input."""
    base = {
        "module": "M1_Clinical_Input",
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": str(uuid.uuid4()),
        "patient_id": str(uuid.uuid4()),
        "doctor_id": str(uuid.uuid4()),
        "demographics": {"age": 54, "gender": "Male", "weight_kg": 72.5},
        "medical_history": {
            "systemic_conditions": ["Diabetes_Type2"],
            "allergies": ["Penicillin"],
            "current_medications": ["Metformin 500mg"],
            "bleeding_disorder": False,
            "immunocompromised": False,
            "smoking_status": "Current_Smoker",
            "bisphosphonate_therapy": False,
            "radiation_therapy_head_neck": False,
        },
        "chief_complaint": {
            "description": "Pain in lower right molar for 3 days",
            "symptoms": ["Toothache", "Swelling_Localized"],
            "duration_days": 3,
            "onset": "Gradual",
        },
        "clinical_assessment": {
            "pain_level": 7,
            "swelling_grade": "Moderate",
            "fever": {"present": True, "temperature_celsius": 38.5},
            "lymphadenopathy": True,
            "tooth_mobility_grade": "Grade_1",
            "percussion_test": "Positive_Severe",
            "vitality_test": "Non_Vital",
            "probing_depth_mm": 6.5,
        },
        "site_assessment": {
            "tooth_site": "36",
            "jaw_region": "Posterior_Mandible",
            "bone_height_mm": 12.0,
            "bone_width_mm": 7.0,
            "bone_density": "D2",
            "adjacent_teeth_status": "Healthy",
            "nerve_proximity_mm": 5.0,
        },
        "clinical_notes": "Patient anxious. Previous failed RCT on #36.",
        "computed_flags": {
            "urgency_flag": "Medium",
            "bisphosphonate_risk": False,
            "radiation_risk": False,
            "age_contraindication": False,
            "implant_data_present": True,
        },
        "validation_status": {"is_valid": True, "errors": [], "warnings": []},
    }
    # Apply overrides via nested merge
    _deep_merge(base, overrides)
    return base


def _deep_merge(base: dict, overrides: dict):
    """Recursively merge overrides into base dict."""
    for key, value in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _make_request(**overrides) -> RiskEngineRequest:
    """Build a RiskEngineRequest with optional overrides."""
    return RiskEngineRequest(**_base_m1_payload(**overrides))


# ═════════════════════════════════════════════════════════════════════════════════
#  SERVICE INSTANCE
# ═════════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def service():
    return RiskEngineService()


# ═════════════════════════════════════════════════════════════════════════════════
#  BONE RULES (R-01 to R-05)
# ═════════════════════════════════════════════════════════════════════════════════

class TestBoneRules:

    def test_r01_low_bone_height_triggers_alert(self, service):
        """R-01: bone_height_mm < 10 should trigger a warning."""
        req = _make_request(site_assessment={"bone_height_mm": 8.5})
        result = service.assess(req)
        r01_alerts = [a for a in result.alerts if a.rule_id == "R-01"]
        assert len(r01_alerts) == 1
        assert r01_alerts[0].severity == AlertSeverity.WARNING

    def test_r01_adequate_bone_height_no_alert(self, service):
        """R-01: bone_height_mm >= 10 should not trigger."""
        req = _make_request(site_assessment={"bone_height_mm": 12.0})
        result = service.assess(req)
        r01_alerts = [a for a in result.alerts if a.rule_id == "R-01"]
        assert len(r01_alerts) == 0

    def test_r02_low_bone_width(self, service):
        """R-02: bone_width_mm < 5 should trigger."""
        req = _make_request(site_assessment={"bone_width_mm": 4.0})
        result = service.assess(req)
        r02_alerts = [a for a in result.alerts if a.rule_id == "R-02"]
        assert len(r02_alerts) == 1

    def test_r03_d4_bone_density(self, service):
        """R-03: D4 density should trigger warning."""
        req = _make_request(site_assessment={"bone_density": "D4"})
        result = service.assess(req)
        r03_alerts = [a for a in result.alerts if a.rule_id == "R-03"]
        assert len(r03_alerts) == 1

    def test_r04_nerve_proximity_critical(self, service):
        """R-04: nerve < 2mm should trigger CRITICAL alert."""
        req = _make_request(site_assessment={"nerve_proximity_mm": 1.5})
        result = service.assess(req)
        r04_alerts = [a for a in result.alerts if a.rule_id == "R-04"]
        assert len(r04_alerts) == 1
        assert r04_alerts[0].severity == AlertSeverity.CRITICAL

    def test_r05_sinus_proximity_maxilla(self, service):
        """R-05: sinus < 8mm in posterior maxilla should trigger."""
        req = _make_request(site_assessment={
            "jaw_region": "Posterior_Maxilla",
            "sinus_proximity_mm": 5.0,
        })
        result = service.assess(req)
        r05_alerts = [a for a in result.alerts if a.rule_id == "R-05"]
        assert len(r05_alerts) == 1

    def test_no_implant_data_skips_bone(self, service):
        """If implant_data_present is False, bone rules are skipped."""
        req = _make_request(
            computed_flags={"implant_data_present": False},
        )
        result = service.assess(req)
        assert result.bone_assessment is None


# ═════════════════════════════════════════════════════════════════════════════════
#  SYSTEMIC RULES (R-06 to R-08)
# ═════════════════════════════════════════════════════════════════════════════════

class TestSystemicRules:

    def test_r06_high_risk_condition(self, service):
        """R-06: Active cancer should produce CRITICAL alert."""
        req = _make_request(
            medical_history={"systemic_conditions": ["Cancer_Active"]}
        )
        result = service.assess(req)
        r06_criticals = [
            a for a in result.alerts
            if a.rule_id == "R-06" and a.severity == AlertSeverity.CRITICAL
        ]
        assert len(r06_criticals) >= 1

    def test_r06_low_risk_no_alert(self, service):
        """R-06: Asthma (Low risk) should NOT produce an alert (only Medium+ alert)."""
        req = _make_request(
            medical_history={
                "systemic_conditions": ["Asthma"],
                "bleeding_disorder": False,
                "immunocompromised": False,
                "smoking_status": "Non-Smoker",
                "bisphosphonate_therapy": False,
                "radiation_therapy_head_neck": False,
            }
        )
        result = service.assess(req)
        r06_alerts = [a for a in result.alerts if a.rule_id == "R-06"]
        assert len(r06_alerts) == 0

    def test_r07_bisphosphonate_implant(self, service):
        """R-07: Bisphosphonate + implant data → CRITICAL."""
        req = _make_request(
            medical_history={"bisphosphonate_therapy": True},
            computed_flags={"bisphosphonate_risk": True, "implant_data_present": True},
        )
        result = service.assess(req)
        r07 = [a for a in result.alerts if a.rule_id == "R-07"]
        assert len(r07) == 1
        assert r07[0].severity == AlertSeverity.CRITICAL

    def test_r08_immunocompromised(self, service):
        """R-08: Immunocompromised patient produces warning."""
        req = _make_request(medical_history={"immunocompromised": True})
        result = service.assess(req)
        r08 = [a for a in result.alerts if a.rule_id == "R-08"]
        assert len(r08) >= 1

    def test_r08_bleeding_disorder(self, service):
        """R-08: Bleeding disorder produces warning."""
        req = _make_request(medical_history={"bleeding_disorder": True})
        result = service.assess(req)
        r08 = [a for a in result.alerts if a.rule_id == "R-08"]
        assert len(r08) >= 1


# ═════════════════════════════════════════════════════════════════════════════════
#  INFECTION RULES (R-09 to R-12)
# ═════════════════════════════════════════════════════════════════════════════════

class TestInfectionRules:

    def test_r09_acute_localized(self, service):
        """R-09: Pus discharge + fever = acute localized infection."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Pus_Discharge", "Swelling_Localized"],
                "description": "Pus from gum",
                "duration_days": 2,
            },
            clinical_assessment={
                "fever": {"present": True, "temperature_celsius": 38.0},
                "swelling_grade": "Moderate",
                "pain_level": 6,
                "lymphadenopathy": False,
            },
        )
        result = service.assess(req)
        assert result.infection_analysis is not None
        assert result.infection_analysis.pattern == "Acute_Localized"

    def test_r10_spreading_infection(self, service):
        """R-10: Diffuse swelling + fever + lymphadenopathy = spreading."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Swelling_Diffuse", "Pus_Discharge"],
                "description": "Severe swelling spreading",
                "duration_days": 1,
            },
            clinical_assessment={
                "fever": {"present": True, "temperature_celsius": 39.0},
                "swelling_grade": "Severe",
                "pain_level": 9,
                "lymphadenopathy": True,
            },
        )
        result = service.assess(req)
        assert result.infection_analysis is not None
        assert result.infection_analysis.pattern == "Spreading_Infection"
        assert result.infection_analysis.spread_risk == "High"

    def test_r11_chronic_fistula(self, service):
        """R-11: Fistula/sinus tract = chronic infection."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Fistula_Sinus_Tract"],
                "description": "Draining fistula",
                "duration_days": 30,
            },
            clinical_assessment={
                "fever": {"present": False},
                "swelling_grade": "None",
                "pain_level": 2,
                "lymphadenopathy": False,
            },
        )
        result = service.assess(req)
        assert result.infection_analysis is not None
        assert result.infection_analysis.pattern == "Chronic_Infection"

    def test_no_infection_indicators(self, service):
        """No infection symptoms → infection_analysis is None."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache"],
                "description": "Mild pain",
                "duration_days": 1,
            },
            clinical_assessment={
                "fever": {"present": False},
                "swelling_grade": "None",
                "pain_level": 3,
                "lymphadenopathy": False,
            },
        )
        result = service.assess(req)
        assert result.infection_analysis is None


# ═════════════════════════════════════════════════════════════════════════════════
#  SURGICAL COMPLEXITY (R-13 to R-16)
# ═════════════════════════════════════════════════════════════════════════════════

class TestSurgicalComplexity:

    def test_simple_case(self, service):
        """Low pain, no swelling, healthy bone → Simple."""
        req = _make_request(
            chief_complaint={
                "symptoms": ["Toothache"],
                "description": "Mild discomfort",
                "duration_days": 1,
            },
            clinical_assessment={
                "pain_level": 2,
                "swelling_grade": "None",
                "fever": {"present": False},
                "lymphadenopathy": False,
                "tooth_mobility_grade": None,
                "vitality_test": "Vital",
                "probing_depth_mm": 3.0,
            },
            medical_history={
                "systemic_conditions": ["None"],
                "bleeding_disorder": False,
                "immunocompromised": False,
                "smoking_status": "Non-Smoker",
                "bisphosphonate_therapy": False,
                "radiation_therapy_head_neck": False,
            },
            site_assessment={
                "bone_height_mm": 14.0,
                "bone_width_mm": 8.0,
                "bone_density": "D2",
                "nerve_proximity_mm": 8.0,
            },
            computed_flags={
                "implant_data_present": True,
                "bisphosphonate_risk": False,
                "radiation_risk": False,
                "age_contraindication": False,
            },
        )
        result = service.assess(req)
        assert result.surgical_complexity is not None
        assert result.surgical_complexity.complexity_class == ComplexityClass.SIMPLE

    def test_complex_case(self, service):
        """Severe pain + mobility + poor bone → Complex or Highly Complex."""
        req = _make_request(
            clinical_assessment={
                "pain_level": 9,
                "swelling_grade": "Severe",
                "fever": {"present": True, "temperature_celsius": 39.0},
                "lymphadenopathy": True,
                "tooth_mobility_grade": "Grade_3",
                "vitality_test": "Non_Vital",
                "probing_depth_mm": 8.0,
            },
            site_assessment={
                "bone_height_mm": 7.0,
                "bone_width_mm": 4.0,
                "bone_density": "D4",
                "nerve_proximity_mm": 1.5,
            },
            medical_history={
                "bleeding_disorder": True,
                "immunocompromised": True,
                "bisphosphonate_therapy": True,
                "smoking_status": "Current_Smoker",
            },
            computed_flags={"implant_data_present": True},
        )
        result = service.assess(req)
        assert result.surgical_complexity is not None
        assert result.surgical_complexity.complexity_class in (
            ComplexityClass.COMPLEX,
            ComplexityClass.HIGHLY_COMPLEX,
        )
        assert result.surgical_complexity.score >= 45


# ═════════════════════════════════════════════════════════════════════════════════
#  RISK SUMMARY & FEASIBILITY
# ═════════════════════════════════════════════════════════════════════════════════

class TestRiskSummary:

    def test_risk_score_in_range(self, service):
        """Risk score should always be 0-100."""
        req = _make_request()
        result = service.assess(req)
        assert 0 <= result.risk_summary.risk_score <= 100

    def test_alert_count_matches(self, service):
        """alert_count in summary should match len(alerts)."""
        req = _make_request()
        result = service.assess(req)
        assert result.risk_summary.alert_count == len(result.alerts)

    def test_implant_not_recommended_under_18(self, service):
        """Age < 18 with implant data → NOT_RECOMMENDED."""
        req = _make_request(
            demographics={"age": 16},
            computed_flags={"age_contraindication": True, "implant_data_present": True},
        )
        result = service.assess(req)
        assert result.risk_summary.implant_feasibility == ImplantFeasibility.NOT_RECOMMENDED

    def test_insufficient_data_no_implant(self, service):
        """No implant data → INSUFFICIENT_DATA."""
        req = _make_request(computed_flags={"implant_data_present": False})
        result = service.assess(req)
        assert result.risk_summary.implant_feasibility == ImplantFeasibility.INSUFFICIENT_DATA

    def test_rule_trace_populated(self, service):
        """Rule trace should contain rule IDs."""
        req = _make_request()
        result = service.assess(req)
        assert len(result.rule_trace) > 0
        assert "R-01" in result.rule_trace


# ═════════════════════════════════════════════════════════════════════════════════
#  API ENDPOINT TESTS
# ═════════════════════════════════════════════════════════════════════════════════

class TestRiskEngineEndpoint:

    @pytest.mark.anyio
    async def test_assess_success(self):
        """POST /api/risk-engine/assess with valid M1 payload → 200."""
        payload = _base_m1_payload()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/risk-engine/assess", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["module"] == "M2_Risk_Engine"
        assert "risk_summary" in body["data"]
        assert "alerts" in body["data"]

    @pytest.mark.anyio
    async def test_assess_invalid_payload(self):
        """POST /api/risk-engine/assess with missing fields → 422."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/risk-engine/assess", json={"bad": "data"})
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_assess_high_risk_case(self):
        """Severe case should return High or Critical risk."""
        payload = _base_m1_payload(
            clinical_assessment={
                "pain_level": 9,
                "swelling_grade": "Severe",
                "fever": {"present": True, "temperature_celsius": 39.5},
                "lymphadenopathy": True,
                "tooth_mobility_grade": "Grade_3",
                "vitality_test": "Non_Vital",
                "probing_depth_mm": 8.0,
            },
            chief_complaint={
                "symptoms": ["Swelling_Diffuse", "Pus_Discharge", "Toothache"],
                "description": "Severe spreading infection",
                "duration_days": 2,
            },
            site_assessment={
                "bone_height_mm": 6.0,
                "bone_width_mm": 3.5,
                "bone_density": "D4",
                "nerve_proximity_mm": 1.0,
                "jaw_region": "Posterior_Mandible",
                "tooth_site": "36",
            },
            medical_history={
                "systemic_conditions": ["Diabetes_Type1", "Cardiovascular_Disease"],
                "bleeding_disorder": True,
                "immunocompromised": True,
                "bisphosphonate_therapy": True,
                "smoking_status": "Current_Smoker",
                "radiation_therapy_head_neck": False,
            },
            computed_flags={"implant_data_present": True},
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/risk-engine/assess", json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["risk_summary"]["overall_risk_level"] in ("High", "Critical")
        assert data["risk_summary"]["immediate_attention_required"] is True
        assert len(data["alerts"]) > 0
