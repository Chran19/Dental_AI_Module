"use client";

import { useState } from "react";
import Link from "next/link";
import { submitClinicalInput } from "@/lib/api";
import { useAuth } from "@/app/providers";

export default function ClinicalPage() {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [formData, setFormData] = useState({
    patient_id: "550e8400-e29b-41d4-a716-446655440000",
    age: "45",
    gender: "Male",
    chief_complaint: "Dental sensitivity",
    symptoms: ["Toothache"],
    symptom_duration_days: "7",
    pain_level: "5",
    swelling_grade: "None",
    smoking_status: "Non-Smoker",
    fever_present: false,
    bleeding_disorder: false,
    immunocompromised: false,
    bisphosphonate_therapy: false,
    radiation_therapy_head_neck: false,
    tooth_site: "11",
    jaw_region: "Anterior_Maxilla",
  });

  const symptomOptions = [
    "Toothache",
    "Thermal_Sensitivity_Hot",
    "Thermal_Sensitivity_Cold",
    "Spontaneous_Pain",
    "Pain_On_Biting",
    "Referred_Pain",
    "Swelling_Localized",
    "Swelling_Diffuse",
    "Gum_Bleeding",
    "Tooth_Mobility",
    "Fractured_Tooth",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await submitClinicalInput(formData);
      setSuccess(
        "Clinical input saved successfully! The data has been validated and sent to the backend.",
      );
      setFormData({
        patient_id: "",
        age: "45",
        gender: "Male",
        chief_complaint: "",
        symptoms: ["Toothache"],
        symptom_duration_days: "7",
        pain_level: "5",
        swelling_grade: "None",
        smoking_status: "Non-Smoker",
        fever_present: false,
        bleeding_disorder: false,
        immunocompromised: false,
        bisphosphonate_therapy: false,
        radiation_therapy_head_neck: false,
        tooth_site: "11",
        jaw_region: "Anterior_Maxilla",
      });
    } catch (err: any) {
      setError(err.message || "Failed to save clinical input");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <h1 className="text-3xl font-bold text-gray-900">
            Clinical Assessment
          </h1>
          <p className="mt-2 text-gray-600">
            Enter clinical examination findings and patient information
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {/* Patient & Demographics */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Patient Info
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
                  required
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

            {/* Chief Complaint & Symptoms */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Presenting Complaint
              </h3>
              <input
                type="text"
                placeholder="Chief complaint (e.g., Dental pain and sensitivity)"
                value={formData.chief_complaint}
                onChange={(e) =>
                  setFormData({ ...formData, chief_complaint: e.target.value })
                }
                required
                className="w-full rounded-lg border px-4 py-2"
              />

              <label className="block mt-4 text-sm font-medium text-gray-700">
                Symptoms
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

              <input
                type="number"
                placeholder="Duration (days)"
                min="0"
                max="3650"
                value={formData.symptom_duration_days}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    symptom_duration_days: e.target.value,
                  })
                }
                className="w-full rounded-lg border px-4 py-2 mt-4"
              />
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

            {/* Medical History */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Medical History
              </h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.fever_present}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        fever_present: e.target.checked,
                      })
                    }
                    className="mr-3"
                  />
                  <span>Fever Present</span>
                </label>
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
                  <span>Head & Neck Radiation Therapy</span>
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

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-indigo-600 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? "Processing..." : "Submit Clinical Assessment"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
