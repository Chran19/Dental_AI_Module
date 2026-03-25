"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/app/providers";
import {
  FileText,
  Clock,
  User,
  Stethoscope,
  AlertCircle,
  CheckCircle,
  Calendar,
} from "lucide-react";

interface Diagnosis {
  id: string;
  patient_name: string;
  patient_id: string;
  diagnosis_date: string;
  condition: string;
  severity: "Low" | "Moderate" | "High";
  status: "Active" | "Resolved" | "Monitoring";
  recommendation: string;
  treatment_plan?: string;
}

export default function DiagnosisPage() {
  const { isAuthenticated } = useAuth();
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "active" | "resolved">("all");

  // Mock data - Replace with actual API call
  useEffect(() => {
    if (isAuthenticated) {
      setTimeout(() => {
        setDiagnoses([
          {
            id: "1",
            patient_name: "John Doe",
            patient_id: "P001",
            diagnosis_date: "2024-03-20",
            condition: "Dental Caries",
            severity: "Moderate",
            status: "Active",
            recommendation: "Treatment required",
            treatment_plan: "Filling on tooth 16",
          },
          {
            id: "2",
            patient_name: "Jane Smith",
            patient_id: "P002",
            diagnosis_date: "2024-03-18",
            condition: "Gingivitis",
            severity: "Low",
            status: "Resolved",
            recommendation: "Follow-up in 3 months",
          },
        ]);
        setLoading(false);
      }, 500);
    }
  }, [isAuthenticated]);

  const filteredDiagnoses = diagnoses.filter((d) => {
    if (filter === "active") return d.status === "Active";
    if (filter === "resolved") return d.status === "Resolved";
    return true;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High":
        return "bg-red-100 text-red-700 border-red-300";
      case "Moderate":
        return "bg-yellow-100 text-yellow-700 border-yellow-300";
      case "Low":
        return "bg-green-100 text-green-700 border-green-300";
      default:
        return "bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === "Active")
      return <AlertCircle className="text-orange-500" size={18} />;
    if (status === "Resolved")
      return <CheckCircle className="text-green-500" size={18} />;
    return <Clock className="text-blue-500" size={18} />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Diagnoses</h1>
          <p className="text-gray-600 mt-1">
            Review patient diagnoses and history
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {(["all", "active", "resolved"] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === status
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {/* Diagnoses List */}
      <div className="grid gap-4">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="mt-3 text-gray-600">Loading diagnoses...</p>
          </div>
        ) : filteredDiagnoses.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Stethoscope className="mx-auto text-gray-400 mb-3" size={40} />
            <p className="text-gray-600">No diagnoses found</p>
          </div>
        ) : (
          filteredDiagnoses.map((diagnosis) => (
            <div
              key={diagnosis.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                {/* Left Section */}
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="bg-blue-100 p-2 rounded-lg">
                      <FileText className="text-blue-600" size={20} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {diagnosis.condition}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {diagnosis.patient_name}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar size={16} className="text-gray-400" />
                      <span>
                        {new Date(
                          diagnosis.diagnosis_date,
                        ).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User size={16} className="text-gray-400" />
                      <span>ID: {diagnosis.patient_id}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(diagnosis.status)}
                      <span className="text-sm font-medium">
                        {diagnosis.status}
                      </span>
                    </div>
                  </div>

                  {diagnosis.recommendation && (
                    <p className="text-sm text-gray-700 mt-3 p-2 bg-gray-50 rounded">
                      <span className="font-medium">Recommendation:</span>{" "}
                      {diagnosis.recommendation}
                    </p>
                  )}
                </div>

                {/* Right Section */}
                <div className="flex items-start gap-2">
                  <span
                    className={`px-3 py-1.5 rounded-lg text-sm font-semibold border ${getSeverityColor(
                      diagnosis.severity,
                    )}`}
                  >
                    {diagnosis.severity}
                  </span>
                </div>
              </div>

              {diagnosis.treatment_plan && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm">
                    <span className="font-medium text-gray-900">
                      Treatment Plan:
                    </span>
                    <span className="text-gray-700 ml-2">
                      {diagnosis.treatment_plan}
                    </span>
                  </p>
                </div>
              )}

              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium text-sm">
                View Details →
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
