"use client";

import { useAuth } from "@/app/providers";
import {
  Calendar,
  Users,
  Stethoscope,
  TrendingUp,
  Clock,
  AlertCircle,
  Activity,
} from "lucide-react";
import Link from "next/link";

export default function DoctorDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-white">
        <h1 className="text-3xl font-bold">
          Welcome back, Dr. {user?.email?.split("@")[0]}
        </h1>
        <p className="text-blue-100 mt-2">
          Manage consultations, diagnoses, and patient care
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Today's Consultations */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Today's Consultations
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">5</p>
              <p className="text-xs text-green-600 mt-2">↑ 2 from yesterday</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Stethoscope className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        {/* Pending Diagnoses */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Pending Diagnoses
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">8</p>
              <p className="text-xs text-yellow-600 mt-2">
                Awaiting confirmation
              </p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-lg">
              <AlertCircle className="text-yellow-600" size={24} />
            </div>
          </div>
        </div>

        {/* Treatment Plans */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Active Treatment Plans
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">12</p>
              <p className="text-xs text-blue-600 mt-2">In progress</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <Activity className="text-purple-600" size={24} />
            </div>
          </div>
        </div>

        {/* Completed Cases */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-gray-700 text-sm font-semibold">
                Completed This Month
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">18</p>
              <p className="text-xs text-green-600 mt-2">Total cases</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <TrendingUp className="text-green-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Schedule */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar size={20} className="text-blue-600" />
              Today's Schedule
            </h2>
            <div className="space-y-3">
              {[
                {
                  time: "09:00 AM",
                  patient: "John Doe",
                  issue: "Root Canal - Tooth 36",
                  status: "Upcoming",
                },
                {
                  time: "10:30 AM",
                  patient: "Jane Smith",
                  issue: "Crown Placement - Tooth 11",
                  status: "In Progress",
                },
                {
                  time: "01:00 PM",
                  patient: "Mike Johnson",
                  issue: "Filling - Tooth 16",
                  status: "Scheduled",
                },
                {
                  time: "02:30 PM",
                  patient: "Sarah Wilson",
                  issue: "Oral Exam",
                  status: "Scheduled",
                },
              ].map((slot, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{slot.patient}</p>
                    <p className="text-xs text-gray-700 font-medium">
                      {slot.issue}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      {slot.time}
                    </p>
                    <span
                      className={`inline-block text-xs font-semibold px-2 py-1 rounded mt-1 ${
                        slot.status === "In Progress"
                          ? "bg-blue-100 text-blue-700"
                          : slot.status === "Upcoming"
                            ? "bg-orange-100 text-orange-700"
                            : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {slot.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Cases */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Users size={20} className="text-green-600" />
              Recent Cases
            </h2>
            <div className="space-y-3">
              {[
                {
                  patient: "Alice Brown",
                  diagnosis: "Dental Caries",
                  date: "2024-03-20",
                  status: "Completed",
                },
                {
                  patient: "Bob Davis",
                  diagnosis: "Gingivitis",
                  date: "2024-03-19",
                  status: "Completed",
                },
                {
                  patient: "Carol White",
                  diagnosis: "Root Canal Required",
                  date: "2024-03-18",
                  status: "In Treatment",
                },
              ].map((case_, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{case_.patient}</p>
                    <p className="text-xs text-gray-700 font-medium">
                      {case_.diagnosis}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-700 font-medium">
                      {case_.date}
                    </p>
                    <span
                      className={`inline-block text-xs font-semibold px-2 py-1 rounded mt-1 ${
                        case_.status === "Completed"
                          ? "bg-green-100 text-green-700"
                          : "bg-blue-100 text-blue-700"
                      }`}
                    >
                      {case_.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Quick Links */}
        <div className="space-y-6">
          {/* Action Buttons */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-2">
              <Link
                href="/dashboard/clinical"
                className="block w-full px-4 py-2.5 bg-blue-600 text-white text-center rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Start Consultation
              </Link>
              <Link
                href="/dashboard/diagnosis"
                className="block w-full px-4 py-2.5 bg-purple-600 text-white text-center rounded-lg font-medium hover:bg-purple-700 transition-colors"
              >
                View Diagnoses
              </Link>
              <Link
                href="/dashboard/treatment"
                className="block w-full px-4 py-2.5 bg-green-600 text-white text-center rounded-lg font-medium hover:bg-green-700 transition-colors"
              >
                Treatment Plans
              </Link>
              <Link
                href="/dashboard/assessment"
                className="block w-full px-4 py-2.5 bg-orange-600 text-white text-center rounded-lg font-medium hover:bg-orange-700 transition-colors"
              >
                Run Assessment
              </Link>
            </div>
          </div>

          {/* Alerts */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Alerts</h3>
            <div className="space-y-3">
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-xs font-semibold text-red-700">
                  ⚠ 3 patients with allergies
                </p>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs font-semibold text-yellow-700">
                  📋 5 pending diagnoses
                </p>
              </div>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs font-semibold text-blue-700">
                  📅 3 follow-ups due today
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
