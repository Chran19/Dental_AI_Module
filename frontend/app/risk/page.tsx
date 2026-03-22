"use client";

import { useState } from "react";
import Link from "next/link";
import { assessRisk, getRiskAssessments } from "@/lib/api";
import { useAuth } from "@/app/providers";
import { useEffect } from "react";

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
      console.log("[Risk UI] Success:", result);
      setResponse(result);
      setSuccess("✓ Risk assessment completed successfully!");

      // Reset form
      setFormData({
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
        bleeding_disorder: false,
        immunocompromised: false,
        bisphosphonate_therapy: false,
        radiation_therapy_head_neck: false,
      });
    } catch (err: any) {
      setError(err.message || "Assessment failed");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <h1 className="text-3xl font-bold text-gray-900">Risk Assessment</h1>
          <p className="mt-2 text-gray-600">
            AI-powered implant candidacy and surgical risk analysis
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {/* Patient Demographics */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Patient Information
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Patient ID"
                  value={formData.patient_id}
                  onChange={(e) =>
                    setFormData({ ...formData, patient_id: e.target.value })
                  }
                  required
                  className="rounded-lg border px-4 py-2"
                />
                <input
                  type="number"
                  placeholder="Age"
                  min="1"
                  max="120"
                  value={formData.age}
                  onChange={(e) =>
                    setFormData({ ...formData, age: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <select
                  value={formData.gender}
                  onChange={(e) =>
                    setFormData({ ...formData, gender: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
                <select
                  value={formData.smoking_status}
                  onChange={(e) =>
                    setFormData({ ...formData, smoking_status: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2"
                >
                  <option value="Non-Smoker">Non-Smoker</option>
                  <option value="Former_Smoker">Former Smoker</option>
                  <option value="Current_Smoker">Current Smoker</option>
                </select>
              </div>
            </div>

            {/* Clinical Presentation */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Clinical Presentation
              </h3>
              <input
                type="text"
                placeholder="Chief Complaint"
                value={formData.chief_complaint}
                onChange={(e) =>
                  setFormData({ ...formData, chief_complaint: e.target.value })
                }
                required
                className="w-full rounded-lg border px-4 py-2"
              />

              <label className="block mt-4 text-sm font-medium text-gray-700">
                Associated Symptoms
              </label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {symptomOptions.map((symptom) => (
                  <label key={symptom} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={(formData.symptoms || []).includes(symptom)}
                      onChange={(e) => {
                        const current = formData.symptoms || [];
                        if (e.target.checked) {
                          setFormData({
                            ...formData,
                            symptoms: [...current, symptom],
                          });
                        } else {
                          setFormData({
                            ...formData,
                            symptoms: current.filter((s) => s !== symptom),
                          });
                        }
                      }}
                      className="mr-2"
                    />
                    {symptom.replace(/_/g, " ")}
                  </label>
                ))}
              </div>
            </div>

            {/* Clinical Findings */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Clinical Findings
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
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
                    className="w-full mt-2"
                  />
                  <span className="text-sm text-gray-600">
                    {formData.pain_level}/10
                  </span>
                </div>

                <select
                  value={formData.swelling_grade}
                  onChange={(e) =>
                    setFormData({ ...formData, swelling_grade: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2 h-fit"
                >
                  <option value="None">No Swelling</option>
                  <option value="Mild">Mild</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Severe">Severe</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <input
                  type="text"
                  placeholder="Tooth Site (e.g., 11)"
                  value={formData.tooth_site}
                  onChange={(e) =>
                    setFormData({ ...formData, tooth_site: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2"
                />
                <select
                  value={formData.jaw_region}
                  onChange={(e) =>
                    setFormData({ ...formData, jaw_region: e.target.value })
                  }
                  className="rounded-lg border px-4 py-2"
                >
                  <option value="Anterior_Maxilla">Anterior Maxilla</option>
                  <option value="Posterior_Maxilla">Posterior Maxilla</option>
                  <option value="Anterior_Mandible">Anterior Mandible</option>
                  <option value="Posterior_Mandible">Posterior Mandible</option>
                </select>
              </div>
            </div>

            {/* Risk Factors */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Risk Factors
              </h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.bleeding_disorder}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        bleeding_disorder: e.target.checked,
                      })
                    }
                    className="mr-3"
                  />
                  <span>Bleeding Disorder</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.immunocompromised}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        immunocompromised: e.target.checked,
                      })
                    }
                    className="mr-3"
                  />
                  <span>Immunocompromised</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.bisphosphonate_therapy}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        bisphosphonate_therapy: e.target.checked,
                      })
                    }
                    className="mr-3"
                  />
                  <span>Bisphosphonate Therapy</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.radiation_therapy_head_neck}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        radiation_therapy_head_neck: e.target.checked,
                      })
                    }
                    className="mr-3"
                  />
                  <span>Radiation Therapy (Head/Neck)</span>
                </label>
              </div>
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
                <strong>Error:</strong> {error}
                <p className="text-sm mt-2">
                  Check browser console (F12) for more details
                </p>
              </div>
            )}

            {success && (
              <div className="rounded-lg bg-green-50 p-4 text-green-700 border border-green-200">
                {success}
              </div>
            )}

            {response && (
              <div className="rounded-lg bg-blue-50 p-4 border border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-2">
                  Backend Response:
                </h4>
                <pre className="bg-white p-3 rounded text-sm overflow-auto max-h-96 text-gray-800 border border-blue-100">
                  {JSON.stringify(response, null, 2)}
                </pre>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-indigo-600 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? "Running Assessment..." : "Run Risk Assessment"}
            </button>
          </form>

          {/* Assessment History */}
          <div className="mt-12 border-t pt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Recent Assessments
            </h2>
            {assessments.length === 0 ? (
              <p className="text-gray-600">
                No assessments recorded yet. Submit a risk assessment above to
                see results.
              </p>
            ) : (
              <div className="space-y-4">
                {assessments.map((assessment, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-4 bg-blue-50 border-blue-200"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-gray-900">
                          Patient: {assessment.patient_id}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          Risk Level:{" "}
                          <span className="font-semibold">
                            {assessment.risk_level}
                          </span>
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-lg">
                          {assessment.composite_risk_score}%
                        </p>
                        <p className="text-xs text-gray-600">Risk Score</p>
                      </div>
                    </div>
                    {assessment.implant_feasibility && (
                      <p className="text-sm mt-2 text-gray-700">
                        Implant Feasibility:{" "}
                        <span className="font-semibold">
                          {assessment.implant_feasibility}
                        </span>
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
