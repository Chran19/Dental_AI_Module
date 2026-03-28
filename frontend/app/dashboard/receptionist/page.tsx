"use client";

import { useAuth } from "@/app/providers";
import {
  Clock,
  Users,
  Phone,
  CheckCircle,
  AlertCircle,
  DollarSign,
  CalendarDays,
} from "lucide-react";
import Link from "next/link";

export default function ReceptionistDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 rounded-lg p-8 text-white">
        <h1 className="text-3xl font-bold">
          Welcome, {user?.email?.split("@")[0]}
        </h1>
        <p className="text-emerald-100 mt-2">
          Manage patient check-ins, appointments, and clinic operations
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Checked In */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Checked In Today
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">12</p>
              <p className="text-xs text-green-600 mt-2">✓ All confirmed</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <CheckCircle className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        {/* In Queue */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Currently in Queue
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">5</p>
              <p className="text-xs text-blue-600 mt-2">Avg wait: 15 min</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Clock className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        {/* New Patients */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                New Patients This Month
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">8</p>
              <p className="text-xs text-purple-600 mt-2">Registered</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <Users className="text-purple-600" size={24} />
            </div>
          </div>
        </div>

        {/* Pending Payments */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Pending Payments
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">$1,250</p>
              <p className="text-xs text-orange-600 mt-2">4 invoices due</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <DollarSign className="text-orange-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Current Queue */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Clock size={20} className="text-blue-600" />
              Current Queue
            </h2>
            <div className="space-y-2">
              {[
                {
                  position: 1,
                  patient: "John Doe",
                  doctor: "Dr. Smith",
                  time: "09:15 AM",
                  status: "Waiting",
                },
                {
                  position: 2,
                  patient: "Jane Smith",
                  doctor: "Dr. Johnson",
                  time: "09:30 AM",
                  status: "In Consultation",
                },
                {
                  position: 3,
                  patient: "Mike Johnson",
                  doctor: "Dr. Smith",
                  time: "09:45 AM",
                  status: "Waiting",
                },
                {
                  position: 4,
                  patient: "Sarah Wilson",
                  doctor: "Dr. Brown",
                  time: "10:00 AM",
                  status: "Waiting",
                },
                {
                  position: 5,
                  patient: "Tom Anderson",
                  doctor: "Dr. Johnson",
                  time: "10:15 AM",
                  status: "Waiting",
                },
              ].map((item) => (
                <div
                  key={item.position}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    item.status === "In Consultation"
                      ? "bg-blue-50 border-blue-200"
                      : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                  } transition-colors`}
                >
                  <div className="flex items-center gap-3">
                    <span className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full font-bold text-sm">
                      {item.position}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900">
                        {item.patient}
                      </p>
                      <p className="text-xs text-gray-700 font-medium">
                        {item.doctor}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      {item.time}
                    </p>
                    <span
                      className={`inline-block text-xs font-semibold px-2 py-1 rounded mt-1 ${
                        item.status === "In Consultation"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-200 text-gray-700"
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Appointments Today */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CalendarDays size={20} className="text-purple-600" />
              Today's Appointments
            </h2>
            <div className="space-y-3">
              {[
                {
                  time: "09:00 AM",
                  patient: "John Doe",
                  phone: "(555) 123-4567",
                  status: "Confirmed",
                },
                {
                  time: "10:30 AM",
                  patient: "Jane Smith",
                  phone: "(555) 234-5678",
                  status: "Confirmed",
                },
                {
                  time: "02:00 PM",
                  patient: "Mike Johnson",
                  phone: "(555) 345-6789",
                  status: "Pending",
                },
              ].map((apt, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <p className="font-semibold text-gray-900 w-20">
                      {apt.time}
                    </p>
                    <div>
                      <p className="font-medium text-gray-900">{apt.patient}</p>
                      <p className="text-xs text-gray-700 font-medium flex items-center gap-1">
                        <Phone size={14} />
                        {apt.phone}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-semibold px-3 py-1 rounded ${
                      apt.status === "Confirmed"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {apt.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-2">
              <Link
                href="/dashboard/patients/new"
                className="block w-full px-4 py-2.5 bg-emerald-600 text-white text-center rounded-lg font-medium hover:bg-emerald-700 transition-colors"
              >
                Register New Patient
              </Link>
              <Link
                href="/dashboard/queue"
                className="block w-full px-4 py-2.5 bg-blue-600 text-white text-center rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Manage Queue
              </Link>
              <button className="block w-full px-4 py-2.5 border border-gray-300 text-gray-700 text-center rounded-lg font-medium hover:bg-gray-50 transition-colors">
                Call Next Patient
              </button>
            </div>
          </div>

          {/* Important Info */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Important</h3>
            <div className="space-y-3">
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs font-semibold text-yellow-700">
                  ⚠ 2 pending confirmations
                </p>
              </div>
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-xs font-semibold text-red-700">
                  🔔 1 no-show scheduled
                </p>
              </div>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs font-semibold text-blue-700">
                  📞 5 follow-up calls due
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
