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
  const [formData, setFormData] = useState({
    patient_id: "",
    risk_factors: "",
  });

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const data = await getRiskAssessments();
        setAssessments(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err.message);
      }
    };

    if (isAuthenticated) fetchAssessments();
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await assessRisk(formData);
      setFormData({ patient_id: "", risk_factors: "" });
      const data = await getRiskAssessments();
      setAssessments(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message);
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
            AI-powered risk analysis and recommendations
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-4 border-b pb-8"
          >
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
            <textarea
              placeholder="Risk Factors"
              value={formData.risk_factors}
              onChange={(e) =>
                setFormData({ ...formData, risk_factors: e.target.value })
              }
              rows={4}
              className="w-full rounded-lg border px-4 py-2"
            />

            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-indigo-600 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? "Assessing..." : "Run Risk Assessment"}
            </button>
          </form>

          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Recent Assessments
            </h2>
            {assessments.length === 0 ? (
              <p className="text-gray-600">No assessments yet.</p>
            ) : (
              <div className="space-y-4">
                {assessments.map((assessment, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50">
                    <p className="font-semibold text-gray-900">
                      Patient: {assessment.patient_id}
                    </p>
                    <div className="mt-2 text-sm text-gray-700">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(assessment, null, 2)}
                      </pre>
                    </div>
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
