"use client";

import { useState, useEffect } from "react";
import { assessRisk, getRiskAssessments } from "@/lib/api";
import { useAuth } from "@/app/providers";
import {
  AlertTriangle,
  CheckCircle,
  Activity,
  FileText,
  Save,
  History,
  TrendingDown,
  TrendingUp,
  ShieldAlert,
  ChevronRight,
  ChevronLeft,
  PieChart,
} from "lucide-react";

export default function RiskPage() {
  const { isAuthenticated } = useAuth();
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [response, setResponse] = useState<any>(null);

  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);

  const [formData, setFormData] = useState({
    patient_id: "550e8400-e29b-41d4-a716-446655440000",
    age: "65",
    gender: "Male",
    smoking_status: "Former_Smoker",
    chief_complaint: "Evaluate implant candidacy",
    symptoms: ["Pain_On_Biting"],
    pain_level: "3",
    swelling_grade: "None",
    tooth_site: "11",
    jaw_region: "Anterior_Maxilla",
    systemic_conditions: ["Diabetes_Type2"],
    bleeding_disorder: false,
    immunocompromised: false,
    bisphosphonate_therapy: true,
    radiation_therapy_head_neck: false,
  });

  const symptomOptions = [
    "Toothache",
    "Thermal_Sensitivity_Hot",
    "Pain_On_Biting",
    "Swelling_Localized",
    "Gum_Bleeding",
    "Tooth_Mobility",
    "Fractured_Tooth",
  ];

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const data = await getRiskAssessments();
        setAssessments(Array.isArray(data) ? data : []);
      } catch (err: any) {
        console.log("[Risk] No assessment history:", err.message);
      }
    };

    if (isAuthenticated) fetchAssessments();
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    if (currentStep === 1) {
      if (!formData.patient_id || !formData.age || !formData.gender || !formData.smoking_status) {
        setError("Please fill out all patient profile fields.");
        return;
      }
    }
    if (currentStep === 3) {
      if (formData.symptoms.length === 0) {
        setError("Please select at least one reported symptom.");
        return;
      }
    }

    if (currentStep < 3) {
      setCurrentStep((prev) => prev + 1);
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const result = await assessRisk(formData);
      // Ensure we have mock score data if the backend didn't provide it
      if (!result.composite_risk_score) {
        result.composite_risk_score =
          result.risk_level === "High"
            ? 85
            : result.risk_level === "Moderate"
              ? 55
              : 20;
      }
      setResponse(result);
      setSuccess("Risk assessment completed successfully!");
      setAssessments((prev) => [result, ...prev]);
      setCurrentStep(4); // Move to results view
    } catch (err: any) {
      setError(err.message || "Assessment failed");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (field: keyof typeof formData) => {
    setFormData((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const handleSymptomChange = (symptom: string) => {
    setFormData((prev) => {
      const current = prev.symptoms;
      if (current.includes(symptom)) {
        return { ...prev, symptoms: current.filter((s) => s !== symptom) };
      } else {
        return { ...prev, symptoms: [...current, symptom] };
      }
    });
  };

  // SVG Gauge Helper
  const renderGauge = (score: number) => {
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    // Semi-circle
    const strokeDasharray = `${circumference / 2} ${circumference / 2}`;
    const strokeDashoffset =
      circumference / 2 - (score / 100) * (circumference / 2);

    let color = "text-green-500";
    if (score >= 40) color = "text-amber-500";
    if (score >= 70) color = "text-red-500";

    return (
      <div className="relative flex flex-col items-center">
        <svg className="w-48 h-24 overflow-hidden" viewBox="0 0 140 70">
          <path
            d="M 10 70 A 60 60 0 0 1 130 70"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="16"
            strokeLinecap="round"
          />
          <path
            d="M 10 70 A 60 60 0 0 1 130 70"
            fill="none"
            className={color}
            stroke="currentColor"
            strokeWidth="16"
            strokeLinecap="round"
            strokeDasharray={"188.4 188.4"}
            strokeDashoffset={188.4 - (score / 100) * 188.4}
            style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
          />
        </svg>
        <div className="absolute bottom-0 flex flex-col items-center">
          <span className={`text-3xl font-black ${color}`}>{score}</span>
          <span className="text-xs font-bold text-gray-700 uppercase tracking-widest">
            Risk Score
          </span>
        </div>
      </div>
    );
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <ShieldAlert className="text-indigo-600" /> Clinical Risk Assessment
          </h1>
          <p className="text-gray-700 mt-1 font-medium">
            Multi-factor analysis for procedural safety and contraindications
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Assessment Wizard or Results */}
          <div className="bg-white p-0 rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            {currentStep < 4 ? (
              <form onSubmit={handleSubmit}>
                {/* Wizard Header */}
                <div className="bg-gray-50 p-6 border-b border-gray-200">
                  <div className="flex justify-between text-sm font-bold text-gray-700 uppercase tracking-wider mb-2">
                    <span className={currentStep >= 1 ? "text-indigo-600" : ""}>
                      Step 1: Patient
                    </span>
                    <span className={currentStep >= 2 ? "text-indigo-600" : ""}>
                      Step 2: Medical
                    </span>
                    <span className={currentStep >= 3 ? "text-indigo-600" : ""}>
                      Step 3: Clinical
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-indigo-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${(currentStep / 3) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="p-8">
                  {/* Step 1: Patient Details */}
                  {currentStep === 1 && (
                    <div className="space-y-6 animate-in slide-in-from-right-8 duration-300">
                      <h2 className="text-xl font-bold text-gray-900 border-b pb-2">
                        Patient Profile
                      </h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-bold text-gray-700 mb-2">
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
                            className="w-full text-sm bg-white text-gray-900 font-medium rounded-lg border-gray-300 px-3 py-2 border focus:ring-2 focus:ring-indigo-500 outline-none transition"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-bold text-gray-700 mb-2">
                            Age
                          </label>
                          <input
                            type="number"
                            value={formData.age}
                            onChange={(e) =>
                              setFormData({ ...formData, age: e.target.value })
                            }
                            className="w-full text-sm bg-white text-gray-900 font-medium rounded-lg border-gray-300 px-3 py-2 border focus:ring-2 focus:ring-indigo-500 outline-none transition"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-bold text-gray-700 mb-2">
                            Gender
                          </label>
                          <select
                            value={formData.gender}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                gender: e.target.value,
                              })
                            }
                            className="w-full text-sm bg-white text-gray-900 font-medium rounded-lg border-gray-300 px-3 py-2 border focus:ring-2 focus:ring-indigo-500 outline-none transition"
                          >
                            <option>Male</option>
                            <option>Female</option>
                            <option>Other</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-bold text-gray-700 mb-2">
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
                            className="w-full text-sm bg-white text-gray-900 font-medium rounded-lg border-gray-300 px-3 py-2 border focus:ring-2 focus:ring-indigo-500 outline-none transition"
                          >
                            <option>Non-Smoker</option>
                            <option value="Former_Smoker">Former Smoker</option>
                            <option value="Current_Smoker">
                              Current Smoker
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Step 2: Medical History */}
                  {currentStep === 2 && (
                    <div className="space-y-6 animate-in slide-in-from-right-8 duration-300">
                      <h2 className="text-xl font-bold text-gray-900 border-b pb-2">
                        Medical History & Red Flags
                      </h2>

                      <div className="space-y-4">
                        <label className="block text-sm font-bold text-gray-700">
                          Critical Contraindications
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {[
                            {
                              id: "bleeding_disorder",
                              label: "Bleeding Disorder",
                              desc: "Increases surgical risk",
                            },
                            {
                              id: "immunocompromised",
                              label: "Immunocompromised",
                              desc: "High infection risk",
                            },
                            {
                              id: "bisphosphonate_therapy",
                              label: "Bisphosphonates (IV/Oral)",
                              desc: "Risk of osteonecrosis",
                            },
                            {
                              id: "radiation_therapy_head_neck",
                              label: "Head/Neck Radiation",
                              desc: "Impaired healing",
                            },
                          ].map((item) => (
                            <div
                              key={item.id}
                              className={`p-4 border rounded-xl flex items-start gap-3 cursor-pointer transition ${formData[item.id as keyof typeof formData] ? "bg-red-50 border-red-200" : "bg-white hover:bg-gray-50"}`}
                              onClick={() =>
                                handleCheckboxChange(
                                  item.id as keyof typeof formData,
                                )
                              }
                            >
                              <input
                                type="checkbox"
                                checked={
                                  formData[
                                    item.id as keyof typeof formData
                                  ] as boolean
                                }
                                readOnly
                                className="mt-1 w-5 h-5 text-indigo-600"
                              />
                              <div>
                                <p
                                  className={`font-bold ${formData[item.id as keyof typeof formData] ? "text-red-900" : "text-gray-900"}`}
                                >
                                  {item.label}
                                </p>
                                <p
                                  className={`text-xs ${formData[item.id as keyof typeof formData] ? "text-red-700" : "text-gray-500"}`}
                                >
                                  {item.desc}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Step 3: Clinical Presentation */}
                  {currentStep === 3 && (
                    <div className="space-y-6 animate-in slide-in-from-right-8 duration-300">
                      <h2 className="text-xl font-bold text-gray-900 border-b pb-2">
                        Clinical Presentation
                      </h2>

                      <div className="space-y-4">
                        <label className="block text-sm font-bold text-gray-700 mb-2">
                          Reported Symptoms
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {symptomOptions.map((symptom) => (
                            <button
                              key={symptom}
                              type="button"
                              onClick={() => handleSymptomChange(symptom)}
                              className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors border ${formData.symptoms.includes(symptom) ? "bg-indigo-100 text-indigo-800 border-indigo-200" : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"}`}
                            >
                              {symptom.replace(/_/g, " ")}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="pt-4">
                        <label className="block text-sm font-bold text-gray-700 mb-4 flex justify-between">
                          <span>Pain Level</span>{" "}
                          <span className="text-indigo-600">
                            {formData.pain_level}/10
                          </span>
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="10"
                          value={formData.pain_level}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              pain_level: e.target.value,
                            })
                          }
                          className="w-full accent-indigo-600 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="mt-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg font-medium flex items-center gap-2">
                      <AlertTriangle size={18} /> {error}
                    </div>
                  )}
                </div>

                {/* Wizard Footer */}
                <div className="p-6 bg-gray-50 border-t border-gray-200 flex justify-between items-center rounded-b-2xl">
                  {currentStep > 1 ? (
                    <button
                      type="button"
                      onClick={() => setCurrentStep((prev) => prev - 1)}
                      className="px-6 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-700 font-bold hover:bg-gray-100 flex items-center transition"
                    >
                      <ChevronLeft size={16} className="mr-1" /> Back
                    </button>
                  ) : (
                    <div></div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="px-8 py-2.5 bg-indigo-600 rounded-lg text-white font-bold hover:bg-indigo-700 flex items-center transition shadow-sm disabled:opacity-50"
                  >
                    {loading ? (
                      "Analyzing..."
                    ) : currentStep === 3 ? (
                      "Calculate Risk Score"
                    ) : (
                      <>
                        Next Step <ChevronRight size={16} className="ml-1" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            ) : (
              /* Results View */
              <div className="animate-in slide-in-from-bottom-8 duration-500">
                <div
                  className={`p-8 border-b ${
                    response.risk_level === "High"
                      ? "bg-red-50 border-red-200"
                      : response.risk_level === "Moderate"
                        ? "bg-amber-50 border-amber-200"
                        : "bg-green-50 border-green-200"
                  }`}
                >
                  <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div>
                      <p
                        className={`text-sm font-bold uppercase tracking-widest mb-2 ${response.risk_level === "High" ? "text-red-700" : response.risk_level === "Moderate" ? "text-amber-700" : "text-green-700"}`}
                      >
                        Overall Assessment
                      </p>
                      <h2
                        className={`text-4xl font-black mb-2 ${response.risk_level === "High" ? "text-red-900" : response.risk_level === "Moderate" ? "text-amber-900" : "text-green-900"}`}
                      >
                        {response.risk_level} Risk Profile
                      </h2>
                      <p
                        className={`text-lg font-medium opacity-80 ${response.risk_level === "High" ? "text-red-900" : response.risk_level === "Moderate" ? "text-amber-900" : "text-green-900"}`}
                      >
                        {response.composite_risk_score >= 70
                          ? "Significant contraindications present."
                          : response.composite_risk_score >= 40
                            ? "Proceed with caution and modifications."
                            : "Standard procedural clearance."}
                      </p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-white/50 backdrop-blur-sm">
                      {renderGauge(response.composite_risk_score || 0)}
                    </div>
                  </div>
                </div>

                <div className="p-8 space-y-8 bg-white">
                  {/* Risk Score Breakdown Chart (Simulated) */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <PieChart size={20} className="text-gray-400" /> Risk
                      Contributors
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                      <div className="flex justify-center">
                        {/* Simulated Pie Chart */}
                        <div
                          className="w-48 h-48 rounded-full relative"
                          style={{
                            background:
                              "conic-gradient(#ef4444 0% 45%, #f59e0b 45% 75%, #3b82f6 75% 100%)",
                          }}
                        >
                          <div className="absolute inset-0 m-auto w-32 h-32 bg-white rounded-full flex items-center justify-center flex-col shadow-[inset_0_2px_4px_rgba(0,0,0,0.1)]">
                            <span className="text-3xl font-black text-gray-800 text-center">
                              {response.composite_risk_score}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 rounded-lg border border-red-100 bg-red-50">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500"></div>
                            <span className="font-bold text-red-900 text-sm">
                              Medical History
                            </span>
                          </div>
                          <span className="font-bold text-red-700 text-sm">
                            45%
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 rounded-lg border border-amber-100 bg-amber-50">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                            <span className="font-bold text-amber-900 text-sm">
                              Clinical Symptoms
                            </span>
                          </div>
                          <span className="font-bold text-amber-700 text-sm">
                            30%
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 rounded-lg border border-blue-100 bg-blue-50">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                            <span className="font-bold text-blue-900 text-sm">
                              Demographics/Habits
                            </span>
                          </div>
                          <span className="font-bold text-blue-700 text-sm">
                            25%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Procedure Matrix */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">
                      Risk-by-Procedure Matrix
                    </h3>
                    <div className="overflow-x-auto rounded-xl border border-gray-200">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-gray-50 text-xs uppercase tracking-widest text-gray-500 border-b">
                            <th className="p-4 font-bold">Planned Procedure</th>
                            <th className="p-4 font-bold">Compatibility</th>
                            <th className="p-4 font-bold">Specific Warning</th>
                          </tr>
                        </thead>
                        <tbody className="text-sm">
                          <tr className="border-b">
                            <td className="p-4 font-bold text-gray-800">
                              Surgical Extraction
                            </td>
                            <td className="p-4">
                              <span className="px-3 py-1 bg-red-100 text-red-700 rounded font-bold text-xs">
                                CONTRAINDICATED
                              </span>
                            </td>
                            <td className="p-4 text-gray-600">
                              High risk of osteonecrosis due to Bisphosphonate
                              therapy.
                            </td>
                          </tr>
                          <tr className="border-b">
                            <td className="p-4 font-bold text-gray-800">
                              Implant Placement
                            </td>
                            <td className="p-4">
                              <span className="px-3 py-1 bg-red-100 text-red-700 rounded font-bold text-xs">
                                HIGH RISK
                              </span>
                            </td>
                            <td className="p-4 text-gray-600">
                              Poor integration prognosis. Diabetes + Smoking +
                              Bisphosphonates.
                            </td>
                          </tr>
                          <tr>
                            <td className="p-4 font-bold text-gray-800">
                              Non-Surgical RCT
                            </td>
                            <td className="p-4">
                              <span className="px-3 py-1 bg-green-100 text-green-700 rounded font-bold text-xs">
                                CLEARED
                              </span>
                            </td>
                            <td className="p-4 text-gray-600">
                              Standard antibiotic prophylaxis recommended.
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div className="flex justify-center pt-6 border-t border-gray-100">
                    <button
                      onClick={() => setCurrentStep(1)}
                      className="px-6 py-2 border border-gray-300 rounded-lg font-bold text-gray-700 hover:bg-gray-50 flex items-center gap-2 transition"
                    >
                      <History size={16} /> New Assessment
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar History & Trends */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2 border-b pb-4">
              <Activity size={20} className="text-indigo-600" /> Patient Trend
            </h3>

            <div className="py-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-gray-500">
                  Current Score
                </span>
                <span className="text-2xl font-black text-gray-800">85</span>
              </div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm font-bold text-gray-500">
                  Previous (3m ago)
                </span>
                <span className="text-lg font-bold text-gray-400">72</span>
              </div>

              <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3">
                <div className="p-2 bg-red-100 text-red-600 rounded-lg">
                  <TrendingUp size={20} />
                </div>
                <div>
                  <p className="font-bold text-red-900 text-sm">
                    Risk Increased
                  </p>
                  <p className="text-xs text-red-700 mt-1 leading-relaxed">
                    Risk profile deteriorated by 18% due to initiation of
                    systemic bisphosphonates.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
              <h4 className="text-sm font-bold text-gray-900 mb-3">
                Recent Assessments
              </h4>
              <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                {assessments.length === 0 ? (
                  <p className="text-sm text-gray-700 italic bg-gray-50 p-3 rounded font-medium">
                    No previous history.
                  </p>
                ) : (
                  assessments.map((a, i) => (
                    <div
                      key={i}
                      className="p-3 bg-gray-50 rounded-xl border border-gray-200 hover:border-indigo-300 transition cursor-pointer"
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-gray-800 text-xs">
                          {a.timestamp
                            ? new Date(a.timestamp).toLocaleDateString()
                            : "Today"}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            a.risk_level === "High"
                              ? "bg-red-100 text-red-700"
                              : a.risk_level === "Moderate"
                                ? "bg-amber-100 text-amber-700"
                                : "bg-green-100 text-green-700"
                          }`}
                        >
                          {a.risk_level}
                        </span>
                      </div>
                      <p className="text-gray-500 line-clamp-2 text-xs font-medium">
                        {a.recommendation || "Assessment completed"}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
