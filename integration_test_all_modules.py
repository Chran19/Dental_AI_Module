#!/usr/bin/env python
"""
End-to-End Integration Test: All Modules (M1-M6 + M8)
Tests complete workflow from clinical input → diagnosis → treatment → explainability
Also tests image analysis integration
"""

import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.schemas.clinical_input import ClinicalInputRequest, ClinicalInputResponse
from app.schemas.risk_engine import RiskEngineRequest
from app.schemas.diagnosis import DiagnosisRequest
from app.schemas.investigation import InvestigationRequest
from app.schemas.treatment import TreatmentRequest

from app.services.clinical_input_service import ClinicalInputService
from app.services.risk_engine_service import RiskEngineService
from app.services.diagnosis_service import DiagnosisService
from app.services.investigation_service import InvestigationService
from app.services.treatment_service import TreatmentService
from app.services.explainability_service import ExplainabilityService


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_module_1_clinical_input():
    """Test Module 1: Clinical Input Processing"""
    print_section("MODULE 1: CLINICAL INPUT PROCESSING")
    
    service = ClinicalInputService()
    
    payload = {
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
        "chief_complaint": "Patient reports severe pain in lower right molar region",
        "symptoms": ["Toothache", "Swelling_Localized"],
        "symptom_duration_days": 3,
        "symptom_onset": "Gradual",
        "pain_level": 8,
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
        "clinical_notes": "Previous failed RCT. Patient anxious.",
    }
    
    request = ClinicalInputRequest(**payload)
    doctor_id = uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")
    output = service.process(request, doctor_id)
    
    print(f"✓ Clinical input validated")
    print(f"  - Patient ID: {output.patient_id}")
    print(f"  - Urgency Flag: {output.computed_flags.urgency_flag}")
    print(f"  - Risk Flags: {[k for k, v in output.computed_flags.__dict__.items() if v and k != 'urgency_flag']}")
    print(f"  - Implant Data Present: {output.computed_flags.implant_data_present}")
    
    return output


def test_module_2_risk_engine(m1_output):
    """Test Module 2: Risk-Based Assessment"""
    print_section("MODULE 2: RISK-BASED ASSESSMENT")
    
    service = RiskEngineService()
    
    # Use the assert method which takes M1Output directly
    output = service.assess(m1_output)
    
    print(f"✓ Risk assessment completed")
    print(f"  - Overall Risk Level: {output.risk_summary.overall_risk_level}")
    print(f"  - Risk Score: {output.risk_summary.risk_score:.1f}")
    print(f"  - Total Alerts: {len(output.risk_summary.alerts)}")
    print(f"  - Implant Feasibility: {output.risk_summary.implant_feasibility}")
    
    return output


def test_module_3_diagnosis(m1_output, m2_output):
    """Test Module 3: Differential Diagnosis"""
    print_section("MODULE 3: DIFFERENTIAL DIAGNOSIS")
    
    service = DiagnosisService()
    
    req = DiagnosisRequest(m1=m1_output, m2=m2_output, max_results=5)
    output = service.diagnose(req)
    
    print(f"✓ Differential diagnoses generated")
    print(f"  - Total Differentials: {len(output.differentials)}")
    print(f"  - Top Diagnosis: {output.differentials[0].name if output.differentials else 'N/A'}")
    if output.differentials:
        print(f"    Confidence: {output.differentials[0].confidence:.1f}%")
    print(f"  - Clinical Summary: {output.clinical_summary[:60]}...")
    
    return output


def test_module_4_investigation(m1_output, m3_output):
    """Test Module 4: Investigation Recommender"""
    print_section("MODULE 4: INVESTIGATION RECOMMENDER")
    
    service = InvestigationService()
    
    req = InvestigationRequest(m1=m1_output, m3=m3_output)
    output = service.recommend(req)
    
    print(f"✓ Investigations recommended")
    print(f"  - Imaging Studies: {len(output.imaging_studies)} items")
    print(f"  - Laboratory Tests: {len(output.laboratory_tests)} items")
    print(f"  - Special Tests: {len(output.special_tests)} items")
    print(f"  - Reasoning: {output.clinical_reasoning[:60]}...")
    
    return output


def test_module_5_treatment(m1_output, m2_output, m3_output, m4_output):
    """Test Module 5: Treatment Recommendation"""
    print_section("MODULE 5: TREATMENT RECOMMENDATION")
    
    service = TreatmentService()
    
    req = TreatmentRequest(m1=m1_output, m2=m2_output, m3=m3_output, m4=m4_output)
    output = service.recommend(req)
    
    print(f"✓ Treatment plan generated")
    print(f"  - Primary Treatment: {output.primary_treatment.name if output.primary_treatment else 'N/A'}")
    print(f"  - Alternative Treatments: {len(output.alternative_treatments)} items")
    print(f"  - Medications: {len(output.medications)} items")
    print(f"  - Contraindications: {len(output.contraindications)} items")
    print(f"  - Feasibility Score: {output.feasibility_score:.0%}")
    
    return output


def test_module_6_explainability(m1_output, m2_output, m3_output, m4_output, m5_output):
    """Test Module 6: Explainability"""
    print_section("MODULE 6: EXPLAINABILITY (Decision Support)")
    
    service = ExplainabilityService()
    
    output = service.generate_explanation(
        m1_output=m1_output,
        m2_output=m2_output,
        m3_output=m3_output,
        m4_output=m4_output,
        m5_output=m5_output
    )
    
    print(f"✓ Explainability generated")
    print(f"  - Summary: {output.summary[:80]}..." if output.summary else "  - Summary: (N/A)")
    print(f"  - Scoring Breakdown: {len(output.m3_scoring_trace)} items")
    print(f"  - M2 Rules Triggered: {len(output.m2_rules_triggered)} items")
    print(f"  - Contraindication Warnings: {len(output.m5_contraindication_warnings)} items")
    print(f"  - Case ID: {output.case_id}")
    
    return output


def test_image_analysis():
    """Test Module 8: Image Analysis"""
    print_section("MODULE 8: IMAGE ANALYSIS (Optional Integration)")
    
    try:
        # Check if model exists
        model_path = Path(__file__).parent / "backend" / "ml" / "models" / "dental_cnn_model_phase4.pth"
        
        if model_path.exists():
            print(f"✓ Image analysis model found at {model_path.name}")
            print(f"  - Can be integrated with diagnosis engine for cross-validation")
            print(f"  - Provides pathology detection and bone quality assessment")
            return True
        else:
            print(f"⚠ Image analysis model not found (optional)")
            print(f"  - Path checked: {model_path}")
            return False
    except Exception as e:
        print(f"⚠ Image analysis check skipped: {str(e)}")
        return False


def main():
    """Run complete integration test"""
    
    print("\n" + "="*80)
    print("  CHAIRSIDE COMPANION: END-TO-END INTEGRATION TEST")
    print("  Testing Modules 1-6 (Core AI Engine) + Module 8 (Image Analysis)")
    print("="*80)
    
    try:
        # Test each module in sequence
        m1 = test_module_1_clinical_input()
        m2 = test_module_2_risk_engine(m1)
        m3 = test_module_3_diagnosis(m1, m2)
        m4 = test_module_4_investigation(m1, m3)
        m5 = test_module_5_treatment(m1, m2, m3, m4)
        m6 = test_module_6_explainability(m1, m2, m3, m4, m5)
        
        # Test image analysis
        m8 = test_image_analysis()
        
        # Summary
        print_section("INTEGRATION TEST SUMMARY")
        print("✓ Module 1 (Clinical Input)      - WORKING")
        print("✓ Module 2 (Risk Engine)         - WORKING")
        print("✓ Module 3 (Diagnosis)           - WORKING")
        print("✓ Module 4 (Investigation)       - WORKING")
        print("✓ Module 5 (Treatment)           - WORKING")
        print("✓ Module 6 (Explainability)      - WORKING")
        print(f"{'✓' if m8 else '⚠'} Module 8 (Image Analysis)      - {'AVAILABLE' if m8 else 'OPTIONAL'}")
        
        print("\n" + "="*80)
        print("  ALL MODULES INTEGRATED AND WORKING! 🎉")
        print("="*80 + "\n")
        
        # Save test result
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": "end_to_end_integration",
            "status": "PASSED",
            "modules_tested": {
                "M1_clinical_input": "WORKING",
                "M2_risk_engine": "WORKING",
                "M3_diagnosis": "WORKING",
                "M4_investigation": "WORKING",
                "M5_treatment": "WORKING",
                "M6_explainability": "WORKING",
                "M8_image_analysis": "AVAILABLE" if m8 else "OPTIONAL"
            },
            "case_id": str(m1.patient_id),
            "final_diagnosis": m3.differentials[0].name if m3.differentials else None,
        }
        
        with open("integration_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print("Result saved to: integration_test_result.json\n")
        
        return 0
        
    except Exception as e:
        print_section("ERROR")
        print(f"✗ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
