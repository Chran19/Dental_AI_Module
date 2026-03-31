"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import StepNavigation from "@/components/clinical/StepNavigation";
import { useAuth } from "@/app/providers";
import {
  getTreatmentsByPatient,
  suggestTreatment,
  downloadTreatmentReportPDF,
} from "@/lib/api";
import {
  Plus,
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  Pill,
  User,
  LayoutList,
  AlignLeft,
  Activity,
  Zap,
  ClipboardList,
  Download,
} from "lucide-react";

interface TreatmentPlan {
  id?: string;
  case_id?: string;
  patient_name?: string;
  patient_id?: string;
  diagnosis_ref?: string;
  procedure: string;
  status: "Planned" | "In Progress" | "Completed" | "Cancelled";
  stage: "Pre-op" | "Operative" | "Post-op" | "Review";
  start_date: string;
  end_date?: string;
  days_remaining?: number;
  progress: number;
  description: string;
  plan_date?: string;
  [key: string]: any;
}

export default function TreatmentPage() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const patientId = params?.id as string;
  const [plans, setPlans] = useState<TreatmentPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [viewMode, setViewMode] = useState<"list" | "timeline">("list");
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  // Modal form data
  const [modalData, setModalData] = useState({
    procedure: "Indirect Composite Inlay",
    description: "",
  });

  // Fetch treatment plans from API
  useEffect(() => {
    if (isAuthenticated && patientId) {
      const fetchPlans = async () => {
        try {
          setLoading(true);
          setError(null);
          const data = await getTreatmentsByPatient(patientId);
          setPlans(Array.isArray(data) ? data : []);
        } catch (err) {
          console.error("[Treatment] Failed to fetch plans:", err);
          setError("Failed to load treatment plans");
        } finally {
          setLoading(false);
        }
      };

      fetchPlans();
    }
  }, [isAuthenticated, patientId]);

  const stats = {
    pending: plans.filter((p) => p.status === "Planned").length,
    inProgress: plans.filter((p) => p.status === "In Progress").length,
    completed: plans.filter((p) => p.status === "Completed").length,
  };

  const filteredPlans = plans.filter((p) => {
    // Patient Filter
    const patientMatch = !patientId || p.patient_id === patientId;
    if (!patientMatch) return false;

    if (filter === "active")
      return ["Planned", "In Progress"].includes(p.status);
    if (filter === "completed") return p.status === "Completed";
    return true;
  });

  const getStatusStyle = (status: string) => {
    switch (status) {
      case "Planned":
        return "bg-slate-100 text-slate-700 border-slate-200";
      case "In Progress":
        return "bg-blue-100 text-blue-700 border-blue-200";
      case "Completed":
        return "bg-green-100 text-green-700 border-green-200";
      case "Cancelled":
        return "bg-red-100 text-red-700 border-red-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const renderStageLine = (currentStage: string) => {
    const stages = ["Pre-op", "Operative", "Post-op", "Review"];
    const currentIndex = stages.indexOf(currentStage);

    return (
      <div className="flex items-center w-full mt-4">
        {stages.map((stage, idx) => (
          <div
            key={stage}
            className="flex-1 flex flex-col items-center relative"
          >
            {idx !== 0 && (
              <div
                className={`absolute left-[-50%] top-3 w-full h-1 -z-10 ${idx <= currentIndex ? "bg-indigo-600" : "bg-gray-200"}`}
              ></div>
            )}
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                idx < currentIndex
                  ? "bg-indigo-600 border-indigo-600 text-white"
                  : idx === currentIndex
                    ? "bg-white border-indigo-600 text-indigo-600"
                    : "bg-white border-gray-300 text-gray-400"
              }`}
            >
              {idx < currentIndex ? <CheckCircle size={12} /> : idx + 1}
            </div>
            <span
              className={`text-xs mt-1 font-medium ${idx <= currentIndex ? "text-gray-800" : "text-gray-600"}`}
            >
              {stage}
            </span>
          </div>
        ))}
      </div>
    );
  };

  // Handler functions
  const handleManagePlan = (planId: string) => {
    setSelectedPlanId(planId);
    // Future: open detailed management modal or page
  };

  const handleExportPDF = async () => {
    if (!patientId) return;
    try {
      await downloadTreatmentReportPDF(patientId);
    } catch (err) {
      console.error("[Treatment] Failed to export PDF:", err);
      setError("Failed to generate treatment plan PDF");
    }
  };

  const handleCreatePlan = async () => {
    if (!patientId) return;

    try {
      const payload = {
        patient_id: patientId,
        procedure: modalData.procedure,
        description: modalData.description,
      };

      await suggestTreatment(payload);
      setShowModal(false);

      // Reset modal data
      setModalData({
        procedure: "Indirect Composite Inlay",
        description: "",
      });

      // Refresh plans
      const data = await getTreatmentsByPatient(patientId);
      setPlans(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("[Treatment] Failed to create plan:", err);
      setError("Failed to create treatment plan");
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      {/* Header Dashboard */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div>
              {" "}
              <Link
                href={`/dashboard/patients/${patientId}`}
                className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center mb-4"
              >
                <Activity size={20} className="mr-1" /> Back to Patient Profile
              </Link>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <ClipboardList className="text-indigo-600" /> Treatment
                Management
              </h1>
              <p className="text-gray-600 mt-1">
                Orchestrate patient care pathways from diagnosis to completion
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleExportPDF}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-50 text-indigo-600 rounded-lg font-bold hover:bg-indigo-100 transition border border-indigo-200"
              >
                <Download size={20} /> Export PDF
              </button>
              <button
                onClick={() => setShowModal(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition shadow-sm"
              >
                <Plus size={20} /> New Treatment Plan
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
              <p className="text-xs font-bold text-slate-500 uppercase">
                Pending
              </p>
              <p className="text-2xl font-bold text-slate-800 mt-1">
                {stats.pending}
              </p>
            </div>
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl">
              <p className="text-xs font-bold text-blue-600 uppercase">
                In Progress
              </p>
              <p className="text-2xl font-bold text-blue-800 mt-1">
                {stats.inProgress}
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 p-4 rounded-xl">
              <p className="text-xs font-bold text-green-600 uppercase">
                Completed
              </p>
              <p className="text-2xl font-bold text-green-800 mt-1">
                {stats.completed}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 space-y-6">
        {/* View Toggles & Filters */}
        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-2 rounded-xl border border-gray-200 shadow-sm gap-4">
          <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setViewMode("list")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition ${viewMode === "list" ? "bg-white text-gray-900 shadow-sm" : "text-gray-700 hover:text-gray-900"}`}
            >
              <AlignLeft size={16} /> List View
            </button>
            <button
              onClick={() => setViewMode("timeline")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition ${viewMode === "timeline" ? "bg-white text-gray-900 shadow-sm" : "text-gray-700 hover:text-gray-900"}`}
            >
              <LayoutList size={16} /> Timeline View
            </button>
          </div>

          <div className="flex gap-2 p-1">
            {(["all", "active", "completed"] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  filter === status
                    ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                    : "bg-white text-gray-600 border-transparent hover:bg-gray-50 hover:border-gray-200"
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Treatment Plans Content */}
        {loading ? (
          <div className="text-center py-20">
            <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 font-medium text-gray-600">
              Loading treatment plans...
            </p>
          </div>
        ) : error ? (
          <div className="text-center py-20 bg-white rounded-xl border border-red-200">
            <AlertCircle className="mx-auto text-red-400 mb-4" size={56} />
            <h3 className="text-lg font-bold text-red-800">{error}</h3>
            <p className="text-sm text-red-600 mt-1">Please try again later</p>
          </div>
        ) : filteredPlans.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
            <Pill className="mx-auto text-gray-300 mb-4" size={56} />
            <h3 className="text-lg font-bold text-gray-800">
              No treatment plans found
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Treatment plans will appear here once they are created
            </p>
          </div>
        ) : viewMode === "list" ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredPlans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition flex flex-col"
              >
                {/* Card Header */}
                <div className="p-5 border-b border-gray-100 bg-gray-50">
                  <span
                    className={`px-2.5 py-1 rounded text-xs font-bold border mb-2 inline-block ${getStatusStyle(plan.status)}`}
                  >
                    {plan.status}
                  </span>
                  <h3 className="font-bold text-gray-900 text-lg">
                    {plan.procedure}
                  </h3>
                  <p className="text-sm font-medium text-indigo-600 flex items-center gap-1 mt-1">
                    <Activity size={14} /> {plan.patient_name || "Patient"}
                  </p>
                </div>

                {/* Card Body */}
                <div className="p-5 flex-1 flex flex-col justify-between">
                  <div className="mb-6">
                    <p className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                      Linked Diagnosis
                    </p>
                    <p className="text-sm text-gray-800 bg-gray-50 p-2 rounded border border-gray-100 inline-flex items-center gap-2">
                      <Activity size={14} className="text-indigo-400" />{" "}
                      {plan.diagnosis_ref}
                    </p>
                  </div>

                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-bold text-gray-500 uppercase">
                        Progress Setup
                      </span>
                      <span className="text-xs font-bold text-indigo-600">
                        {plan.progress}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 mb-4 overflow-hidden">
                      <div
                        className="bg-indigo-500 h-2 transition-all"
                        style={{ width: `${plan.progress}%` }}
                      ></div>
                    </div>
                    {renderStageLine(plan.stage)}
                  </div>
                </div>

                {/* Card Footer */}
                <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-between items-center gap-4">
                  <div className="flex items-center gap-4 text-xs font-medium text-gray-600">
                    <div className="flex items-center gap-1.5">
                      <Calendar size={14} className="text-gray-400" /> Starts:{" "}
                      {new Date(plan.start_date).toLocaleDateString()}
                    </div>
                    {plan.days_remaining !== undefined &&
                      plan.status !== "Completed" && (
                        <div className="flex items-center gap-1.5 text-orange-600 bg-orange-50 px-2 py-1 rounded">
                          <Clock size={14} /> {plan.days_remaining} days left
                        </div>
                      )}
                  </div>
                  <button
                    onClick={() => handleManagePlan(plan.id)}
                    className="text-indigo-600 font-bold text-sm hover:underline transition"
                  >
                    Manage
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Timeline/Gantt Alternative View */
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm p-6 overflow-x-auto">
            <div className="min-w-[800px]">
              <div className="grid grid-cols-12 gap-4 pb-4 border-b border-gray-200 text-xs font-bold text-gray-700 uppercase tracking-wider">
                <div className="col-span-3">Patient & Plan</div>
                <div className="col-span-2">Diagnostic Link</div>
                <div className="col-span-7">Timeline (Current Month)</div>
              </div>

              <div className="space-y-6 pt-6">
                {filteredPlans.map((plan) => (
                  <div
                    key={plan.id}
                    className="grid grid-cols-12 gap-4 items-center"
                  >
                    <div className="col-span-3">
                      <p className="font-bold text-gray-900">
                        {plan.patient_name}
                      </p>
                      <p className="text-xs font-semibold text-indigo-600">
                        {plan.procedure}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full whitespace-nowrap overflow-hidden text-ellipsis inline-block max-w-full">
                        {plan.diagnosis_ref}
                      </span>
                    </div>
                    <div className="col-span-7 relative flex items-center h-8 bg-gray-50 rounded-lg">
                      {/* Timeline bar showing treatment progress */}
                      <div className="absolute left-0 w-full flex justify-between px-2 text-[10px] text-gray-300 pointer-events-none">
                        <span>Mar 1</span>
                        <span>Mar 15</span>
                        <span>Mar 31</span>
                      </div>
                      <div
                        className={`absolute h-6 rounded flex items-center px-2 text-[10px] font-bold text-white shadow-sm overflow-hidden ${
                          plan.status === "Completed"
                            ? "bg-green-500"
                            : "bg-indigo-500"
                        }`}
                        style={{
                          left: plan.status === "Completed" ? "10%" : "30%",
                          width: plan.status === "Completed" ? "40%" : "60%",
                        }}
                      >
                        {plan.start_date} - {plan.end_date || "Ongoing"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        <div className="max-w-7xl mx-auto px-6">
          <StepNavigation patientId={patientId} currentStep="treatment" />
        </div>
      </div>

      {/* Treatment Plan Management Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Create Treatment Plan
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Design a new clinical pathway for this patient
                </p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-700 hover:text-gray-900 p-2 text-xl font-bold"
              >
                &times;
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-6 bg-white">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Procedure Type
                </label>
                <select
                  value={modalData.procedure}
                  onChange={(e) =>
                    setModalData({ ...modalData, procedure: e.target.value })
                  }
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900"
                >
                  <option>Indirect Composite Inlay</option>
                  <option>Direct Composite Fill</option>
                  <option>Root Canal Therapy</option>
                  <option>Crown Restoration</option>
                  <option>Periodontal Therapy</option>
                  <option>Dental Implant</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Treatment Description
                </label>
                <textarea
                  rows={3}
                  value={modalData.description}
                  onChange={(e) =>
                    setModalData({ ...modalData, description: e.target.value })
                  }
                  placeholder="Clinical notes and treatment details..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 placeholder-gray-600"
                ></textarea>
              </div>

              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <h4 className="text-xs uppercase tracking-wider font-bold text-indigo-800 mb-2 flex items-center gap-2">
                  <Zap size={14} className="text-amber-500 fill-amber-500" /> AI
                  Treatment Suggestions
                </h4>
                <p className="text-sm text-indigo-700">
                  Treatment recommendations will be generated based on the
                  patient's diagnosis and clinical data
                </p>
              </div>
            </div>

            <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg font-bold hover:bg-gray-100 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleCreatePlan}
                className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition shadow-sm"
              >
                Create Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
