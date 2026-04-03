"use client";

import { QueueItem } from "@/lib/types/queue";
import {
  Clock,
  User,
  ChevronRight,
  Stethoscope,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";

interface QueueBoardProps {
  items: QueueItem[];
  isLoading: boolean;
  onStatusChange?: (id: string, status: QueueItem["status"]) => void;
  role: "DOCTOR" | "RECEPTIONIST" | "ADMIN";
}

export default function QueueBoard({
  items,
  isLoading,
  onStatusChange,
  role,
}: QueueBoardProps) {
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
        <div className="mx-auto w-12 h-12 bg-slate-100 flex items-center justify-center rounded-full text-slate-400 mb-4">
          <Clock size={24} />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Queue is empty</h3>
        <p className="text-slate-700 font-medium">
          No patients are currently waiting for consultation.
        </p>
        <Link
          href="/dashboard/patients/new"
          className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors"
        >
          <User size={16} />
          Add Patient Intake
        </Link>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "EMERGENCY":
        return "bg-red-100 text-red-700 border-red-200";
      case "URGENT":
        return "bg-orange-100 text-orange-700 border-orange-200";
      default:
        return "bg-blue-100 text-blue-700 border-blue-200";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Waiting":
        return "bg-yellow-100 text-yellow-700";
      case "In_Consultation":
        return "bg-green-100 text-green-700";
      default:
        return "bg-slate-100 text-slate-600";
    }
  };

  const formatStatus = (status: string) => {
    return status.replace(/_/g, " ");
  };

  return (
    <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
      {items.map((item) => (
        <div
          key={item.id}
          className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:border-blue-300 transition-all"
        >
          {/* Patient Info Row */}
          <div className="flex items-center gap-4 mb-4">
            <div
              className={`w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center font-bold text-lg ${
                item.status === "In_Consultation"
                  ? "bg-green-600 text-white animate-pulse"
                  : "bg-slate-100 text-slate-600"
              }`}
            >
              {item.patient_name?.charAt(0) || "?"}
            </div>

            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <h4 className="font-bold text-slate-900">
                  {item.patient_name}
                </h4>
                {item.patient_id && (
                  <span className="text-gray-500 text-xs font-normal uppercase bg-slate-100 px-2 py-0.5 rounded-md">
                    ID: {item.patient_id.substring(0, 8)}
                  </span>
                )}
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full border font-bold ${getPriorityColor(item.priority)}`}
                >
                  {item.priority}
                </span>
                {item.priority === "EMERGENCY" && (
                  <div className="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse" />
                )}
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <div className="flex items-center gap-1.5 text-slate-500 font-medium bg-slate-50 px-2 py-1 rounded border border-slate-100">
                  <Clock size={12} className="text-blue-500" />
                  <span>
                    Checked in:{" "}
                    {item.check_in_time
                      ? new Date(item.check_in_time).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "N/A"}
                  </span>
                </div>
                <div
                  className={`px-2 py-1 rounded font-bold uppercase tracking-wider border ${getStatusBadge(item.status)}`}
                >
                  {formatStatus(item.status)}
                </div>
                {item.status === "Waiting" && item.check_in_time && (
                  <div className="text-slate-500 font-medium">
                    Wait time:{" "}
                    {Math.floor(
                      (Date.now() - new Date(item.check_in_time).getTime()) /
                        60000,
                    )}
                    m
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Notes if present */}
          {item.notes && (
            <p className="text-xs text-purple-600 font-medium mb-4 bg-purple-50 px-3 py-2 rounded border border-purple-100">
              📝 {item.notes}
            </p>
          )}

          {/* Action Buttons Row */}
          <div className="flex flex-wrap gap-3 justify-end">
            {role === "DOCTOR" && item.status === "Waiting" && (
              <button
                onClick={() => onStatusChange?.(item.id, "In_Consultation")}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-lg transition-all whitespace-nowrap"
              >
                <Stethoscope size={16} />
                Call Patient
              </button>
            )}

            {item.status === "In_Consultation" && role === "DOCTOR" && (
              <button
                onClick={() => onStatusChange?.(item.id, "Completed")}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-bold rounded-lg transition-all whitespace-nowrap"
              >
                <CheckCircle2 size={16} />
                End Consultation
              </button>
            )}

            {item.status === "In_Consultation" ? (
              <Link
                href={`/dashboard/patients/${item.patient_id}`}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-lg transition-all whitespace-nowrap"
              >
                Go to Visit
                <ChevronRight size={16} />
              </Link>
            ) : (
              <Link
                href={`/dashboard/patients/${item.patient_id}`}
                className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
                title="View Record"
              >
                <User size={18} />
              </Link>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
