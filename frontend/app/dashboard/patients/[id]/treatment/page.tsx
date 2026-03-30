"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import StepNavigation from "@/components/clinical/StepNavigation";
import { useAuth } from "@/app/providers";
import {
  Plus,
  DollarSign,
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
  ShieldCheck,
  CreditCard,
  ChevronRight,
  ClipboardList,
} from "lucide-react";

interface TreatmentPlan {
  id: string;
  patient_name: string;
  patient_id: string;
  diagnosis_ref: string;
  procedure: string;
  status: "Planned" | "In Progress" | "Completed" | "Cancelled";
  stage: "Pre-op" | "Operative" | "Post-op" | "Review";
  start_date: string;
  end_date?: string;
  days_remaining?: number;
  cost: number;
  paid: number;
  insurance_covered: boolean;
  progress: number;
  description: string;
}

export default function TreatmentPage() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const patientId = params?.id as string;
  const [plans, setPlans] = useState<TreatmentPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [viewMode, setViewMode] = useState<"list" | "timeline">("list");
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  // Modal form data
  const [modalData, setModalData] = useState({
    patient: "John Doe (P001)",
    diagnosis: "Dental Caries (Class II) - Left Molar",
    procedure: "Indirect Composite Inlay",
    description: "",
    cost: "350",
    insured: false,
  });

  // Mock data
  useEffect(() => {
    if (isAuthenticated) {
      setTimeout(() => {
        setPlans([
          {
            id: "1",
            patient_name: "John Doe",
            patient_id: "P001",
            diagnosis_ref: "Dental Caries (Class II)",
            procedure: "Composite Restorations (x2)",
            status: "In Progress",
            stage: "Operative",
            start_date: "2024-03-15",
            end_date: "2024-04-10",
            days_remaining: 12,
            cost: 450,
            paid: 200,
            insurance_covered: true,
            progress: 50,
            description: "Composite filling on teeth 16, 26.",
          },
          {
            id: "2",
            patient_name: "Jane Smith",
            patient_id: "P002",
            diagnosis_ref: "Irreversible Pulpitis",
            procedure: "Root Canal Therapy & Crown",
            status: "Planned",
            stage: "Pre-op",
            start_date: "2024-04-05",
            end_date: "2024-05-20",
            days_remaining: 52,
            cost: 1200,
            paid: 0,
            insurance_covered: false,
            progress: 0,
            description:
              "Endodontic treatment tooth 36 followed by full ceramic crown.",
          },
          {
            id: "3",
            patient_name: "Mike Johnson",
            patient_id: "P003",
            diagnosis_ref: "Stage II Periodontitis",
            procedure: "Non-Surgical Periodontal Therapy",
            status: "Completed",
            stage: "Review",
            start_date: "2024-01-10",
            end_date: "2024-02-28",
            days_remaining: 0,
            cost: 600,
            paid: 600,
            insurance_covered: true,
            progress: 100,
            description: "Full mouth scaling and root planing.",
          },
        ]);
        setLoading(false);
      }, 600);
    }
  }, [isAuthenticated]);

  const stats = {
    pending: plans.filter((p) => p.status === "Planned").length,
    inProgress: plans.filter((p) => p.status === "In Progress").length,
    completed: plans.filter((p) => p.status === "Completed").length,
    totalRevenue: plans.reduce((acc, curr) => acc + curr.paid, 0),
    totalExpected: plans.reduce((acc, curr) => acc + curr.cost, 0),
  };

  const filteredPlans = plans.filter((p) => {
    // Patient Filter
    const patientMatch =
      !patientId ||
      p.patient_id === patientId ||
      patientId === "P001"; /* mock filter */
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
    // In a real app, this would open a detailed management modal or page
    setShowModal(true);
  };

  const handleCreatePlan = () => {
    const newPlan: TreatmentPlan = {
      id: String(plans.length + 1),
      patient_name: modalData.patient.split(" (")[0],
      patient_id: modalData.patient.split("(")[1]?.replace(")", "") || "P999",
      diagnosis_ref: modalData.diagnosis,
      procedure: modalData.procedure,
      status: "Planned",
      stage: "Pre-op",
      start_date: new Date().toISOString().split("T")[0],
      cost: parseInt(modalData.cost) || 0,
      paid: 0,
      insurance_covered: modalData.insured,
      progress: 0,
      description: modalData.description || "New treatment plan",
    };
    setPlans([...plans, newPlan]);
    setShowModal(false);
    // Reset modal data
    setModalData({
      patient: "John Doe (P001)",
      diagnosis: "Dental Caries (Class II) - Left Molar",
      procedure: "Indirect Composite Inlay",
      description: "",
      cost: "350",
      insured: false,
    });
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
              </Link>{" "}
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <ClipboardList className="text-indigo-600" /> Treatment
                Management
              </h1>
              <p className="text-gray-600 mt-1">
                Orchestrate patient care pathways from diagnosis to completion
              </p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition shadow-sm"
            >
              <Plus size={20} /> New Treatment Plan
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
            <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl md:col-span-2 flex justify-between items-center">
              <div>
                <p className="text-xs font-bold text-emerald-700 uppercase">
                  Revenue Realized / Projected
                </p>
                <p className="text-2xl font-bold text-emerald-900 mt-1">
                  ${stats.totalRevenue}{" "}
                  <span className="text-lg text-emerald-600 font-medium">
                    / ${stats.totalExpected}
                  </span>
                </p>
              </div>
              <div className="bg-emerald-100 p-3 rounded-full text-emerald-600">
                <DollarSign size={24} />
              </div>
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
              Loading schedules...
            </p>
          </div>
        ) : filteredPlans.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
            <Pill className="mx-auto text-gray-300 mb-4" size={56} />
            <h3 className="text-lg font-bold text-gray-800">
              No active plans found
            </h3>
          </div>
        ) : viewMode === "list" ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredPlans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition flex flex-col"
              >
                {/* Card Header */}
                <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-start">
                  <div>
                    <span
                      className={`px-2.5 py-1 rounded text-xs font-bold border mb-2 inline-block ${getStatusStyle(plan.status)}`}
                    >
                      {plan.status}
                    </span>
                    <h3 className="font-bold text-gray-900 text-lg">
                      {plan.procedure}
                    </h3>
                    <p className="text-sm font-medium text-indigo-600 flex items-center gap-1 mt-1">
                      <User size={14} /> {plan.patient_name}{" "}
                      <span className="text-gray-700 font-medium ml-1">
                        ({plan.patient_id})
                      </span>
                    </p>
                  </div>

                  {/* Mini Financials */}
                  <div className="flex flex-col items-end">
                    <div className="flex items-center gap-1 text-sm font-bold text-gray-800">
                      <DollarSign size={14} className="text-gray-400" />
                      {plan.cost}
                    </div>
                    <div className="text-xs text-gray-500 font-medium">
                      {plan.paid >= plan.cost ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <CheckCircle size={10} /> Fully Paid
                        </span>
                      ) : (
                        `Paid: $${plan.paid}`
                      )}
                    </div>
                    {plan.insurance_covered && (
                      <span className="text-[10px] uppercase font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded mt-1 flex items-center gap-1 border border-blue-100">
                        <ShieldCheck size={10} /> Insured
                      </span>
                    )}
                  </div>
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
                      {/* Mock horizontal bar calculation based on progress/dates */}
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

      {/* Smart New Plan Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Create Treatment Plan
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Draft a new clinical pathway
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
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">
                    Select Patient
                  </label>
                  <select
                    value={modalData.patient}
                    onChange={(e) =>
                      setModalData({ ...modalData, patient: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900"
                  >
                    <option>John Doe (P001)</option>
                    <option>Jane Smith (P002)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">
                    Link Diagnosis
                  </label>
                  <select
                    value={modalData.diagnosis}
                    onChange={(e) =>
                      setModalData({ ...modalData, diagnosis: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900"
                  >
                    <option>Dental Caries (Class II) - Left Molar</option>
                  </select>
                </div>
              </div>

              {/* Smart AI Suggestions */}
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <h4 className="text-xs uppercase tracking-wider font-bold text-indigo-800 mb-3 flex items-center gap-2">
                  <Zap size={14} className="text-amber-500 fill-amber-500" /> AI
                  Recommended Approaches
                </h4>
                <div className="space-y-2">
                  <label className="flex items-center p-3 bg-white border border-indigo-100 rounded cursor-pointer hover:border-indigo-300">
                    <input
                      type="radio"
                      name="plan"
                      checked={
                        modalData.procedure === "Indirect Composite Inlay"
                      }
                      onChange={() =>
                        setModalData({
                          ...modalData,
                          procedure: "Indirect Composite Inlay",
                          cost: "350",
                        })
                      }
                      className="text-indigo-600 mr-3"
                    />
                    <div className="flex-1">
                      <span className="font-bold text-gray-900 block">
                        Indirect Composite Inlay
                      </span>
                      <span className="text-xs text-gray-500">
                        Conservative margin approach. Estimated $350.
                      </span>
                    </div>
                  </label>
                  <label className="flex items-center p-3 bg-white border border-gray-200 rounded cursor-pointer hover:border-indigo-300">
                    <input
                      type="radio"
                      name="plan"
                      checked={modalData.procedure === "Direct Composite Fill"}
                      onChange={() =>
                        setModalData({
                          ...modalData,
                          procedure: "Direct Composite Fill",
                          cost: "200",
                        })
                      }
                      className="text-indigo-600 mr-3"
                    />
                    <div className="flex-1">
                      <span className="font-bold text-gray-900 block">
                        Direct Composite Fill
                      </span>
                      <span className="text-xs text-gray-500">
                        Standard restorative. Estimated $200.
                      </span>
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Custom Procedure Description
                </label>
                <textarea
                  rows={3}
                  value={modalData.description}
                  onChange={(e) =>
                    setModalData({ ...modalData, description: e.target.value })
                  }
                  placeholder="Additional clinician notes..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 placeholder-gray-600"
                ></textarea>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2">
                    Expected Cost ($)
                  </label>
                  <div className="relative">
                    <DollarSign
                      size={16}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                      type="number"
                      value={modalData.cost}
                      onChange={(e) =>
                        setModalData({ ...modalData, cost: e.target.value })
                      }
                      className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900"
                    />
                  </div>
                </div>
                <div className="flex items-end pb-2">
                  <label className="flex items-center gap-2 cursor-pointer text-sm font-bold text-gray-700">
                    <input
                      type="checkbox"
                      checked={modalData.insured}
                      onChange={(e) =>
                        setModalData({
                          ...modalData,
                          insured: e.target.checked,
                        })
                      }
                      className="w-5 h-5 text-indigo-600 rounded"
                    />{" "}
                    Applies to Insurance
                  </label>
                </div>
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
                Initialize Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
