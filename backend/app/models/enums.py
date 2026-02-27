"""
Module 1 — Clinical Enumerations
All predefined enum types used across clinical input processing.
Reference: Module_1_Clinical_Input_Processing.md §3
"""

from enum import Enum


# ─── Patient Demographics ───────────────────────────────────────────────────────

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


# ─── Medical History ─────────────────────────────────────────────────────────────

class SystemicCondition(str, Enum):
    """Predefined systemic conditions list (§3.2.1)"""
    DIABETES_TYPE1 = "Diabetes_Type1"
    DIABETES_TYPE2 = "Diabetes_Type2"
    HYPERTENSION = "Hypertension"
    CARDIOVASCULAR_DISEASE = "Cardiovascular_Disease"
    OSTEOPOROSIS = "Osteoporosis"
    RHEUMATOID_ARTHRITIS = "Rheumatoid_Arthritis"
    HEPATITIS_B = "Hepatitis_B"
    HEPATITIS_C = "Hepatitis_C"
    HIV_AIDS = "HIV_AIDS"
    KIDNEY_DISEASE = "Kidney_Disease"
    LIVER_DISEASE = "Liver_Disease"
    THYROID_DISORDER = "Thyroid_Disorder"
    ASTHMA = "Asthma"
    COPD = "COPD"
    EPILEPSY = "Epilepsy"
    BLOOD_DISORDER = "Blood_Disorder"
    AUTOIMMUNE_DISEASE = "Autoimmune_Disease"
    CANCER_ACTIVE = "Cancer_Active"
    CANCER_REMISSION = "Cancer_Remission"
    PREGNANCY = "Pregnancy"
    NONE = "None"


class SmokingStatus(str, Enum):
    NON_SMOKER = "Non-Smoker"
    FORMER_SMOKER = "Former_Smoker"
    CURRENT_SMOKER = "Current_Smoker"


# ─── Symptoms & Complaint ────────────────────────────────────────────────────────

class Symptom(str, Enum):
    """Predefined symptoms list (§3.3.1)"""
    TOOTHACHE = "Toothache"
    THERMAL_SENSITIVITY_HOT = "Thermal_Sensitivity_Hot"
    THERMAL_SENSITIVITY_COLD = "Thermal_Sensitivity_Cold"
    SPONTANEOUS_PAIN = "Spontaneous_Pain"
    PAIN_ON_BITING = "Pain_On_Biting"
    REFERRED_PAIN = "Referred_Pain"
    SWELLING_LOCALIZED = "Swelling_Localized"
    SWELLING_DIFFUSE = "Swelling_Diffuse"
    SWELLING_EXTRAORAL = "Swelling_Extraoral"
    GUM_BLEEDING = "Gum_Bleeding"
    GUM_RECESSION = "Gum_Recession"
    PUS_DISCHARGE = "Pus_Discharge"
    TOOTH_MOBILITY = "Tooth_Mobility"
    TOOTH_DISCOLORATION = "Tooth_Discoloration"
    FRACTURED_TOOTH = "Fractured_Tooth"
    BAD_BREATH = "Bad_Breath"
    DRY_MOUTH = "Dry_Mouth"
    DIFFICULTY_CHEWING = "Difficulty_Chewing"
    JAW_PAIN = "Jaw_Pain"
    JAW_CLICKING = "Jaw_Clicking"
    LIMITED_MOUTH_OPENING = "Limited_Mouth_Opening"
    NUMBNESS_TINGLING = "Numbness_Tingling"
    FISTULA_SINUS_TRACT = "Fistula_Sinus_Tract"
    ULCERATION = "Ulceration"


class SymptomOnset(str, Enum):
    SUDDEN = "Sudden"
    GRADUAL = "Gradual"
    INTERMITTENT = "Intermittent"


# ─── Clinical Assessment ─────────────────────────────────────────────────────────

class SwellingGrade(str, Enum):
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class ToothMobilityGrade(str, Enum):
    NONE = "None"
    GRADE_1 = "Grade_1"
    GRADE_2 = "Grade_2"
    GRADE_3 = "Grade_3"


class PercussionTest(str, Enum):
    NEGATIVE = "Negative"
    POSITIVE_MILD = "Positive_Mild"
    POSITIVE_SEVERE = "Positive_Severe"


class VitalityTest(str, Enum):
    VITAL = "Vital"
    NON_VITAL = "Non_Vital"
    INCONCLUSIVE = "Inconclusive"
    NOT_TESTED = "Not_Tested"


# ─── Site & Bone Assessment ──────────────────────────────────────────────────────

class JawRegion(str, Enum):
    ANTERIOR_MAXILLA = "Anterior_Maxilla"
    POSTERIOR_MAXILLA = "Posterior_Maxilla"
    ANTERIOR_MANDIBLE = "Anterior_Mandible"
    POSTERIOR_MANDIBLE = "Posterior_Mandible"


class BoneDensity(str, Enum):
    """Misch classification"""
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"


class AdjacentTeethStatus(str, Enum):
    HEALTHY = "Healthy"
    RESTORED = "Restored"
    MISSING = "Missing"
    COMPROMISED = "Compromised"


# ─── Computed / System Enums ─────────────────────────────────────────────────────

class UrgencyFlag(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class CaseStatus(str, Enum):
    DRAFT = "Draft"
    VALIDATED = "Validated"
    ANALYZED = "Analyzed"
    CONFIRMED = "Confirmed"


class UserRole(str, Enum):
    DOCTOR = "Doctor"
    ADMIN = "Admin"
