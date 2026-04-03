"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { submitClinicalInput } from "@/lib/api";
import { fetchPatientById } from "@/lib/store";
import { useAuth } from "@/app/providers";
import StepNavigation from "@/components/clinical/StepNavigation";
import {
  User,
  HeartPulse,
  Stethoscope,
  ClipboardList,
  CheckCircle,
  FileText,
  Activity,
  AlertTriangle,
  Info,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

const symptomCategories = {
  Pain: [
    "Toothache",
    "Thermal_Sensitivity_Hot",
    "Thermal_Sensitivity_Cold",
    "Spontaneous_Pain",
    "Pain_On_Biting",
    "Referred_Pain",
    "Jaw_Pain",
  ],
  "Swelling & Inflammation": [
    "Swelling_Localized",
    "Swelling_Diffuse",
    "Swelling_Extraoral",
    "Gum_Bleeding",
    "Gum_Recession",
    "Pus_Discharge",
  ],
  Other: [
    "Tooth_Mobility",
    "Tooth_Discoloration",
    "Fractured_Tooth",
    "Bad_Breath",
    "Dry_Mouth",
    "Difficulty_Chewing",
    "Jaw_Clicking",
    "Limited_Mouth_Opening",
    "Numbness_Tingling",
    "Fistula_Sinus_Tract",
    "Ulceration",
  ],
};

const defaultFormData = {
  patient_id: "550e8400-e29b-41d4-a716-446655440000",
  age: "45",
  gender: "Male",
  chief_complaint: "Dental sensitivity",
  symptoms: ["Toothache"] as string[],
  symptom_duration_days: "7",
  pain_level: "5",
  swelling_grade: "None",
  smoking_status: "Non-Smoker",
  systemic_conditions: ["None"] as string[],
  fever_present: false,
  bleeding_disorder: false,
  immunocompromised: false,
  bisphosphonate_therapy: false,
  radiation_therapy_head_neck: false,
  tooth_sites: ["11"] as string[],
  jaw_region: "Anterior_Maxilla",
};

export default function ClinicalPage() {
  const params = useParams();
  const patientId = (params?.id as string) || defaultFormData.patient_id;
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [formData, setFormData] = useState({
    ...defaultFormData,
    patient_id: patientId,
  });

  // Helper function to calculate age from date of birth
  const calculateAge = (dob: string): number => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }
    return age;
  };

  // Fetch patient demographics on page load
  useEffect(() => {
    const loadPatientData = async () => {
      if (!patientId) return;

      try {
        const patient = await fetchPatientById(patientId);
        if (patient) {
          const dob = patient.date_of_birth || patient.dob;
          const age = dob ? calculateAge(dob).toString() : defaultFormData.age;
          const gender = patient.gender || defaultFormData.gender;

          setFormData((prev) => ({
            ...prev,
            patient_id: patientId,
            age: age,
            gender: gender,
          }));
        } else {
          // Fallback if patient not found
          setFormData((prev) => ({ ...prev, patient_id: patientId }));
        }
      } catch (err) {
        console.error("Failed to load patient data:", err);
        // Fallback on error - still update patient_id
        setFormData((prev) => ({ ...prev, patient_id: patientId }));
      }
    };

    loadPatientData();
  }, [patientId]);

  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [response, setResponse] = useState<any>(null);

  const steps = [
    { id: 1, title: "Demographics", icon: User },
    { id: 2, title: "Symptoms", icon: AlertTriangle },
    { id: 3, title: "Clinical Findings", icon: Stethoscope },
    { id: 4, title: "Medical History", icon: HeartPulse },
    { id: 5, title: "Review", icon: ClipboardList },
  ];

  const handleNext = () => {
    setError("");
    if (currentStep === 1) {
      if (
        !formData.patient_id ||
        !formData.age ||
        !formData.gender ||
        !formData.chief_complaint
      ) {
        setError("Please fill out all demographic fields.");
        return;
      }
    }
    if (currentStep === 2) {
      if (!formData.symptom_duration_days || formData.symptoms.length === 0) {
        setError("Please select at least one symptom and duration.");
        return;
      }
    }
    if (currentStep === 3) {
      if (!formData.tooth_sites || formData.tooth_sites.length === 0) {
        setError("Please select at least one affected tooth.");
        return;
      }
    }
    setCurrentStep((prev) => Math.min(prev + 1, steps.length));
  };
  const handlePrev = () => setCurrentStep((prev) => Math.max(prev - 1, 1));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (currentStep !== steps.length) {
      handleNext();
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    setResponse(null);

    try {
      const result = await submitClinicalInput(formData);
      setResponse(result);
      setSuccess(
        "Clinical input processed successfully! Data sent to backend.",
      );
      // Keep showing the success state on the Review page instead of resetting immediately
    } catch (err: any) {
      setError(err.message || "Failed to save clinical input");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const toggleSymptom = (symptom: string) => {
    const current = formData.symptoms || [];
    if (current.includes(symptom)) {
      setFormData({
        ...formData,
        symptoms: current.filter((s) => s !== symptom),
      });
    } else {
      setFormData({ ...formData, symptoms: [...current, symptom] });
    }
  };

  const toggleCondition = (condition: string) => {
    const current = formData.systemic_conditions || [];
    if (condition === "None") {
      setFormData({ ...formData, systemic_conditions: ["None"] });
    } else {
      let updated = current.includes(condition)
        ? current.filter((c) => c !== condition)
        : [...current.filter((c) => c !== "None"), condition];
      if (updated.length === 0) updated = ["None"];
      setFormData({ ...formData, systemic_conditions: updated });
    }
  };

  const toggleTooth = (tooth: string) => {
    const current = formData.tooth_sites || [];
    if (current.includes(tooth)) {
      // Remove tooth if already selected
      const updated = current.filter((t) => t !== tooth);
      setFormData({
        ...formData,
        tooth_sites: updated.length > 0 ? updated : [tooth],
      });
    } else {
      // Add tooth to selection
      setFormData({ ...formData, tooth_sites: [...current, tooth] });
    }
  };

  const resetForm = () => {
    setFormData({ ...defaultFormData, patient_id: patientId });
    setCurrentStep(1);
    setSuccess("");
    setResponse(null);
    setError("");
  };

  const getPainColor = (level: number) => {
    if (level <= 3) return "bg-green-500";
    if (level <= 6) return "bg-yellow-500";
    if (level <= 8) return "bg-orange-500";
    return "bg-red-600";
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href={`/dashboard/patients/${patientId}`}
          className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center"
        >
          <ChevronLeft size={20} className="mr-1" /> Back to Patient Profile
        </Link>

        <div className="mt-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <ClipboardList className="text-indigo-600" size={32} />
            Clinical Assessment
          </h1>
          <p className="mt-2 text-gray-700 font-medium">
            Complete the structured clinical input to generate accurate AI
            predictions.
          </p>
        </div>

        {/* Stepper Navigation */}
        <div className="mt-8 mb-8">
          <div className="flex items-center justify-between relative">
            <div className="absolute left-0 top-1/2 w-full h-1 bg-gray-200 -z-10 transform -translate-y-1/2 rounded"></div>
            <div
              className="absolute left-0 top-1/2 h-1 bg-indigo-600 -z-10 transform -translate-y-1/2 rounded transition-all duration-300"
              style={{
                width: `${((currentStep - 1) / (steps.length - 1)) * 100}%`,
              }}
            ></div>

            {steps.map((step) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = currentStep > step.id;

              return (
                <div key={step.id} className="flex flex-col items-center">
                  <button
                    onClick={() => setCurrentStep(step.id)}
                    className={`w-12 h-12 rounded-full flex items-center justify-center border-4 transition-colors ${
                      isActive
                        ? "bg-indigo-600 border-indigo-200 text-white shadow-md"
                        : isCompleted
                          ? "bg-indigo-600 border-white text-white"
                          : "bg-white border-gray-200 text-gray-400"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle size={24} />
                    ) : (
                      <Icon size={20} />
                    )}
                  </button>
                  <span
                    className={`mt-2 text-sm font-medium ${isActive ? "text-indigo-700" : "text-gray-500"}`}
                  >
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <form onSubmit={handleSubmit}>
            <div className="p-8">
              {/* Step 1: Demographics */}
              {currentStep === 1 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                  <div className="flex items-center gap-2 mb-6">
                    <User className="text-indigo-600" />
                    <h2 className="text-xl font-semibold text-gray-800">
                      Patient Data
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        Patient ID
                      </label>
                      <input
                        type="text"
                        value={formData.patient_id}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            patient_id: e.target.value,
                          })
                        }
                        required
                        list="patients"
                        placeholder="Search Name or ID"
                        className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition placeholder-gray-500"
                      />
                      <datalist id="patients">
                        <option value="550e8400-e29b-41d4-a716-446655440000">
                          Charlie Brown (Current)
                        </option>
                        <option value="NEW-PATIENT-001">John Doe (New)</option>
                        <option value="NEW-PATIENT-002">
                          Jane Smith (New)
                        </option>
                      </datalist>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        Age
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="120"
                        value={formData.age}
                        onChange={(e) =>
                          setFormData({ ...formData, age: e.target.value })
                        }
                        required
                        className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition placeholder-gray-500"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        Gender
                      </label>
                      <select
                        value={formData.gender}
                        onChange={(e) =>
                          setFormData({ ...formData, gender: e.target.value })
                        }
                        className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition"
                      >
                        <option value="Male" className="bg-gray-700">
                          Male
                        </option>
                        <option value="Female" className="bg-gray-700">
                          Female
                        </option>
                        <option value="Other" className="bg-gray-700">
                          Other
                        </option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        Chief Complaint
                      </label>
                      <input
                        type="text"
                        value={formData.chief_complaint}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            chief_complaint: e.target.value,
                          })
                        }
                        required
                        placeholder="e.g. Pain in lower left jaw"
                        className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition placeholder-gray-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Symptoms */}
              {currentStep === 2 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                  <div className="flex items-center gap-2 mb-6">
                    <AlertTriangle className="text-orange-500" />
                    <h2 className="text-xl font-semibold text-gray-800">
                      Symptom Assessment
                    </h2>
                  </div>

                  <div className="space-y-2 mb-6">
                    <label className="text-sm font-medium text-gray-700">
                      Duration of Symptoms (days)
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.symptom_duration_days}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          symptom_duration_days: e.target.value,
                        })
                      }
                      className="w-full md:w-1/3 text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition placeholder-gray-500"
                    />
                  </div>

                  <div className="space-y-8">
                    {Object.entries(symptomCategories).map(
                      ([category, items]) => (
                        <div
                          key={category}
                          className="bg-white rounded-lg border border-gray-100 p-4 shadow-sm"
                        >
                          <h3 className="text-md font-semibold text-gray-800 mb-3 border-b pb-2">
                            {category}
                          </h3>
                          <div className="flex flex-wrap gap-2">
                            {items.map((symptom) => {
                              const isSelected =
                                formData.symptoms.includes(symptom);
                              return (
                                <button
                                  type="button"
                                  key={symptom}
                                  onClick={() => toggleSymptom(symptom)}
                                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors border ${
                                    isSelected
                                      ? "bg-indigo-100 text-indigo-800 border-indigo-300 hover:bg-indigo-200"
                                      : "bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100 hover:text-gray-900"
                                  }`}
                                >
                                  {symptom.replace(/_/g, " ")}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </div>
              )}

              {/* Step 3: Clinical Findings */}
              {currentStep === 3 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                  <div className="flex items-center gap-2 mb-6">
                    <Stethoscope className="text-blue-500" />
                    <h2 className="text-xl font-semibold text-gray-800">
                      Clinical Findings
                    </h2>
                  </div>

                  <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-8">
                    {/* Pain Level */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="text-sm font-bold text-gray-700">
                          Pain Level:{" "}
                          <span className="text-lg ml-1">
                            {formData.pain_level}/10
                          </span>
                        </label>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        value={formData.pain_level}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            pain_level: e.target.value,
                          })
                        }
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                      />
                      <div
                        className="w-full h-2 rounded-lg mt-2 transition-all duration-300 opacity-70"
                        style={{
                          background: `linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444)`,
                          clipPath: `inset(0 ${100 - Number(formData.pain_level) * 10}% 0 0)`,
                        }}
                      ></div>
                      <div className="flex justify-between text-xs text-gray-700 font-medium mt-2">
                        <span>No Pain (0)</span>
                        <span>Moderate (5)</span>
                        <span>Severe (10)</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">
                          Swelling Grade
                        </label>
                        <select
                          value={formData.swelling_grade}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              swelling_grade: e.target.value,
                            })
                          }
                          className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:ring-2 focus:ring-indigo-500 outline-none transition"
                        >
                          <option value="None">None</option>
                          <option value="Mild">Mild</option>
                          <option value="Moderate">Moderate</option>
                          <option value="Severe">Severe</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">
                          Jaw Region
                        </label>
                        <select
                          value={formData.jaw_region}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              jaw_region: e.target.value,
                            })
                          }
                          className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition placeholder-gray-500"
                        >
                          <option value="Anterior_Maxilla">
                            Anterior Maxilla
                          </option>
                          <option value="Posterior_Maxilla">
                            Posterior Maxilla
                          </option>
                          <option value="Anterior_Mandible">
                            Anterior Mandible
                          </option>
                          <option value="Posterior_Mandible">
                            Posterior Mandible
                          </option>
                        </select>
                      </div>
                    </div>

                    {/* Simple Odontogram Tooth Selector - Multi-Select */}
                    <div className="space-y-3">
                      <label className="text-sm font-medium text-gray-700 flex justify-between items-center">
                        <span>Affected Tooth/Teeth (FDI)</span>
                        <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded">
                          Selected:{" "}
                          {formData.tooth_sites &&
                          formData.tooth_sites.length > 0
                            ? formData.tooth_sites.join(", ")
                            : "None"}
                        </span>
                      </label>
                      <p className="text-xs text-gray-600 italic">
                        Click to select, click again to deselect. You can select
                        multiple teeth.
                      </p>
                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div className="text-center font-semibold text-gray-500 text-xs mb-2">
                          MAXILLARY
                        </div>
                        <div className="flex justify-center gap-1 mb-4 flex-wrap">
                          {["18", "17", "16", "15", "14", "13", "12", "11"].map(
                            (t) => (
                              <button
                                key={t}
                                type="button"
                                onClick={() => toggleTooth(t)}
                                className={`w-8 h-10 rounded border text-xs font-bold transition-colors ${formData.tooth_sites?.includes(t) ? "bg-indigo-600 text-white border-indigo-700" : "bg-white border-gray-300 hover:bg-gray-200 text-gray-700"}`}
                              >
                                {t}
                              </button>
                            ),
                          )}
                          <div className="w-2"></div>
                          {["21", "22", "23", "24", "25", "26", "27", "28"].map(
                            (t) => (
                              <button
                                key={t}
                                type="button"
                                onClick={() => toggleTooth(t)}
                                className={`w-8 h-10 rounded border text-xs font-bold transition-colors ${formData.tooth_sites?.includes(t) ? "bg-indigo-600 text-white border-indigo-700" : "bg-white border-gray-300 hover:bg-gray-200 text-gray-700"}`}
                              >
                                {t}
                              </button>
                            ),
                          )}
                        </div>
                        <div className="flex justify-center gap-1 flex-wrap">
                          {["48", "47", "46", "45", "44", "43", "42", "41"].map(
                            (t) => (
                              <button
                                key={t}
                                type="button"
                                onClick={() => toggleTooth(t)}
                                className={`w-8 h-10 rounded border text-xs font-bold transition-colors ${formData.tooth_sites?.includes(t) ? "bg-indigo-600 text-white border-indigo-700" : "bg-white border-gray-300 hover:bg-gray-200 text-gray-700"}`}
                              >
                                {t}
                              </button>
                            ),
                          )}
                          <div className="w-2"></div>
                          {["31", "32", "33", "34", "35", "36", "37", "38"].map(
                            (t) => (
                              <button
                                key={t}
                                type="button"
                                onClick={() => toggleTooth(t)}
                                className={`w-8 h-10 rounded border text-xs font-bold transition-colors ${formData.tooth_sites?.includes(t) ? "bg-indigo-600 text-white border-indigo-700" : "bg-white border-gray-300 hover:bg-gray-200 text-gray-700"}`}
                              >
                                {t}
                              </button>
                            ),
                          )}
                        </div>
                        <div className="text-center font-semibold text-gray-500 text-xs mt-2">
                          MANDIBULAR
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Medical History */}
              {currentStep === 4 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                  <div className="flex items-center gap-2 mb-6">
                    <HeartPulse className="text-red-500" />
                    <h2 className="text-xl font-semibold text-gray-800">
                      Medical History
                    </h2>
                  </div>

                  <div className="space-y-2 mb-6 w-full md:w-1/2">
                    <label className="text-sm font-medium text-gray-700">
                      Smoking Status
                    </label>
                    <select
                      value={formData.smoking_status}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          smoking_status: e.target.value,
                        })
                      }
                      className="w-full text-sm bg-white text-black font-medium rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none transition"
                    >
                      <option value="Non-Smoker" className="bg-gray-700">
                        Non-Smoker
                      </option>
                      <option value="Former_Smoker" className="bg-gray-700">
                        Former Smoker
                      </option>
                      <option value="Current_Smoker" className="bg-gray-700">
                        Current Smoker
                      </option>
                    </select>
                  </div>

                  <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                    <label className="block text-sm font-semibold text-gray-800 mb-4 border-b pb-2">
                      Systemic Conditions
                    </label>
                    <div className="flex flex-wrap gap-2 mb-6">
                      {[
                        "None",
                        "Diabetes_Type1",
                        "Diabetes_Type2",
                        "Hypertension",
                        "Cardiovascular_Disease",
                        "Osteoporosis",
                        "Rheumatoid_Arthritis",
                        "HIV_AIDS",
                        "Kidney_Disease",
                        "Liver_Disease",
                        "Thyroid_Disorder",
                        "Asthma",
                      ].map((condition) => {
                        const isSelected =
                          formData.systemic_conditions.includes(condition);
                        return (
                          <button
                            type="button"
                            key={condition}
                            onClick={() => toggleCondition(condition)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all border ${
                              isSelected
                                ? condition === "None"
                                  ? "bg-green-100 border-green-300 text-green-800"
                                  : "bg-red-50 border-red-200 text-red-800"
                                : "bg-white border-gray-300 text-gray-600 hover:bg-gray-50"
                            }`}
                          >
                            {condition.replace(/_/g, " ")}
                          </button>
                        );
                      })}
                    </div>

                    <label className="block text-sm font-semibold text-gray-800 mb-4 border-b pb-2 mt-8">
                      Specific Risk Factors
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[
                        { key: "fever_present", label: "Fever Present" },
                        {
                          key: "bleeding_disorder",
                          label: "Bleeding Disorder",
                        },
                        {
                          key: "immunocompromised",
                          label: "Immunocompromised",
                        },
                        {
                          key: "bisphosphonate_therapy",
                          label: "Bisphosphonate Therapy",
                        },
                        {
                          key: "radiation_therapy_head_neck",
                          label: "Head & Neck Radiation",
                        },
                      ].map(({ key, label }) => (
                        <label
                          key={key}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${formData[key as keyof typeof formData] ? "bg-orange-50 border-orange-200" : "bg-gray-50 border-gray-200 hover:bg-gray-100"}`}
                        >
                          <input
                            type="checkbox"
                            checked={
                              formData[key as keyof typeof formData] as boolean
                            }
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                [key]: e.target.checked,
                              })
                            }
                            className="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 mr-3"
                          />
                          <span
                            className={`font-medium ${formData[key as keyof typeof formData] ? "text-orange-900" : "text-gray-700"}`}
                          >
                            {label}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Review */}
              {currentStep === 5 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                  <div className="flex items-center gap-2 mb-6">
                    <CheckCircle className="text-green-600" />
                    <h2 className="text-xl font-semibold text-gray-800">
                      Review & Submit
                    </h2>
                  </div>

                  {error && (
                    <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-700 border border-red-200 flex items-start">
                      <AlertTriangle
                        className="mr-3 flex-shrink-0 mt-0.5"
                        size={20}
                      />
                      <div>
                        <strong>Error:</strong> {error}
                      </div>
                    </div>
                  )}

                  {success ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center shadow-sm">
                      <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                      <h3 className="text-xl font-bold text-green-800 mb-2">
                        Success!
                      </h3>
                      <p className="text-green-700">{success}</p>
                      <button
                        type="button"
                        onClick={resetForm}
                        className="mt-6 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
                      >
                        Start New Assessment
                      </button>
                    </div>
                  ) : (
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                      <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                        <span className="font-semibold text-gray-700">
                          Patient: {formData.patient_id}
                        </span>
                        <span className="text-sm text-gray-500">
                          {formData.age} yrs • {formData.gender}
                        </span>
                      </div>

                      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 text-sm">
                        <div className="space-y-4">
                          <div>
                            <h4 className="text-xs uppercase tracking-wider text-gray-700 font-bold mb-1">
                              Chief Complaint
                            </h4>
                            <p className="text-gray-900 font-medium">
                              {formData.chief_complaint}
                            </p>
                          </div>
                          <div>
                            <h4 className="text-xs uppercase tracking-wider text-gray-700 font-bold mb-1">
                              Symptoms ({formData.symptom_duration_days} days)
                            </h4>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {formData.symptoms.length > 0 ? (
                                formData.symptoms.map((s) => (
                                  <span
                                    key={s}
                                    className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded text-xs"
                                  >
                                    {s.replace(/_/g, " ")}
                                  </span>
                                ))
                              ) : (
                                <span className="text-gray-500 italic">
                                  None selected
                                </span>
                              )}
                            </div>
                          </div>
                          <div>
                            <h4 className="text-xs uppercase tracking-wider text-gray-700 font-bold mb-1">
                              Pain & Swelling
                            </h4>
                            <p className="text-gray-900">
                              Pain:{" "}
                              <span className="font-medium mr-3">
                                {formData.pain_level}/10
                              </span>{" "}
                              Swelling:{" "}
                              <span className="font-medium">
                                {formData.swelling_grade}
                              </span>
                            </p>
                          </div>
                        </div>

                        <div className="space-y-4 md:border-l pl-0 md:pl-8">
                          <div>
                            <h4 className="text-xs uppercase tracking-wider text-gray-700 font-bold mb-1">
                              Clinical Site
                            </h4>
                            <p className="text-gray-900">
                              Tooth:{" "}
                              <span className="font-bold text-indigo-700">
                                {formData.tooth_sites &&
                                formData.tooth_sites.length > 0
                                  ? formData.tooth_sites.join(", ")
                                  : "None"}
                              </span>{" "}
                              ({formData.jaw_region.replace(/_/g, " ")})
                            </p>
                          </div>
                          <div>
                            <h4 className="text-xs uppercase tracking-wider text-gray-700 font-bold mb-1">
                              Medical Highlights
                            </h4>
                            <p className="text-gray-900 mb-1">
                              Smoking:{" "}
                              {formData.smoking_status.replace(/_/g, " ")}
                            </p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {formData.systemic_conditions.filter(
                                (c) => c !== "None",
                              ).length > 0 &&
                                formData.systemic_conditions.map(
                                  (c) =>
                                    c !== "None" && (
                                      <span
                                        key={c}
                                        className="bg-red-50 text-red-700 border border-red-100 px-2 py-0.5 rounded text-xs"
                                      >
                                        {c.replace(/_/g, " ")}
                                      </span>
                                    ),
                                )}
                              {formData.bleeding_disorder && (
                                <span className="bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded text-xs">
                                  Bleeding Disorder
                                </span>
                              )}
                              {formData.bisphosphonate_therapy && (
                                <span className="bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded text-xs">
                                  Bisphosphonates
                                </span>
                              )}
                              {formData.radiation_therapy_head_neck && (
                                <span className="bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded text-xs">
                                  Radiation
                                </span>
                              )}
                              {formData.immunocompromised && (
                                <span className="bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded text-xs">
                                  Immunocompromised
                                </span>
                              )}
                              {formData.fever_present && (
                                <span className="bg-yellow-50 text-yellow-700 border border-yellow-100 px-2 py-0.5 rounded text-xs">
                                  Fever
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Form Footer / Navigation */}
            {!success && (
              <div className="px-8 py-5 bg-gray-50 border-t border-gray-200 flex justify-between items-center rounded-b-xl">
                {currentStep > 1 ? (
                  <button
                    type="button"
                    onClick={handlePrev}
                    className="px-6 py-2.5 rounded-lg border border-gray-300 bg-white text-gray-700 font-medium hover:bg-gray-50 flex items-center transition"
                  >
                    <ChevronLeft size={18} className="mr-1" /> Previous
                  </button>
                ) : (
                  <div></div>
                )}

                {currentStep < steps.length ? (
                  <button
                    type="button"
                    onClick={handleNext}
                    className="px-8 py-2.5 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700 flex items-center transition shadow-sm"
                  >
                    Next Step <ChevronRight size={18} className="ml-1" />
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-8 py-2.5 rounded-lg bg-green-600 text-white font-bold hover:bg-green-700 flex items-center transition shadow-sm disabled:opacity-50"
                  >
                    {loading ? (
                      <>Processing...</>
                    ) : (
                      <>
                        Submit Assessment{" "}
                        <CheckCircle size={18} className="ml-2" />
                      </>
                    )}
                  </button>
                )}
              </div>
            )}

            {success && (
              <StepNavigation patientId={patientId} currentStep="clinical" />
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
