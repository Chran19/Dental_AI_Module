"use client";

import { useState } from "react";
import { useAuth } from "@/app/providers";
import {
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Edit2,
  DollarSign,
  AlertTriangle,
  MoreVertical,
  Pill,
  FileText,
} from "lucide-react";
import Link from "next/link";

interface PatientProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  age: number;
  gender: string;
  address: string;
  date_of_birth: string;
  medical_conditions: string[];
  allergies: string[];
  insurance: string;
  last_visit: string;
  total_visits: number;
  balance: number;
}

export default function PatientProfilePage({
  params,
}: {
  params: { id: string };
}) {
  const { isAuthenticated } = useAuth();
  const [patient, setPatient] = useState<PatientProfile>({
    id: params.id,
    name: "John Doe",
    email: "john@example.com",
    phone: "(555) 123-4567",
    age: 42,
    gender: "Male",
    address: "123 Main St, City, State 12345",
    date_of_birth: "1982-03-15",
    medical_conditions: ["Hypertension", "Type 2 Diabetes"],
    allergies: ["Penicillin"],
    insurance: "Blue Cross Blue Shield",
    last_visit: "2024-03-20",
    total_visits: 12,
    balance: 150.0,
  });

  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-2xl font-bold">
            {patient.name.charAt(0)}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{patient.name}</h1>
            <p className="text-gray-600">Patient ID: {patient.id}</p>
          </div>
        </div>

        <div className="flex gap-2">
          <Link
            href={`/dashboard/patients/${params.id}/edit`}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Edit2 size={18} />
            Edit
          </Link>
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <MoreVertical size={20} />
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                <button className="w-full text-left px-4 py-2 hover:bg-gray-50 text-red-600 font-medium rounded-t-lg">
                  Delete Patient
                </button>
                <button className="w-full text-left px-4 py-2 hover:bg-gray-50 rounded-b-lg">
                  Export Records
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Alert if allergies */}
      {patient.allergies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertTriangle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <h3 className="font-semibold text-red-900">Allergies</h3>
            <p className="text-red-700">{patient.allergies.join(", ")}</p>
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Personal Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Contact Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <Phone className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Phone
                  </p>
                  <p className="text-gray-900 font-medium">{patient.phone}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Email
                  </p>
                  <p className="text-gray-900 font-medium">{patient.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Address
                  </p>
                  <p className="text-gray-900 font-medium text-sm">
                    {patient.address}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    DOB / Age
                  </p>
                  <p className="text-gray-900 font-medium">
                    {patient.date_of_birth} ({patient.age}y)
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Medical History */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Medical History
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Pill size={18} className="text-blue-600" />
                  Medical Conditions
                </h3>
                <div className="space-y-2">
                  {patient.medical_conditions.map((condition, idx) => (
                    <div
                      key={idx}
                      className="px-3 py-2 bg-blue-50 rounded-lg text-sm"
                    >
                      {condition}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertTriangle size={18} className="text-red-600" />
                  Known Allergies
                </h3>
                <div className="space-y-2">
                  {patient.allergies.length > 0 ? (
                    patient.allergies.map((allergy, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 bg-red-50 rounded-lg text-sm font-medium text-red-700"
                      >
                        {allergy}
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">No known allergies</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Visits */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FileText size={20} className="text-purple-600" />
              Recent Activity
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <p className="text-gray-900">Last dental examination</p>
                <p className="text-sm text-gray-600">
                  {new Date(patient.last_visit).toLocaleDateString()}
                </p>
              </div>
              <div className="flex justify-between items-center py-3">
                <p className="text-gray-900">Total visits</p>
                <p className="font-semibold text-gray-900">
                  {patient.total_visits}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Account Info */}
        <div className="space-y-6">
          {/* Insurance */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Insurance</h3>
            <p className="text-gray-600 text-sm">{patient.insurance}</p>
          </div>

          {/* Account Balance */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Account Balance</h3>
              <DollarSign className="text-blue-600" size={20} />
            </div>
            <p
              className={`text-3xl font-bold ${
                patient.balance > 0 ? "text-red-600" : "text-green-600"
              }`}
            >
              ${patient.balance.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {patient.balance > 0 ? "Amount due" : "Paid"}
            </p>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                Print Records
              </button>
              <button className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                Send Bill
              </button>
              <button className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                Schedule Appointment
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
