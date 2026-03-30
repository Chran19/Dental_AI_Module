"use client";

import { useAuth } from "@/app/providers";
import { useState, useEffect, useCallback } from "react";
import {
  Clock,
  Users,
  Phone,
  CheckCircle,
  DollarSign,
  UserPlus,
  CreditCard,
  ClipboardCheck,
  Building,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { getDashboardStats, fetchQueue, getRecentActivity } from "@/lib/store";
import type { QueueItem } from "@/lib/types/queue";
import type { ActivityEntry } from "@/lib/store";
import Link from "next/link";

export default function ReceptionistDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    checkedIn: 0,
    inQueue: 0,
    newPatients: 0,
    totalPatients: 0,
  });
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [dashStats, queueData] = await Promise.all([
        getDashboardStats(),
        fetchQueue(),
      ]);
      setStats(dashStats);
      setQueue(queueData);
      setActivity(getRecentActivity(8));
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 20000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleCallNext = () => {
    const waitingIdx = queue.findIndex((q) => q.status === "Waiting");
    if (waitingIdx > -1) {
      const updatedQueue = [...queue];
      updatedQueue[waitingIdx] = {
        ...updatedQueue[waitingIdx],
        status: "In_Consultation",
      };
      setQueue(updatedQueue);
    }
  };

  const SkeletonBlock = () => (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm animate-pulse">
      <div className="flex justify-between">
        <div className="space-y-3 flex-1">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        </div>
        <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Building className="text-emerald-600" /> Front Desk Operations
            </h1>
            <p className="text-gray-600 mt-1 font-medium">
              Welcome back,{" "}
              {user?.email?.split("@")[0] || "Admin"}. Manage queue
              and logistics.
            </p>
          </div>

          <div className="flex gap-2">
            <Link
              href="/dashboard/patients/new"
              className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold shadow-sm hover:bg-emerald-700 transition"
            >
              <UserPlus size={16} /> Patient Intake
            </Link>
            <button
              onClick={() => setShowPaymentModal(true)}
              className="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-bold shadow-sm hover:bg-gray-50 transition"
            >
              <CreditCard size={16} /> Bill Patient
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            <>
              <SkeletonBlock />
              <SkeletonBlock />
              <SkeletonBlock />
              <SkeletonBlock />
            </>
          ) : (
            <>
              <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">
                      Checked In
                    </p>
                    <p className="text-3xl font-black text-emerald-700 mt-1">
                      {stats.checkedIn}
                    </p>
                  </div>
                  <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                    <CheckCircle size={20} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">
                      In Queue
                    </p>
                    <p className="text-3xl font-black text-blue-700 mt-1">
                      {stats.inQueue}
                    </p>
                  </div>
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                    <Clock size={20} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">
                      New Today
                    </p>
                    <p className="text-3xl font-black text-purple-700 mt-1">
                      {stats.newPatients}
                    </p>
                  </div>
                  <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
                    <Users size={20} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">
                      Total Patients
                    </p>
                    <p className="text-3xl font-black text-orange-600 mt-1">
                      {stats.totalPatients}
                    </p>
                  </div>
                  <div className="p-2 bg-orange-50 text-orange-600 rounded-lg">
                    <ClipboardCheck size={20} />
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interactive Queue Board */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
            <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Users size={18} className="text-blue-600" /> Active Queue Board
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={handleCallNext}
                  className="text-sm px-3 py-1.5 bg-blue-600 text-white font-bold rounded shadow-sm hover:bg-blue-700 transition"
                >
                  Call Next Ready
                </button>
                <Link
                  href="/dashboard/queue"
                  className="text-sm px-3 py-1.5 bg-white border border-gray-300 text-gray-700 font-bold rounded shadow-sm hover:bg-gray-50 transition"
                >
                  Full View
                </Link>
              </div>
            </div>
            <div className="p-0">
              <table className="w-full text-left">
                <thead className="bg-white border-b border-gray-100 text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                  <tr>
                    <th className="p-4 w-12 text-center">#</th>
                    <th className="p-4">Patient</th>
                    <th className="p-4 hidden sm:table-cell">Visit Reason</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {loading ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="p-8 text-center text-gray-500 font-medium"
                      >
                        Loading Queue...
                      </td>
                    </tr>
                  ) : queue.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="p-8 text-center text-gray-400 font-medium"
                      >
                        Queue is empty. Use{" "}
                        <Link
                          href="/dashboard/patients/new"
                          className="text-blue-600 font-bold hover:underline"
                        >
                          Patient Intake
                        </Link>{" "}
                        to add patients.
                      </td>
                    </tr>
                  ) : (
                    queue.map((item, idx) => (
                      <tr
                        key={item.id}
                        className={`border-b border-gray-50 last:border-0 hover:bg-gray-50 transition ${item.status === "In_Consultation" ? "bg-indigo-50/30" : ""}`}
                      >
                        <td className="p-4 text-center font-black text-gray-900">
                          {idx + 1}
                        </td>
                        <td className="p-4">
                          <Link
                            href={`/dashboard/patients/${item.patient_id}`}
                            className="font-bold text-gray-900 hover:text-blue-600 transition-colors"
                          >
                            {item.patient_name}
                          </Link>
                        </td>
                        <td className="p-4 hidden sm:table-cell text-gray-600 font-medium text-xs">
                          {item.notes || "—"}
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span
                              className={`inline-block w-2 h-2 rounded-full ${item.status === "In_Consultation" ? "bg-indigo-500 animate-pulse" : "bg-amber-400"}`}
                            ></span>
                            <span
                              className={`font-bold text-xs uppercase tracking-wider ${item.status === "In_Consultation" ? "text-indigo-700" : "text-amber-700"}`}
                            >
                              {item.status.replace(/_/g, " ")}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <Link
                            href={`/dashboard/patients/${item.patient_id}`}
                            className="text-xs font-bold text-blue-600 border border-blue-200 bg-blue-50 px-3 py-1.5 rounded hover:bg-blue-100 transition"
                          >
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Activity Feed */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
              <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                <h2 className="text-[15px] font-bold text-gray-900 flex items-center gap-2">
                  <Clock size={16} className="text-gray-600" /> Recent Activity
                </h2>
              </div>
              <div className="p-4">
                {loading ? (
                  <div className="h-32 bg-gray-100 rounded animate-pulse"></div>
                ) : activity.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-6">
                    No recent activity. Actions will appear here.
                  </p>
                ) : (
                  <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-300 before:to-transparent">
                    {activity.map((act, idx) => (
                      <div key={idx} className="relative flex items-start">
                        <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-white border-4 border-gray-200"></div>
                        <div className="ml-8 pr-4">
                          <p className="text-[10px] font-bold text-gray-500">
                            {act.time}
                          </p>
                          <p className="text-sm font-bold text-gray-900 mt-0.5">
                            {act.action}
                          </p>
                          <p className="text-xs text-gray-600 font-medium">
                            {act.subject}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {showPaymentModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h2 className="text-xl font-bold text-gray-900">
                Process Payment
              </h2>
              <button
                onClick={() => setShowPaymentModal(false)}
                className="text-gray-500 hover:text-gray-900 font-bold text-xl"
              >
                &times;
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Patient Name
                </label>
                <input
                  type="text"
                  placeholder="Search patient..."
                  className="w-full border border-gray-300 rounded p-2 focus:ring-2 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Amount
                </label>
                <input
                  type="number"
                  placeholder="0.00"
                  className="w-full border border-gray-300 rounded p-2 focus:ring-2 outline-none"
                />
              </div>
              <button
                onClick={() => setShowPaymentModal(false)}
                className="w-full bg-emerald-600 text-white font-bold py-3 pt-3 mt-4 rounded hover:bg-emerald-700 transition"
              >
                Process Charge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
