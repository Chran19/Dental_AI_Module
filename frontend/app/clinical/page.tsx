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
    patient_id: "",
    chief_complaint: "",
    observations: "",
    treatment_plan: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await submitClinicalInput(formData);
      setSuccess("Clinical input saved successfully!");
      setFormData({
        patient_id: "",
        chief_complaint: "",
        observations: "",
        treatment_plan: "",
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <h1 className="text-3xl font-bold text-gray-900">Clinical Input</h1>
          <p className="mt-2 text-gray-600">
            Enter clinical observations and data
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <input
              type="text"
              placeholder="Patient ID"
              value={formData.patient_id}
              onChange={(e) =>
                setFormData({ ...formData, patient_id: e.target.value })
              }
              required
              className="w-full rounded-lg border px-4 py-2"
            />
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
            <textarea
              placeholder="Observations"
              value={formData.observations}
              onChange={(e) =>
                setFormData({ ...formData, observations: e.target.value })
              }
              rows={5}
              className="w-full rounded-lg border px-4 py-2"
            />
            <textarea
              placeholder="Treatment Plan"
              value={formData.treatment_plan}
              onChange={(e) =>
                setFormData({ ...formData, treatment_plan: e.target.value })
              }
              rows={5}
              className="w-full rounded-lg border px-4 py-2"
            />

            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
                {error}
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
              {loading ? "Saving..." : "Save Clinical Input"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
