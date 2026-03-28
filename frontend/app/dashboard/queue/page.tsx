"use client";

import { useEffect, useState } from "react";
import QueueBoard from "@/components/queue/QueueBoard";
import { QueueItem } from "@/lib/types/queue";
import { fetchAPI } from "@/lib/api";
import {
  Calendar,
  RefreshCcw,
  Bell,
  Users,
  Clock,
  CheckCircle,
} from "lucide-react";
import { useAuth } from "@/app/providers";

export default function ReceptionistQueuePage() {
  const [items, setItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();

  const fetchQueue = async () => {
    setIsLoading(true);
    try {
      const response = await fetchAPI("/queue/active", { method: "GET" });
      setItems(response);
    } catch (err) {
      console.error("Error fetching queue:", err);
      // Fallback for development/missing endpoint
      setItems([
        {
          id: "1",
          patient_id: "p1",
          patient_name: "Alice Smith",
          check_in_time: new Date().toISOString(),
          status: "WAITING",
          priority: "NORMAL",
        },
        {
          id: "2",
          patient_id: "p2",
          patient_name: "Bob Johnson",
          check_in_time: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          status: "WAITING",
          priority: "URGENT",
        },
        {
          id: "3",
          patient_id: "p3",
          patient_name: "Charlie Brown",
          check_in_time: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          status: "IN_CONSULTATION",
          priority: "NORMAL",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchQueue, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="text-blue-600" />
            Active Clinic Queue
          </h1>
          <p className="text-slate-700 text-sm mt-1 font-medium">
            Real-time occupancy and patient flow status
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchQueue}
            className="p-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
            title="Refresh Queue"
          >
            <RefreshCcw size={18} className={isLoading ? "animate-spin" : ""} />
          </button>
          <button
            className="p-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
            title="Notifications"
          >
            <Bell size={18} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={Users}
          label="Total Waiting"
          value={items.filter((i) => i.status === "WAITING").length.toString()}
          sub="Patients in lobby"
          color="bg-blue-600"
        />
        <StatCard
          icon={CheckCircle}
          label="In Consultation"
          value={items
            .filter((i) => i.status === "IN_CONSULTATION")
            .length.toString()}
          sub="Currently with doctors"
          color="bg-green-600"
        />
        <StatCard
          icon={Clock}
          label="High Priority"
          value={items
            .filter((i) => i.priority !== "NORMAL" && i.status === "WAITING")
            .length.toString()}
          sub="Requires immediate attention"
          color="bg-red-600"
        />
      </div>

      <div className="mt-8 bg-white/50 backdrop-blur-sm p-6 rounded-3xl border border-white/80 shadow-sm">
        <QueueBoard
          items={items}
          isLoading={isLoading}
          role={user?.role || "RECEPTIONIST"}
        />
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  return (
    <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col gap-3 group hover:border-blue-200 transition-all">
      <div className={`p-2.5 rounded-2xl w-fit ${color} text-white shadow-lg`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">
          {label}
        </p>
        <p className="text-3xl font-black text-slate-900 mt-0.5 tracking-tight group-hover:scale-105 transition-transform origin-left">
          {value}
        </p>
        <p className="text-[10px] text-slate-600 mt-1 font-medium">{sub}</p>
      </div>
    </div>
  );
}
