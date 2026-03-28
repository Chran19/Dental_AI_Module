"use client";

import { useAuth } from "@/app/providers";
import { useState, useEffect } from "react";
import {
  Clock,
  Users,
  Phone,
  CheckCircle,
  AlertCircle,
  DollarSign,
  CalendarDays,
  UserPlus,
  CreditCard,
  ChevronRight,
  ClipboardCheck,
  Building
} from "lucide-react";
import { useRouter } from "next/navigation";

export default function ReceptionistDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  const handleCallNext = () => {
    if (data && data.queue) {
       const newQueue = [...data.queue];
       const waitingIdx = newQueue.findIndex((q: any) => q.status === "Waiting");
       if (waitingIdx > -1) {
          newQueue[waitingIdx].status = "In Consultation";
          setData({ ...data, queue: newQueue });
       }
    }
  };

  useEffect(() => {
    // Simulate API fetch
    const fetchData = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      setData({
        stats: { checkedIn: 12, inQueue: 5, newPatients: 8, pendingPayments: 1250 },
        alerts: [
          { type: 'payment', message: 'Pending payments highlight', details: '$1,250 due today - 4 invoices require immediate action' },
          { type: 'registration', message: '3 new patient registrations', details: 'Initial intake forms submitted - awaiting manual verification' }
        ],
        queue: [
          { position: 1, patient: "John Doe", doctor: "Dr. Smith", waitTime: "15 min", status: "Waiting" },
          { position: 2, patient: "Jane Smith", doctor: "Dr. Johnson", waitTime: "--", status: "In Consultation" },
          { position: 3, patient: "Mike Brown", doctor: "Dr. Smith", waitTime: "8 min", status: "Waiting" },
          { position: 4, patient: "Sarah Wilson", doctor: "Dr. Brown", waitTime: "3 min", status: "Waiting" },
        ],
        payments: [
          { invoice: "INV-001", patient: "Alice Brown", amount: 450, status: "Due Today" },
          { invoice: "INV-002", patient: "Tom Anderson", amount: 300, status: "Due Tomorrow" },
          { invoice: "INV-003", patient: "Emily White", amount: 500, status: "Overdue" }
        ],
        activity: [
          { time: "10:45 AM", action: "Patient checked in", subject: "John Doe" },
          { time: "10:30 AM", action: "Payment received", subject: "$150 from Mark V." },
          { time: "10:15 AM", action: "New registration", subject: "Emily White" },
          { time: "10:00 AM", action: "Consultation started", subject: "Sarah J. with Dr. Smith" }
        ]
      });
      setLoading(false);
    };
    fetchData();
  }, []);

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
               Welcome back, {user?.email?.split("@")[0] || "Admin"}. Manage queue and logistics.
             </p>
           </div>
           
           <div className="flex gap-2">
              <button onClick={() => router.push('/dashboard/patients')} className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold shadow-sm hover:bg-emerald-700 transition">
                <UserPlus size={16} /> New Patient
              </button>
              <button onClick={() => setShowPaymentModal(true)} className="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-bold shadow-sm hover:bg-gray-50 transition">
                <CreditCard size={16} /> Bill Patient
              </button>
           </div>
         </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 space-y-6">
         
         {/* Alerts Row */}
         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             {loading ? (
               <><div className="h-20 bg-gray-200 rounded-xl animate-pulse"></div><div className="h-20 bg-gray-200 rounded-xl animate-pulse"></div></>
             ) : data?.alerts.map((alert: any, idx: number) => (
                <div key={idx} className={`p-4 rounded-xl border flex items-start gap-4 shadow-sm ${alert.type === 'payment' ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-200'}`}>
                   <div className={`p-2 rounded-lg ${alert.type === 'payment' ? 'bg-orange-100 text-orange-600' : 'bg-blue-100 text-blue-600'}`}>
                      {alert.type === 'payment' ? <DollarSign size={24} /> : <ClipboardCheck size={24} />}
                   </div>
                   <div>
                      <h4 className={`text-sm font-bold uppercase tracking-wider ${alert.type === 'payment' ? 'text-orange-900' : 'text-blue-900'}`}>{alert.message}</h4>
                      <p className={`text-sm mt-0.5 font-medium ${alert.type === 'payment' ? 'text-orange-700' : 'text-blue-700'}`}>{alert.details}</p>
                   </div>
                </div>
             ))}
         </div>

         {/* Stats */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {loading ? (
              <><SkeletonBlock /><SkeletonBlock /><SkeletonBlock /><SkeletonBlock /></>
            ) : (
              <>
                 <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                   <div className="flex justify-between items-start">
                      <div>
                        <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Checked In</p>
                        <p className="text-3xl font-black text-emerald-700 mt-1">{data.stats.checkedIn}</p>
                      </div>
                      <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><CheckCircle size={20} /></div>
                   </div>
                 </div>

                 <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                   <div className="flex justify-between items-start">
                      <div>
                        <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">In Queue</p>
                        <p className="text-3xl font-black text-blue-700 mt-1">{data.stats.inQueue}</p>
                      </div>
                      <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Clock size={20} /></div>
                   </div>
                 </div>

                 <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                   <div className="flex justify-between items-start">
                      <div>
                        <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">New Patients</p>
                        <p className="text-3xl font-black text-purple-700 mt-1">{data.stats.newPatients}</p>
                      </div>
                      <div className="p-2 bg-purple-50 text-purple-600 rounded-lg"><Users size={20} /></div>
                   </div>
                 </div>

                 <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                   <div className="flex justify-between items-start">
                      <div>
                        <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">Receivables</p>
                        <p className="text-3xl font-black text-orange-600 mt-1">${data.stats.pendingPayments}</p>
                      </div>
                      <div className="p-2 bg-orange-50 text-orange-600 rounded-lg"><DollarSign size={20} /></div>
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
                 <button onClick={handleCallNext} className="text-sm px-3 py-1.5 bg-blue-600 text-white font-bold rounded shadow-sm hover:bg-blue-700 transition">Call Next Ready</button>
               </div>
               <div className="p-0">
                  <table className="w-full text-left">
                     <thead className="bg-white border-b border-gray-100 text-[10px] uppercase font-bold text-gray-400 tracking-wider">
                       <tr>
                         <th className="p-4 w-12 text-center">#</th>
                         <th className="p-4">Patient</th>
                         <th className="p-4 hidden sm:table-cell">Provider</th>
                         <th className="p-4">Status & Wait</th>
                         <th className="p-4 text-right">Action</th>
                       </tr>
                     </thead>
                     <tbody className="text-sm">
                       {loading ? (
                          <tr><td colSpan={5} className="p-8 text-center text-gray-500 font-medium">Loading Queue...</td></tr>
                       ) : data.queue.map((item: any, idx: number) => (
                          <tr key={idx} className={`border-b border-gray-50 last:border-0 hover:bg-gray-50 transition ${item.status === 'In Consultation' ? 'bg-indigo-50/30' : ''}`}>
                             <td className="p-4 text-center font-black text-gray-900">{item.position}</td>
                             <td className="p-4 font-bold text-gray-900">{item.patient}</td>
                             <td className="p-4 hidden sm:table-cell text-gray-600 font-medium">{item.doctor}</td>
                             <td className="p-4">
                                <div className="flex items-center gap-2">
                                   <span className={`inline-block w-2 h-2 rounded-full ${item.status === 'In Consultation' ? 'bg-indigo-500 animate-pulse' : 'bg-amber-400'}`}></span>
                                   <span className={`font-bold text-xs uppercase tracking-wider ${item.status === 'In Consultation' ? 'text-indigo-700' : 'text-amber-700'}`}>{item.status}</span>
                                   {item.status === 'Waiting' && <span className="text-xs text-gray-500 ml-1">({item.waitTime})</span>}
                                </div>
                             </td>
                             <td className="p-4 text-right">
                                {item.status === 'Waiting' ? (
                                   <button className="text-xs font-bold text-blue-600 border border-blue-200 bg-blue-50 px-3 py-1.5 rounded hover:bg-blue-100 transition">Call In</button>
                                ) : (
                                   <span className="text-xs text-gray-400 font-bold uppercase">Busy</span>
                                )}
                             </td>
                          </tr>
                       ))}
                     </tbody>
                  </table>
               </div>
            </div>

            {/* Smart Payment Widget & Activity side panel */}
            <div className="space-y-6">
               
               {/* Pre-Billing/Payments */}
               <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
                  <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                    <h2 className="text-[15px] font-bold text-gray-900 flex items-center gap-2">
                       <DollarSign size={16} className="text-orange-600" /> Payment Collection
                    </h2>
                  </div>
                  <div className="p-4">
                     {loading ? (
                        <div className="h-40 bg-gray-100 rounded animate-pulse"></div>
                     ) : (
                        <div className="space-y-3">
                           {data.payments.map((pmt: any, idx: number) => (
                              <div key={idx} className="flex justify-between items-center border border-gray-100 bg-white p-3 rounded-xl hover:border-orange-300 transition shadow-sm">
                                 <div>
                                   <p className="font-bold text-gray-900 text-sm">{pmt.patient}</p>
                                   <p className="text-[10px] font-bold text-gray-500">{pmt.invoice}</p>
                                 </div>
                                 <div className="text-right">
                                   <p className="font-black text-gray-900">${pmt.amount}</p>
                                   <p className={`text-[10px] uppercase font-bold tracking-wider ${pmt.status === 'Overdue' ? 'text-red-600' : 'text-orange-600'}`}>{pmt.status}</p>
                                 </div>
                              </div>
                           ))}
                           <button className="w-full mt-2 text-xs font-bold text-orange-700 bg-orange-50 border border-orange-200 py-2 rounded-lg hover:bg-orange-100">Send Reminders</button>
                        </div>
                     )}
                  </div>
               </div>

               {/* Activity Feed */}
               <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
                  <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                    <h2 className="text-[15px] font-bold text-gray-900 flex items-center gap-2">
                       <Clock size={16} className="text-gray-600" /> Recent Activity
                    </h2>
                  </div>
                  <div className="p-4">
                     {loading ? (
                        <div className="h-32 bg-gray-100 rounded animate-pulse"></div>
                     ) : (
                        <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-300 before:to-transparent">
                           {data.activity.map((act: any, idx: number) => (
                              <div key={idx} className="relative flex items-start">
                                 <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-white border-4 border-gray-200"></div>
                                 <div className="ml-8 pr-4">
                                    <p className="text-[10px] font-bold text-gray-500">{act.time}</p>
                                    <p className="text-sm font-bold text-gray-900 mt-0.5">{act.action}</p>
                                    <p className="text-xs text-gray-600 font-medium">{act.subject}</p>
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
               <h2 className="text-xl font-bold text-gray-900">Process Payment</h2>
               <button onClick={() => setShowPaymentModal(false)} className="text-gray-500 hover:text-gray-900 font-bold text-xl">&times;</button>
             </div>
             <div className="p-6 space-y-4">
                <div>
                   <label className="block text-sm font-bold text-gray-700 mb-2">Select Patient</label>
                   <select className="w-full border border-gray-300 rounded p-2 focus:ring-2 outline-none">
                      <option>Alice Brown (INV-001)</option>
                   </select>
                </div>
                <div>
                   <label className="block text-sm font-bold text-gray-700 mb-2">Amount</label>
                   <input type="number" defaultValue="450" className="w-full border border-gray-300 rounded p-2 focus:ring-2 outline-none" />
                </div>
                <button onClick={() => setShowPaymentModal(false)} className="w-full bg-emerald-600 text-white font-bold py-3 pt-3 mt-4 rounded hover:bg-emerald-700 transition">Process Charge</button>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}
