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
  const [filteredItems, setFilteredItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPriority, setFilterPriority] = useState("all");
  const { user } = useAuth();

  const checkAlerts = (currentItems: QueueItem[]) => {
    const alerts: any[] = [];
    currentItems.forEach((item) => {
      if (item.status === "WAITING") {
        const waitMinutes = Math.floor(
          (Date.now() - new Date(item.check_in_time).getTime()) / 60000
        );
        if (waitMinutes > 30) {
          alerts.push({
            id: item.id,
            message: `${item.patient_name} waiting ${waitMinutes}m+`,
          });
        }
      }
    });
    setNotifications(alerts);
  };

  const fetchQueue = async () => {
    setIsLoading(true);
    try {
      const response = await fetchAPI("/queue/active", { method: "GET" });
      setItems(response);
      checkAlerts(response);
    } catch (err) {
      console.error("Error fetching queue:", err);
      // Fallback for development/missing endpoint
      const mockItems = [
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
          check_in_time: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
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
      ];
      setItems(mockItems as any[]);
      checkAlerts(mockItems as any[]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: QueueItem["status"]) => {
    // Optimistic update
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: newStatus } : item))
    );
    try {
      await fetchAPI(`/queue/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
    } catch (err) {
      console.error("Status update failed:", err);
      fetchQueue(); // Revert on error
    }
  };

  useEffect(() => {
    let result = [...items];

    // Priority sorting
    result.sort((a, b) => {
      const priorityOrder: Record<string, number> = { EMERGENCY: 0, URGENT: 1, NORMAL: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });

    // Filtering
    if (searchQuery) {
      result = result.filter(
        (i) =>
          i.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          i.patient_id.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    if (filterPriority !== "all") {
      result = result.filter((i) => i.priority === filterPriority);
    }

    setFilteredItems(result);
  }, [items, searchQuery, filterPriority]);

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(() => {
        fetchQueue();
    }, 30000);
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
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors relative"
              title="Notifications"
            >
              <Bell size={18} />
              <span className="absolute top-1 right-1 bg-red-600 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center font-bold">
                {notifications.length}
              </span>
            </button>
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-72 bg-white border border-slate-200 shadow-lg rounded-xl overflow-hidden z-50">
                <div className="p-3 border-b border-slate-100 bg-slate-50 font-bold text-slate-800 text-sm">Alerts & Notifications</div>
                {notifications.length === 0 ? (
                   <div className="p-4 text-xs text-slate-500 text-center font-medium">No active alerts. Queue is running smoothly.</div>
                ) : (
                   notifications.map((n, i) => (
                      <div key={i} className="p-3 border-b border-slate-50 text-xs text-slate-700 hover:bg-red-50 font-bold text-red-700">⚠️ {n.message}</div>
                   ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={Users}
          label="Total Waiting"
          value={items.filter((i) => i.status === "WAITING").length.toString()}
          sub={`~${items.filter((i) => i.status === "WAITING").length * 20} min est wait time`}
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

      <div className="flex flex-col sm:flex-row gap-4 mt-6">
        <input
          type="text"
          placeholder="Search patient name or ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-medium text-sm text-slate-900"
        />
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg font-medium text-sm text-slate-900 bg-white"
        >
          <option value="all">All Priorities</option>
          <option value="NORMAL">Normal</option>
          <option value="URGENT">Urgent</option>
          <option value="EMERGENCY">Emergency</option>
        </select>
      </div>

      <div className="mt-6 bg-white/50 backdrop-blur-sm p-6 rounded-3xl border border-white/80 shadow-sm">
        <QueueBoard
          items={filteredItems}
          isLoading={isLoading}
          onStatusChange={handleStatusChange}
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
