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
} from "lucide-react";

export default function RiskPage() {
  const { isAuthenticated } = useAuth();
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [formData, setFormData] = useState({
    patient_id: "550e8400-e29b-41d4-a716-446655440000",
    age: "45",
    gender: "Male",
    smoking_status: "Non-Smoker",
    chief_complaint: "Evaluate implant candidacy",
    symptoms: ["Pain_On_Biting"],
    pain_level: "5",
    swelling_grade: "None",
    tooth_site: "11",
    jaw_region: "Anterior_Maxilla",
    systemic_conditions: ["None"],
    bleeding_disorder: false,
    immunocompromised: false,
    bisphosphonate_therapy: false,
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
        console.log("Assessments fetched:", data);
        setAssessments(Array.isArray(data) ? data : []);
      } catch (err: any) {
        console.log("[Risk] No assessment history:", err.message);
      }
    };

    if (isAuthenticated) fetchAssessments();
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const result = await assessRisk(formData);
      setResponse(result);
      setSuccess("Risk assessment completed successfully!");
      setAssessments((prev) => [result, ...prev]);
    } catch (err: any) {
      setError(err.message || "Assessment failed");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (field: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: !prev[field as keyof typeof prev],
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

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Risk Assessment</h1>
        <p className="text-slate-500">
          Evaluate patient risk factors for dental procedures
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Assessment Form */}
        <div className="lg:col-span-2 space-y-6">
          <form
            onSubmit={handleSubmit}
            className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6"
          >
            <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
              <FileText className="text-blue-500" size={20} />
              <h2 className="font-bold text-slate-900">Patient Details</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Patient ID
                </label>
                <input
                  type="text"
                  value={formData.patient_id}
                  onChange={(e) =>
                    setFormData({ ...formData, patient_id: e.target.value })
                  }
                  className="w-full rounded-lg border-slate-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Age
                </label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) =>
                    setFormData({ ...formData, age: e.target.value })
                  }
                  className="w-full rounded-lg border-slate-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Gender
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) =>
                    setFormData({ ...formData, gender: e.target.value })
                  }
                  className="w-full rounded-lg border-slate-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                >
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Smoking Status
                </label>
                <select
                  value={formData.smoking_status}
                  onChange={(e) =>
                    setFormData({ ...formData, smoking_status: e.target.value })
                  }
                  className="w-full rounded-lg border-slate-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                >
                  <option>Non-Smoker</option>
                  <option>Former Smoker</option>
                  <option>Current Smoker</option>
                </select>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <h3 className="font-medium text-slate-900 mb-3">
                Clinical Indicators
              </h3>
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {symptomOptions.map((symptom) => (
                    <button
                      key={symptom}
                      type="button"
                      onClick={() => handleSymptomChange(symptom)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        formData.symptoms.includes(symptom)
                          ? "bg-blue-100 text-blue-700 border border-blue-200"
                          : "bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {symptom.replace(/_/g, " ")}
                    </button>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Pain Level (0-10)
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="10"
                      value={formData.pain_level}
                      onChange={(e) =>
                        setFormData({ ...formData, pain_level: e.target.value })
                      }
                      className="w-full max-w-xs"
                    />
                    <div className="text-right text-sm text-slate-500">
                      {formData.pain_level}/10
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mt-4">
                  <h4 className="text-sm font-medium text-slate-700">
                    Risk Factors
                  </h4>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.bleeding_disorder}
                      onChange={() => handleCheckboxChange("bleeding_disorder")}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-slate-600">
                      Bleeding Disorder
                    </span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.immunocompromised}
                      onChange={() => handleCheckboxChange("immunocompromised")}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-slate-600">
                      Immunocompromised
                    </span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.bisphosphonate_therapy}
                      onChange={() =>
                        handleCheckboxChange("bisphosphonate_therapy")
                      }
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-slate-600">
                      Bisphosphonate Therapy
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full md:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <div className="animate-spin h-5 w-5 border-2 border-white/20 border-t-white rounded-full" />
                ) : (
                  <Save size={18} />
                )}
                Run Assessment
              </button>
            </div>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            {success && (
              <p className="text-green-500 text-sm mt-2">{success}</p>
            )}
          </form>
        </div>

        {/* Results & History */}
        <div className="space-y-6">
          {response && (
            <div className="bg-white p-6 rounded-2xl border border-blue-100 shadow-md animate-in slide-in-from-right">
              <div className="flex items-center gap-2 mb-4 text-blue-800">
                <Activity size={20} />
                <h3 className="font-bold">Latest Assessment</h3>
              </div>
              <div className="space-y-4">
                <div
                  className={`p-4 rounded-xl border ${
                    response.risk_level === "High"
                      ? "bg-red-50 border-red-100 text-red-700"
                      : response.risk_level === "Moderate"
                        ? "bg-amber-50 border-amber-100 text-amber-700"
                        : "bg-green-50 border-green-100 text-green-700"
                  }`}
                >
                  <div className="text-xs font-bold uppercase tracking-wide opacity-70">
                    Risk Level
                  </div>
                  <div className="text-2xl font-black">
                    {response.risk_level || "Unknown"}
                  </div>
                </div>
                <div className="text-sm text-slate-600">
                  <span className="font-bold text-slate-900 block mb-1">
                    Recommendation:
                  </span>
                  {response.recommendation || "Proceed with standard protocol."}
                </div>
              </div>
            </div>
          )}

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-slate-700">
                <History size={20} />
                <h3 className="font-bold">History</h3>
              </div>
              <span className="text-xs bg-slate-100 px-2 py-1 rounded-full text-slate-500">
                {assessments.length}
              </span>
            </div>
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
              {assessments.length === 0 ? (
                <p className="text-sm text-slate-400 italic">
                  No previous assessments.
                </p>
              ) : (
                assessments.map((a, i) => (
                  <div
                    key={i}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm"
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-slate-900">
                        {a.timestamp
                          ? new Date(a.timestamp).toLocaleDateString()
                          : "Recent"}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-bold ${
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
                    <p className="text-slate-500 line-clamp-2 text-xs">
                      {a.recommendation}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
