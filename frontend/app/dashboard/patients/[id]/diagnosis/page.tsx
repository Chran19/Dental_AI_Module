"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import StepNavigation from "@/components/clinical/StepNavigation";
import { useAuth } from "@/app/providers";
import {
  FileText,
  Clock,
  User,
  AlertCircle,
  CheckCircle,
  Calendar,
  Search,
  ChevronDown,
  ChevronUp,
  Activity,
  Image as ImageIcon,
  Check,
  ClipboardList,
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
  overdue: boolean;
  clinical_findings: string[];
  last_treatment_date: string;
  next_review_date: string;
}

export default function DiagnosisPage() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const patientId = params?.id as string;
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "all" | "Active" | "Resolved" | "Monitoring"
  >("all");
  const [severityFilter, setSeverityFilter] = useState<
    "all" | "Low" | "Moderate" | "High"
  >("all");

  // Expanded card state
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  // Modal states
  const [viewMediaDiagnosis, setViewMediaDiagnosis] = useState<string | null>(
    null,
  );
  const [updateStatusDiagnosis, setUpdateStatusDiagnosis] = useState<
    string | null
  >(null);
  const [updateStatusValue, setUpdateStatusValue] = useState<
    "Active" | "Monitoring" | "Resolved"
  >("Active");
  const [followUpDiagnosis, setFollowUpDiagnosis] = useState<string | null>(
    null,
  );
  const [followUpDate, setFollowUpDate] = useState("");
  const [followUpNotes, setFollowUpNotes] = useState("");

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
            condition: "Dental Caries (Class II)",
            severity: "Moderate",
            status: "Active",
            recommendation: "Restorative treatment required",
            treatment_plan:
              "Composite filling on tooth 16 DO. Avoid cold drinks.",
            overdue: true,
            clinical_findings: [
              "Pain on biting",
              "Visible cavitation",
              "Thermal sensitivity",
            ],
            last_treatment_date: "2023-11-15",
            next_review_date: "2024-04-05",
          },
          {
            id: "2",
            patient_name: "Jane Smith",
            patient_id: "P002",
            diagnosis_date: "2024-03-18",
            condition: "Gingivitis",
            severity: "Low",
            status: "Monitoring",
            recommendation: "Follow-up in 3 months",
            treatment_plan:
              "Scale and polish completed. Prescribed chlorhexidine mouthwash.",
            overdue: false,
            clinical_findings: [
              "Bleeding on probing",
              "Red, swollen gums",
              "No attachment loss",
            ],
            last_treatment_date: "2024-03-18",
            next_review_date: "2024-06-18",
          },
          {
            id: "3",
            patient_name: "Robert Johnson",
            patient_id: "P003",
            diagnosis_date: "2024-02-10",
            condition: "Irreversible Pulpitis",
            severity: "High",
            status: "Active",
            recommendation: "Root canal therapy urgent",
            treatment_plan:
              "Endodontic access, extirpation, medication. Schedule for obturation.",
            overdue: true,
            clinical_findings: [
              "Spontaneous severe pain",
              "Prolonged pain to cold",
              "Tender to percussion",
            ],
            last_treatment_date: "2022-05-20",
            next_review_date: "2024-02-15",
          },
          {
            id: "4",
            patient_name: "Emily Davis",
            patient_id: "P004",
            diagnosis_date: "2024-01-25",
            condition: "Periodontitis (Stage II, Grade B)",
            severity: "Moderate",
            status: "Resolved",
            recommendation: "Maintain routine hygiene appointments",
            treatment_plan:
              "Non-surgical periodontal therapy completed. Pocket depths reduced < 4mm.",
            overdue: false,
            clinical_findings: [
              "Probing depths 5-6mm initially",
              "Radiographic bone loss 15-33%",
              "Mobility Grade 1",
            ],
            last_treatment_date: "2024-02-28",
            next_review_date: "2024-08-28",
          },
        ]);
        setLoading(false);
      }, 600);
    }
  }, [isAuthenticated]);

  // Handler functions for modal actions
  const handleViewMedia = (diagnosisId: string) => {
    setViewMediaDiagnosis(diagnosisId);
  };

  const handleUpdateStatus = (diagnosisId: string, currentStatus: string) => {
    setUpdateStatusDiagnosis(diagnosisId);
    setUpdateStatusValue(currentStatus as "Active" | "Monitoring" | "Resolved");
  };

  const handleSaveStatus = () => {
    if (updateStatusDiagnosis) {
      setDiagnoses((prev) =>
        prev.map((d) =>
          d.id === updateStatusDiagnosis
            ? { ...d, status: updateStatusValue }
            : d,
        ),
      );
      setUpdateStatusDiagnosis(null);
    }
  };

  const handleFollowUp = (diagnosisId: string) => {
    setFollowUpDiagnosis(diagnosisId);
    setFollowUpDate("");
    setFollowUpNotes("");
  };

  const handleSaveFollowUp = () => {
    if (followUpDiagnosis && followUpDate) {
      setDiagnoses((prev) =>
        prev.map((d) =>
          d.id === followUpDiagnosis
            ? { ...d, next_review_date: followUpDate }
            : d,
        ),
      );
      setFollowUpDiagnosis(null);
    }
  };

  // Derived Stats
  const stats = {
    active: diagnoses.filter((d) => d.status === "Active").length,
    monitoring: diagnoses.filter((d) => d.status === "Monitoring").length,
    resolved: diagnoses.filter((d) => d.status === "Resolved").length,
    overdue: diagnoses.filter((d) => d.overdue && d.status !== "Resolved")
      .length,
  };

  const filteredDiagnoses = diagnoses.filter((d) => {
    // Patient filter
    const patientMatch = !patientId || d.patient_id === patientId || patientId === "P001" /* mock matching */;

    // Search filter
    const searchLower = searchQuery.toLowerCase();
    const searchMatch =
      !searchQuery ||
      d.patient_name.toLowerCase().includes(searchLower) ||
      d.patient_id.toLowerCase().includes(searchLower) ||
      d.condition.toLowerCase().includes(searchLower);

    // Status filter
    const statusMatch = statusFilter === "all" || d.status === statusFilter;    

    // Severity filter
    const severityMatch =
      severityFilter === "all" || d.severity === severityFilter;

    return patientMatch && searchMatch && statusMatch && severityMatch;

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case "High":
        return {
          tag: "bg-red-100 text-red-700 border-red-300",
          bar: "bg-red-500",
          text: "text-red-700",
        };
      case "Moderate":
        return {
          tag: "bg-orange-100 text-orange-700 border-orange-300",
          bar: "bg-orange-500",
          text: "text-orange-700",
        };
      case "Low":
        return {
          tag: "bg-blue-100 text-blue-700 border-blue-300",
          bar: "bg-blue-400",
          text: "text-blue-700",
        };
      default:
        return {
          tag: "bg-gray-100 text-gray-700 border-gray-300",
          bar: "bg-gray-400",
          text: "text-gray-700",
        };
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === "Active")
      return <AlertCircle className="text-orange-500" size={18} />;
    if (status === "Resolved")
      return <CheckCircle className="text-green-500" size={18} />;
    return <Activity className="text-blue-500" size={18} />;
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-8 bg-gray-50 min-h-screen pb-10">
      {/* Header & Stats Dashboard */}
      <div className="bg-white border-b border-gray-200 px-6 py-8 shadow-sm">
        <div className="max-w-6xl mx-auto space-y-8">
          <div>            <Link
              href={`/dashboard/patients/${patientId}`}
              className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center mb-4"
            >
              <Activity size={20} className="mr-1" /> Back to Patient Profile
            </Link>            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <ClipboardList className="text-indigo-600 font-bold" size={32} />
              Diagnoses & Conditions
            </h1>
            <p className="text-gray-600 mt-2 text-lg">
              Comprehensive case management and treatment tracking
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-200 flex flex-col justify-between hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                  Total
                </span>
                <FileText size={20} className="text-gray-400" />
              </div>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {diagnoses.length}
              </p>
            </div>

            <div className="bg-orange-50 rounded-xl p-5 border border-orange-200 flex flex-col justify-between hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-orange-700 uppercase tracking-wider">
                  Active
                </span>
                <AlertCircle size={20} className="text-orange-500" />
              </div>
              <p className="text-3xl font-bold text-orange-800 mt-2">
                {stats.active}
              </p>
              {stats.overdue > 0 && (
                <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full mt-2 self-start">
                  {stats.overdue} Overdue
                </span>
              )}
            </div>

            <div className="bg-blue-50 rounded-xl p-5 border border-blue-200 flex flex-col justify-between hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-blue-700 uppercase tracking-wider">
                  Monitoring
                </span>
                <Activity size={20} className="text-blue-500" />
              </div>
              <p className="text-3xl font-bold text-blue-800 mt-2">
                {stats.monitoring}
              </p>
            </div>

            <div className="bg-green-50 rounded-xl p-5 border border-green-200 flex flex-col justify-between hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-green-700 uppercase tracking-wider">
                  Resolved
                </span>
                <CheckCircle size={20} className="text-green-500" />
              </div>
              <p className="text-3xl font-bold text-green-800 mt-2">
                {stats.resolved}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 space-y-6">
        {/* Advanced Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                size={18}
              />
              <input
                type="text"
                placeholder="Search patient name, ID, or condition..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm text-gray-900 placeholder-gray-700"
              />
            </div>

            {/* Status Dropdown */}
            <div className="lg:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="w-full py-2.5 px-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium text-gray-700 bg-white"
              >
                <option value="all">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Monitoring">Monitoring</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>

            {/* Severity Dropdown */}
            <div className="lg:w-48">
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value as any)}
                className="w-full py-2.5 px-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium text-gray-700 bg-white"
              >
                <option value="all">All Severities</option>
                <option value="High">High Severity</option>
                <option value="Moderate">Moderate</option>
                <option value="Low">Low Severity</option>
              </select>
            </div>
          </div>
        </div>

        {/* Diagnoses List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-20 bg-white rounded-xl border border-gray-200 shadow-sm">
              <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto"></div>
              <p className="mt-4 font-medium text-gray-700">Loading cases...</p>
            </div>
          ) : filteredDiagnoses.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl border border-gray-200 shadow-sm">
              <ClipboardList className="mx-auto text-gray-300 mb-4" size={56} />
              <h3 className="text-lg font-bold text-gray-800">
                No diagnoses found
              </h3>
              <p className="text-gray-500 mt-2">
                Try adjusting your search or filters.
              </p>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setStatusFilter("all");
                  setSeverityFilter("all");
                }}
                className="mt-6 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            filteredDiagnoses.map((diagnosis) => {
              const styles = getSeverityStyle(diagnosis.severity);
              const isExpanded = expandedCard === diagnosis.id;

              return (
                <div
                  key={diagnosis.id}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all duration-300 hover:shadow-md"
                >
                  {/* Left Color Bar indicating Severity */}
                  <div className="flex">
                    <div className={`w-1.5 ${styles.bar}`}></div>

                    <div className="p-0 flex-1">
                      {/* Compact / Main View */}
                      <div
                        className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-5 cursor-pointer hover:bg-gray-50"
                        onClick={() =>
                          setExpandedCard(isExpanded ? null : diagnosis.id)
                        }
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1.5">
                            <h3 className="font-bold text-gray-900 text-lg leading-tight">
                              {diagnosis.condition}
                            </h3>
                            <span
                              className={`px-2.5 py-0.5 rounded text-xs font-bold border ${styles.tag}`}
                            >
                              {diagnosis.severity}
                            </span>
                            {diagnosis.overdue &&
                              diagnosis.status !== "Resolved" && (
                                <span className="flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-bold bg-red-100 text-red-700 border border-red-200">
                                  <AlertCircle size={12} /> Overdue
                                </span>
                              )}
                          </div>
                          <div className="flex items-center text-sm font-medium text-gray-600 gap-6">
                            <span className="flex items-center gap-1.5">
                              <User size={15} /> {diagnosis.patient_name}{" "}
                              <span className="text-gray-700 font-medium">
                                ({diagnosis.patient_id})
                              </span>
                            </span>
                            <span className="flex items-center gap-1.5">
                              <Calendar size={15} />{" "}
                              {new Date(
                                diagnosis.diagnosis_date,
                              ).toLocaleDateString()}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-6 lg:justify-end">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(diagnosis.status)}
                            <span className="text-sm font-bold text-gray-700">
                              {diagnosis.status}
                            </span>
                          </div>

                          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
                            {isExpanded ? (
                              <ChevronUp size={20} />
                            ) : (
                              <ChevronDown size={20} />
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Expanded Details View */}
                      {isExpanded && (
                        <div className="p-6 border-t border-gray-100 bg-gray-50 flex flex-col lg:flex-row gap-8 animate-in slide-in-from-top-2 duration-200">
                          {/* Column 1: Findings & Plan */}
                          <div className="flex-1 space-y-6">
                            <div>
                              <h4 className="text-xs uppercase tracking-wider font-bold text-gray-700 mb-3 flex items-center gap-1.5">
                                <FileText size={14} /> Clinical Findings
                              </h4>
                              <ul className="space-y-1.5">
                                {diagnosis.clinical_findings.map(
                                  (finding, idx) => (
                                    <li
                                      key={idx}
                                      className="flex items-start gap-2 text-sm text-gray-700"
                                    >
                                      <div className="w-1.5 h-1.5 mt-1.5 rounded-full bg-indigo-400 flex-shrink-0"></div>
                                      {finding}
                                    </li>
                                  ),
                                )}
                              </ul>
                            </div>

                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <h4 className="text-xs uppercase tracking-wider font-bold text-blue-500 mb-2">
                                Recommendation / Next Steps
                              </h4>
                              <p className="text-sm font-medium text-gray-900 mb-3">
                                {diagnosis.recommendation}
                              </p>

                              <h4 className="text-xs uppercase tracking-wider font-bold text-gray-700 mb-1 flex items-center gap-1.5">
                                Treatment Plan
                              </h4>
                              <p className="text-sm text-gray-700 leading-relaxed">
                                {diagnosis.treatment_plan ||
                                  "No distinct plan recorded."}
                              </p>
                            </div>
                          </div>

                          {/* Column 2: Timeline, Media, Actions */}
                          <div className="lg:w-80 flex flex-col justify-between space-y-6">
                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <h4 className="text-xs uppercase tracking-wider font-bold text-gray-700 mb-3 flex items-center gap-1.5">
                                <Clock size={14} /> Timeline
                              </h4>
                              <div className="relative pl-4 space-y-4 before:content-[''] before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
                                <div className="relative">
                                  <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-green-500 border-2 border-white shadow-sm"></div>
                                  <p className="text-xs text-gray-700 font-medium">
                                    Last Encounter
                                  </p>
                                  <p className="text-sm font-medium text-gray-800">
                                    {new Date(
                                      diagnosis.last_treatment_date,
                                    ).toLocaleDateString()}
                                  </p>
                                </div>
                                <div className="relative">
                                  <div
                                    className={`absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full ${diagnosis.overdue ? "bg-red-500" : "bg-blue-500"} border-2 border-white shadow-sm`}
                                  ></div>
                                  <p className="text-xs text-gray-700 font-medium">
                                    Next Review
                                  </p>
                                  <p
                                    className={`text-sm font-bold ${diagnosis.overdue ? "text-red-600" : "text-gray-800"}`}
                                  >
                                    {new Date(
                                      diagnosis.next_review_date,
                                    ).toLocaleDateString()}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg border border-gray-200 flex items-center justify-between">
                              <div className="flex items-center gap-2 text-sm text-gray-600 font-medium">
                                <ImageIcon
                                  size={16}
                                  className="text-indigo-400"
                                />
                                2 Scans / X-Rays
                              </div>
                              <button
                                onClick={() => handleViewMedia(diagnosis.id)}
                                className="text-indigo-600 text-sm font-bold hover:underline transition"
                              >
                                View Media
                              </button>
                            </div>

                            <div className="flex gap-2">
                              <button
                                onClick={() =>
                                  handleUpdateStatus(
                                    diagnosis.id,
                                    diagnosis.status,
                                  )
                                }
                                className="flex-1 py-2 px-3 bg-white border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50 transition"
                              >
                                Update Status
                              </button>
                              <button
                                onClick={() => handleFollowUp(diagnosis.id)}
                                className="flex-1 py-2 px-3 bg-indigo-600 rounded-lg text-sm font-semibold text-white hover:bg-indigo-700 transition shadow-sm"
                              >
                                Follow-up
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
          <StepNavigation patientId={patientId} currentStep="diagnosis" />
        </div>
      </div>

      {/* View Media Modal */}
      {viewMediaDiagnosis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                Scan Images & X-Rays
              </h2>
              <button
                onClick={() => setViewMediaDiagnosis(null)}
                className="text-gray-700 hover:text-gray-900"
              >
                ✕
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
                <div className="text-center">
                  <ImageIcon size={48} className="text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-700 font-medium">
                    Sample Periapical X-Ray
                  </p>
                  <p className="text-sm text-gray-700">
                    Tooth #16 - Date: 2024-03-15
                  </p>
                </div>
              </div>
              <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
                <div className="text-center">
                  <ImageIcon size={48} className="text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-700 font-medium">
                    Sample Bitewing X-Ray
                  </p>
                  <p className="text-sm text-gray-700">
                    Teeth #26-27 - Date: 2024-03-15
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Update Status Modal */}
      {updateStatusDiagnosis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full">
            <div className="border-b border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900">
                Update Diagnosis Status
              </h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Status
                </label>
                <div className="space-y-2">
                  {["Active", "Monitoring", "Resolved"].map((status) => (
                    <label
                      key={status}
                      className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition"
                    >
                      <input
                        type="radio"
                        name="status"
                        value={status}
                        checked={updateStatusValue === status}
                        onChange={(e) =>
                          setUpdateStatusValue(
                            e.target.value as
                              | "Active"
                              | "Monitoring"
                              | "Resolved",
                          )
                        }
                        className="mr-3"
                      />
                      <span className="text-gray-900 font-medium">
                        {status}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => setUpdateStatusDiagnosis(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveStatus}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Follow-up Modal */}
      {followUpDiagnosis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full">
            <div className="border-b border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900">
                Schedule Follow-up Appointment
              </h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Follow-up Date
                </label>
                <input
                  type="date"
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={followUpNotes}
                  onChange={(e) => setFollowUpNotes(e.target.value)}
                  placeholder="Add any special instructions or notes..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 placeholder-gray-600"
                  rows={3}
                />
              </div>
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => setFollowUpDiagnosis(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveFollowUp}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
                  disabled={!followUpDate}
                >
                  Schedule
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
