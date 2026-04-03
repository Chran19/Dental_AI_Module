"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getAssessmentsByPatient } from "@/lib/api";
import { useAuth } from "@/app/providers";
import {
  ChevronLeft,
  ClipboardList,
  Calendar,
  AlertCircle,
  Eye,
  Download,
  Filter,
} from "lucide-react";

interface Assessment {
  id: string;
  patient_id: string;
  doctor_id: string;
  chief_complaint: string;
  urgency_flag: "Low" | "Medium" | "High";
  status: string;
  created_at: string;
  updated_at: string;
  clinical_input_json?: any;
}

export default function AssessmentsPage() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const patientId = (params?.id as string) || "";

  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedAssessment, setSelectedAssessment] =
    useState<Assessment | null>(null);
  const [sortBy, setSortBy] = useState<"recent" | "urgent">("recent");

  useEffect(() => {
    if (isAuthenticated && patientId) {
      loadAssessments();
    }
  }, [isAuthenticated, patientId]);

  const loadAssessments = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getAssessmentsByPatient(patientId);
      const assessmentList = Array.isArray(data) ? data : [];
      setAssessments(assessmentList);
      if (assessmentList.length === 0) {
        setError("No clinical assessments found");
      }
    } catch (err: any) {
      console.error("Failed to load assessments:", err);
      setError(err.message || "Failed to load assessments");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "High":
        return "bg-red-100 text-red-800 border-red-200";
      case "Medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "Low":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const sortedAssessments = [...assessments].sort((a, b) => {
    if (sortBy === "urgent") {
      const urgencyOrder: Record<string, number> = {
        High: 0,
        Medium: 1,
        Low: 2,
      };
      return (
        (urgencyOrder[a.urgency_flag] ?? 3) -
        (urgencyOrder[b.urgency_flag] ?? 3)
      );
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <Link
          href={`/dashboard/patients/${patientId}`}
          className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center mb-6"
        >
          <ChevronLeft size={20} className="mr-1" /> Back to Patient Profile
        </Link>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3 mb-2">
            <ClipboardList className="text-indigo-600" size={40} />
            Clinical Assessments
          </h1>
          <p className="text-gray-600 text-lg">
            View all submitted clinical input assessments for this patient
          </p>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600 font-medium">
                Loading assessments...
              </p>
            </div>
          </div>
        )}

        {error && !loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
            <AlertCircle className="text-blue-600 mx-auto mb-3" size={40} />
            <p className="text-blue-900 font-semibold text-lg">{error}</p>
            <p className="text-blue-700 text-sm mt-2">
              No clinical assessments have been submitted yet for this patient.
            </p>
            <Link
              href={`/dashboard/patients/${patientId}/clinical`}
              className="mt-4 inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition"
            >
              Create Assessment
            </Link>
          </div>
        )}

        {assessments.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-2 text-gray-700">
                <Calendar size={20} />
                <span className="font-semibold">
                  {assessments.length} Assessment
                  {assessments.length !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Filter size={18} className="text-gray-600" />
                <select
                  value={sortBy}
                  onChange={(e) =>
                    setSortBy(e.target.value as "recent" | "urgent")
                  }
                  className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 font-medium text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="recent">Most Recent</option>
                  <option value="urgent">By Urgency</option>
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {sortedAssessments.map((assessment, index) => {
                const assessmentNumber = sortedAssessments.length - index;
                return (
                  <div
                    key={assessment.id}
                    className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-6"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm">
                            #{assessmentNumber}
                          </span>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {assessment.chief_complaint}
                          </h3>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold border ${getUrgencyColor(
                              assessment.urgency_flag,
                            )}`}
                          >
                            {assessment.urgency_flag} Urgency
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar size={16} />
                            <span className="font-medium">
                              {formatDate(assessment.created_at)}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <ClipboardList size={16} />
                            <span className="font-medium capitalize">
                              {assessment.status}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedAssessment(assessment)}
                          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition text-sm"
                        >
                          <Eye size={16} />
                          View
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition text-sm">
                          <Download size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Assessment Detail Modal */}
      {selectedAssessment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-50 border-b border-gray-200 p-6 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm">
                  #
                  {sortedAssessments.findIndex(
                    (a) => a.id === selectedAssessment.id,
                  ) >= 0
                    ? sortedAssessments.length -
                      sortedAssessments.findIndex(
                        (a) => a.id === selectedAssessment.id,
                      )
                    : "?"}
                </span>
                <h2 className="text-2xl font-bold text-gray-900">
                  Assessment Details
                </h2>
              </div>
              <button
                onClick={() => setSelectedAssessment(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-gray-600 text-sm font-medium mb-1">
                    Chief Complaint
                  </p>
                  <p className="text-gray-900 font-semibold text-lg">
                    {selectedAssessment.chief_complaint}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm font-medium mb-1">
                    Urgency Level
                  </p>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${getUrgencyColor(
                      selectedAssessment.urgency_flag,
                    )}`}
                  >
                    {selectedAssessment.urgency_flag}
                  </span>
                </div>
                <div>
                  <p className="text-gray-600 text-sm font-medium mb-1">
                    Status
                  </p>
                  <p className="text-gray-900 font-semibold capitalize">
                    {selectedAssessment.status}
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Detailed Assessment
                </h3>
                {selectedAssessment.clinical_input_json ? (
                  <div className="space-y-6">
                    {selectedAssessment.clinical_input_json.demographics && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold text-gray-900 mb-3">
                          Demographics
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Age</p>
                            <p className="font-semibold text-gray-900">
                              {
                                selectedAssessment.clinical_input_json
                                  .demographics.age
                              }{" "}
                              years
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">Gender</p>
                            <p className="font-semibold text-gray-900">
                              {
                                selectedAssessment.clinical_input_json
                                  .demographics.gender
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {selectedAssessment.clinical_input_json.chief_complaint && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold text-gray-900 mb-2">
                          Chief Complaint
                        </h4>
                        {typeof selectedAssessment.clinical_input_json
                          .chief_complaint === "object" ? (
                          <div className="space-y-2 text-sm">
                            <div>
                              <p className="text-gray-600">
                                Complaint Description
                              </p>
                              <p className="font-semibold text-gray-900">
                                {
                                  selectedAssessment.clinical_input_json
                                    .chief_complaint.description
                                }
                              </p>
                            </div>
                            {selectedAssessment.clinical_input_json
                              .chief_complaint.symptoms && (
                              <div>
                                <p className="text-gray-600">Symptoms</p>
                                <p className="font-semibold text-gray-900">
                                  {Array.isArray(
                                    selectedAssessment.clinical_input_json
                                      .chief_complaint.symptoms,
                                  )
                                    ? selectedAssessment.clinical_input_json.chief_complaint.symptoms.join(
                                        ", ",
                                      )
                                    : selectedAssessment.clinical_input_json
                                        .chief_complaint.symptoms}
                                </p>
                              </div>
                            )}
                            {selectedAssessment.clinical_input_json
                              .chief_complaint.duration_days && (
                              <div>
                                <p className="text-gray-600">Duration</p>
                                <p className="font-semibold text-gray-900">
                                  {
                                    selectedAssessment.clinical_input_json
                                      .chief_complaint.duration_days
                                  }{" "}
                                  days
                                </p>
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-gray-900">
                            {
                              selectedAssessment.clinical_input_json
                                .chief_complaint
                            }
                          </p>
                        )}
                      </div>
                    )}

                    {selectedAssessment.clinical_input_json
                      .clinical_assessment && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold text-gray-900 mb-3">
                          Clinical Assessment
                        </h4>
                        <div className="space-y-2 text-sm">
                          <div>
                            <p className="text-gray-600">Pain Level</p>
                            <p className="font-semibold text-gray-900">
                              {
                                selectedAssessment.clinical_input_json
                                  .clinical_assessment.pain_level
                              }
                              /10
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">Swelling Grade</p>
                            <p className="font-semibold text-gray-900">
                              {
                                selectedAssessment.clinical_input_json
                                  .clinical_assessment.swelling_grade
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {selectedAssessment.clinical_input_json.site_assessment && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold text-gray-900 mb-3">
                          Site Assessment
                        </h4>
                        <div className="space-y-2 text-sm">
                          <div>
                            <p className="text-gray-600">
                              Affected Tooth/Teeth
                            </p>
                            <p className="font-semibold text-gray-900">
                              {Array.isArray(
                                selectedAssessment.clinical_input_json
                                  .site_assessment.tooth_sites,
                              )
                                ? selectedAssessment.clinical_input_json.site_assessment.tooth_sites.join(
                                    ", ",
                                  )
                                : selectedAssessment.clinical_input_json
                                    .site_assessment.tooth_sites}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">Jaw Region</p>
                            <p className="font-semibold text-gray-900">
                              {selectedAssessment.clinical_input_json.site_assessment.jaw_region.replace(
                                /_/g,
                                " ",
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-600 italic">
                    No detailed assessment data available
                  </p>
                )}
              </div>

              <div className="border-t border-gray-200 pt-6 flex gap-4">
                <button
                  onClick={() => setSelectedAssessment(null)}
                  className="flex-1 px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium transition"
                >
                  Close
                </button>
                <Link
                  href={`/dashboard/patients/${patientId}/diagnosis`}
                  className="flex-1 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition text-center"
                >
                  Generate Diagnosis
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
