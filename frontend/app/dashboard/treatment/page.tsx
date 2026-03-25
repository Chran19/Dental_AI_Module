"use client";

import { useState, useEffect } from "react";
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
} from "lucide-react";

interface TreatmentPlan {
  id: string;
  patient_name: string;
  patient_id: string;
  procedure: string;
  status: "Planned" | "In Progress" | "Completed" | "Cancelled";
  start_date: string;
  end_date?: string;
  cost: number;
  progress: number;
  description: string;
}

export default function TreatmentPage() {
  const { isAuthenticated } = useAuth();
  const [plans, setPlans] = useState<TreatmentPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  // Mock data - Replace with actual API call
  useEffect(() => {
    if (isAuthenticated) {
      setTimeout(() => {
        setPlans([
          {
            id: "1",
            patient_name: "John Doe",
            patient_id: "P001",
            procedure: "Composite Filling",
            status: "In Progress",
            start_date: "2024-03-15",
            cost: 250,
            progress: 60,
            description: "Filling on tooth 16 and 26",
          },
          {
            id: "2",
            patient_name: "Jane Smith",
            patient_id: "P002",
            procedure: "Crown Placement",
            status: "Planned",
            start_date: "2024-04-01",
            cost: 800,
            progress: 0,
            description: "Full ceramic crown on tooth 11",
          },
          {
            id: "3",
            patient_name: "Mike Johnson",
            patient_id: "P003",
            procedure: "Root Canal Therapy",
            status: "Completed",
            start_date: "2024-02-10",
            end_date: "2024-03-10",
            cost: 600,
            progress: 100,
            description: "Complete RCT on tooth 36",
          },
        ]);
        setLoading(false);
      }, 500);
    }
  }, [isAuthenticated]);

  const filteredPlans = plans.filter((p) => {
    if (filter === "active")
      return ["Planned", "In Progress"].includes(p.status);
    if (filter === "completed") return p.status === "Completed";
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Planned":
        return "bg-slate-100 text-slate-700";
      case "In Progress":
        return "bg-blue-100 text-blue-700";
      case "Completed":
        return "bg-green-100 text-green-700";
      case "Cancelled":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Planned":
        return <Calendar className="text-slate-600" size={18} />;
      case "In Progress":
        return <Clock className="text-blue-600 animate-spin" size={18} />;
      case "Completed":
        return <CheckCircle className="text-green-600" size={18} />;
      case "Cancelled":
        return <AlertCircle className="text-red-600" size={18} />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Treatment Plans</h1>
          <p className="text-gray-600 mt-1">
            Manage patient treatment procedures
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          New Plan
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {(["all", "active", "completed"] as const).map((status) => (
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

      {/* Treatment Plans Grid */}
      <div className="grid gap-4">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="mt-3 text-gray-600">Loading treatment plans...</p>
          </div>
        ) : filteredPlans.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Pill className="mx-auto text-gray-400 mb-3" size={40} />
            <p className="text-gray-600">No treatment plans found</p>
          </div>
        ) : (
          filteredPlans.map((plan) => (
            <div
              key={plan.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                {/* Left Section */}
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="bg-purple-100 p-2 rounded-lg">
                      <Pill className="text-purple-600" size={20} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {plan.procedure}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {plan.patient_name}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {plan.description}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        Progress
                      </span>
                      <span className="text-sm font-semibold text-gray-900">
                        {plan.progress}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${plan.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Info Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User size={16} className="text-gray-400" />
                      <span>ID: {plan.patient_id}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar size={16} className="text-gray-400" />
                      <span>
                        {new Date(plan.start_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <DollarSign size={16} className="text-gray-400" />
                      <span>${plan.cost}</span>
                    </div>
                  </div>
                </div>

                {/* Right Section */}
                <div className="flex items-start gap-2">
                  <div
                    className={`px-3 py-2 rounded-lg font-medium text-sm flex items-center gap-2 ${getStatusColor(
                      plan.status,
                    )}`}
                  >
                    {getStatusIcon(plan.status)}
                    {plan.status}
                  </div>
                </div>
              </div>

              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium text-sm">
                View Details →
              </button>
            </div>
          ))
        )}
      </div>

      {/* New Plan Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              New Treatment Plan
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Patient
                </label>
                <input
                  type="text"
                  placeholder="Search patient..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Procedure
                </label>
                <input
                  type="text"
                  placeholder="Enter procedure name..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost
                </label>
                <input
                  type="number"
                  placeholder="Enter cost..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Create Plan
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
