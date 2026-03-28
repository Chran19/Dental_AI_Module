"use client";

import { useAuth } from "@/app/providers";
import { useState, useEffect } from "react";
import {
  Calendar,
  Users,
  Stethoscope,
  TrendingUp,
  Clock,
  AlertCircle,
  Activity,
  CheckCircle,
  FileText,
  ChevronRight,
  ClipboardList
} from "lucide-react";
import Link from "next/link";

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Simulate API fetch for real-time data
    const fetchDashboardData = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network
      setData({
        stats: {
          todayConsultations: 7,
          pendingDiagnoses: 3,
          activePlans: 15,
          completedThisMonth: 42
        },
        alerts: [
          { type: 'urgent', message: '1 diagnosis awaiting confirmation', details: 'Patient: John Smith - Periapical lesion detected' },
          { type: 'warning', message: '2 overdue follow-ups', details: 'Patients: Sarah Johnson, Mike Brown' }
        ],
        schedule: [
          { time: "09:00 AM", patient: "John Doe", issue: "Root Canal - Tooth 36", status: "Upcoming" },
          { time: "10:30 AM", patient: "Jane Smith", issue: "Crown Placement - Tooth 11", status: "In Progress" },
          { time: "01:00 PM", patient: "Mike Johnson", issue: "Filling - Tooth 16", status: "Scheduled" },
          { time: "02:30 PM", patient: "Sarah Wilson", issue: "Oral Exam", status: "Scheduled" }
        ],
        recentCases: [
          { patient: "Alice Brown", diagnosis: "Dental Caries", date: "2024-03-20", status: "Completed" },
          { patient: "Bob Davis", diagnosis: "Gingivitis", date: "2024-03-19", status: "Completed" },
          { patient: "Carol White", diagnosis: "Root Canal", date: "2024-03-18", status: "In Treatment" }
        ]
      });
      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  const SkeletonCard = () => (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm animate-pulse">
      <div className="flex justify-between">
        <div className="space-y-3 flex-1">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/3"></div>
        </div>
        <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      
      {/* Welcome Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Stethoscope className="text-indigo-600" /> Dr. {user?.email?.split("@")[0] || "Provider"}
            </h1>
            <p className="text-gray-600 mt-1 font-medium">
              Manage clinical pipeline, diagnostics, and patient care.
            </p>
          </div>
          
          <div className="flex items-center gap-4 bg-gray-50 border border-gray-200 px-4 py-2 rounded-lg">
             <div className="w-2 h-2 rounded-full bg-green-500"></div>
             <span className="text-sm font-bold text-gray-700">Online & Active</span>
             <span className="text-xs text-gray-400">|</span>
             <span className="text-sm font-bold text-gray-500">Next Break: 12:30 PM</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 space-y-6">
        
        {/* Alerts & Quick Actions Bar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           
           {/* Alerts */}
           <div className="lg:col-span-2 space-y-3">
             {loading ? (
               <div className="h-24 bg-gray-200 animate-pulse rounded-xl border border-gray-100"></div>
             ) : data?.alerts.map((alert: any, idx: number) => (
                <div key={idx} className={`rounded-xl border p-4 flex items-center gap-4 shadow-sm ${alert.type === 'urgent' ? 'bg-red-50 border-red-200' : 'bg-amber-50 border-amber-200'}`}>
                  <div className={`p-2 rounded-full ${alert.type === 'urgent' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
                    <AlertCircle size={24} />
                  </div>
                  <div className="flex-1">
                    <p className={`font-bold ${alert.type === 'urgent' ? 'text-red-900' : 'text-amber-900'}`}>
                      {alert.message}
                    </p>
                    <p className={`text-sm mt-0.5 ${alert.type === 'urgent' ? 'text-red-700' : 'text-amber-700'}`}>
                      {alert.details}
                    </p>
                  </div>
                  <button className={`px-4 py-2 rounded-lg text-sm font-bold border transition shadow-sm ${alert.type === 'urgent' ? 'bg-red-600 border-red-700 text-white hover:bg-red-700' : 'bg-white border-amber-300 text-amber-800 hover:bg-amber-100'}`}>
                    {alert.type === 'urgent' ? 'Review Now' : 'Schedule'}
                  </button>
                </div>
             ))}
           </div>

           {/* Quick Link Buttons Layout */}
           <div className="grid grid-cols-2 gap-3">
              <Link href="/dashboard/clinical" className="flex flex-col items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-xl hover:border-indigo-400 hover:shadow-md transition group text-indigo-700">
                 <FileText size={28} className="text-indigo-500 group-hover:scale-110 transition-transform" />
                 <span className="text-sm font-bold text-gray-800">New Clinical Note</span>
              </Link>
              <Link href="/dashboard/upload" className="flex flex-col items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-400 hover:shadow-md transition group text-blue-700">
                 <Activity size={28} className="text-blue-500 group-hover:scale-110 transition-transform" />
                 <span className="text-sm font-bold text-gray-800">Analyze Scan</span>
              </Link>
              <Link href="/dashboard/diagnosis" className="flex flex-col items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-xl hover:border-purple-400 hover:shadow-md transition group text-purple-700">
                 <ClipboardList size={28} className="text-purple-500 group-hover:scale-110 transition-transform" />
                 <span className="text-sm font-bold text-gray-800">Diagnoses</span>
              </Link>
              <Link href="/dashboard/treatment" className="flex flex-col items-center justify-center gap-2 p-4 bg-white border border-gray-200 rounded-xl hover:border-green-400 hover:shadow-md transition group text-green-700">
                 <CheckCircle size={28} className="text-green-500 group-hover:scale-110 transition-transform" />
                 <span className="text-sm font-bold text-gray-800">Treatments</span>
              </Link>
           </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            <>
              <SkeletonCard /><SkeletonCard /><SkeletonCard /><SkeletonCard />
            </>
          ) : (
            <>
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm flex flex-col justify-between">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Today's Load</p>
                    <p className="text-3xl font-black text-gray-900 mt-2">{data.stats.todayConsultations}</p>
                    <p className="text-xs text-green-600 font-bold mt-2 flex items-center gap-1"><TrendingUp size={12} /> 2 vs Yesterday</p>
                  </div>
                  <div className="bg-blue-50 text-blue-600 p-3 rounded-xl border border-blue-100">
                    <Users size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm flex flex-col justify-between">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Awaiting Confirmation</p>
                    <p className="text-3xl font-black text-amber-600 mt-2">{data.stats.pendingDiagnoses}</p>
                    <p className="text-xs text-amber-700 font-bold mt-2 flex items-center gap-1">Action Required</p>
                  </div>
                  <div className="bg-amber-50 text-amber-600 p-3 rounded-xl border border-amber-100">
                    <AlertCircle size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm flex flex-col justify-between">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Active Treatments</p>
                    <p className="text-3xl font-black text-purple-700 mt-2">{data.stats.activePlans}</p>
                    <p className="text-xs text-purple-600 font-bold mt-2 flex items-center gap-1">In progress</p>
                  </div>
                  <div className="bg-purple-50 text-purple-600 p-3 rounded-xl border border-purple-100">
                    <Activity size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm flex flex-col justify-between">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Cases Completed</p>
                    <p className="text-3xl font-black text-green-700 mt-2">{data.stats.completedThisMonth}</p>
                    <p className="text-xs text-green-600 font-bold mt-2 flex items-center gap-1">This Month</p>
                  </div>
                  <div className="bg-green-50 text-green-600 p-3 rounded-xl border border-green-100">
                    <CheckCircle size={24} />
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Schedule & Recent Column Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
           
           {/* Left: Schedule Today */}
           <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                 <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <Calendar size={18} className="text-indigo-600" /> Daily Schedule
                 </h2>
                 <Link href="#" className="text-sm font-bold text-indigo-600 flex items-center hover:underline">Full View <ChevronRight size={16} /></Link>
              </div>
              <div className="p-5 flex-1 space-y-3">
                 {loading ? (
                    <div className="space-y-4 pt-2">
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                    </div>
                 ) : (
                    data.schedule.map((slot: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl hover:border-indigo-300 transition-colors shadow-sm group">
                        <div className="flex gap-4 items-center">
                           <div className="text-right w-16 border-r pr-4 border-gray-200">
                             <p className="text-sm font-black text-gray-900">{slot.time.split(' ')[0]}</p>
                             <p className="text-[10px] font-bold text-gray-500 uppercase">{slot.time.split(' ')[1]}</p>
                           </div>
                           <div>
                             <p className="font-bold text-gray-900 text-sm group-hover:text-indigo-700 transition">{slot.patient}</p>
                             <p className="text-xs text-gray-500 mt-0.5 font-medium">{slot.issue}</p>
                           </div>
                        </div>
                        <div>
                          <span className={`inline-flex items-center px-3 py-1 bg-white border rounded text-[10px] uppercase font-bold tracking-wider ${
                             slot.status === 'In Progress' ? 'border-blue-200 text-blue-700 bg-blue-50' :
                             slot.status === 'Upcoming' ? 'border-amber-200 text-amber-700 bg-amber-50' : 'border-gray-200 text-gray-600 bg-gray-50'
                          }`}>
                            {slot.status === 'In Progress' && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse mr-1.5 "></span>}
                            {slot.status}
                          </span>
                        </div>
                      </div>
                    ))
                 )}
              </div>
           </div>

           {/* Right: Recent Cases */}
           <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                 <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <ClipboardList size={18} className="text-green-600" /> Recent Cases
                 </h2>
                 <Link href="/dashboard/diagnosis" className="text-sm font-bold text-indigo-600 flex items-center hover:underline">View All <ChevronRight size={16} /></Link>
              </div>
              <div className="p-5 flex-1 space-y-3">
                 {loading ? (
                    <div className="space-y-4 pt-2">
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                      <div className="h-12 bg-gray-100 rounded-lg animate-pulse"></div>
                    </div>
                 ) : (
                    data.recentCases.map((case_: any, idx: number) => (
                      <div key={idx} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-white border border-gray-200 rounded-xl hover:border-green-300 transition-colors shadow-sm">
                        <div>
                           <div className="flex items-center gap-2">
                             <p className="font-bold text-gray-900 text-sm">{case_.patient}</p>
                             <span className="text-xs font-bold text-gray-400">•</span>
                             <p className="text-xs text-gray-500 font-medium">{new Date(case_.date).toLocaleDateString()}</p>
                           </div>
                           <p className="text-xs text-gray-600 mt-1 font-medium bg-gray-50 inline-block px-2 py-0.5 rounded border border-gray-100">Diag: {case_.diagnosis}</p>
                        </div>
                        <div className="mt-2 sm:mt-0 items-end">
                           <span className={`inline-flex items-center px-3 py-1 bg-white border rounded text-[10px] uppercase font-bold tracking-wider ${
                             case_.status === 'Completed' ? 'border-green-200 text-green-700 bg-green-50' : 'border-indigo-200 text-indigo-700 bg-indigo-50'
                           }`}>
                             {case_.status}
                           </span>
                        </div>
                      </div>
                    ))
                 )}
              </div>
           </div>

        </div>
      </div>
    </div>
  );
}
