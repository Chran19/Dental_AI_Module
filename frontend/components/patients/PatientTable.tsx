"use client";

import { Patient } from "@/lib/types/patient";
import Link from "next/link";
import { User, ChevronRight, Phone, Mail, Calendar } from "lucide-react";

interface PatientTableProps {
  patients: Patient[];
  isLoading: boolean;
}

export default function PatientTable({
  patients,
  isLoading,
}: PatientTableProps) {
  if (isLoading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="w-full py-12 text-center bg-white rounded-xl border-2 border-dashed border-slate-200">
        <div className="inline-flex items-center justify-center p-3 mb-4 rounded-full bg-slate-100 text-slate-400">
          <User size={32} />
        </div>
        <h3 className="text-lg font-medium text-slate-900">
          No patients found
        </h3>
        <p className="text-slate-500 mt-1">
          Try adjusting your search or add a new patient.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            <tr>
              <th scope="col" className="px-6 py-3 text-left">
                Patient
              </th>
              <th scope="col" className="px-6 py-3 text-left">
                Contact
              </th>
              <th scope="col" className="px-6 py-3 text-left">
                Created
              </th>
              <th scope="col" className="px-6 py-3 text-right">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {patients.map((patient) => (
              <tr
                key={patient.id}
                className="hover:bg-blue-50/30 transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-10 w-10 flex-shrink-0 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                      {patient.first_name?.[0]}
                      {patient.last_name?.[0]}
                    </div>
                    <div className="ml-4">
                      <Link
                        href={`/dashboard/patients/${patient.id}`}
                        className="text-sm font-semibold text-slate-900 hover:text-blue-600"
                      >
                        {patient.first_name} {patient.last_name}
                      </Link>
                      <div className="text-xs text-slate-500 font-mono mt-1">
                        ID: {patient.id.split("-")[0]}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="space-y-1">
                    {patient.phone && (
                      <div className="flex items-center gap-2 text-xs text-slate-600">
                        <Phone size={12} className="text-slate-400" />
                        <span>{patient.phone}</span>
                      </div>
                    )}
                    {patient.email && (
                      <div className="flex items-center gap-2 text-xs text-slate-600">
                        <Mail size={12} className="text-slate-400" />
                        <span>{patient.email}</span>
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    <Calendar size={12} className="text-slate-400" />
                    <span>
                      {patient.created_at
                        ? new Date(patient.created_at).toLocaleDateString()
                        : "N/A"}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link
                    href={`/dashboard/patients/${patient.id}`}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 rounded-md transition-all sm:text-xs"
                  >
                    View Record
                    <ChevronRight size={14} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
