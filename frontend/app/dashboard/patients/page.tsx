"use client";

import { useEffect, useState } from "react";
import { Plus, Users, Filter } from "lucide-react";
import PatientTable from "@/components/patients/PatientTable";
import PatientSearch from "@/components/patients/PatientSearch";
import { Patient } from "@/lib/types/patient";
import Link from "next/link";
import { fetchAPI } from "@/lib/api";

export default function PatientsDashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatients = async () => {
    setIsLoading(true);
    try {
      const response = await fetchAPI("/patients", { method: "GET" });
      setPatients(response);
      setFilteredPatients(response);
    } catch (err: any) {
      console.error("Error fetching patients:", err);
      setError(
        "Unable to load patients. Please check if the backend is running.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleSearch = (query: string) => {
    if (!query.trim()) {
      setFilteredPatients(patients);
      return;
    }

    const q = query.toLowerCase();
    const filtered = patients.filter(
      (p) =>
        `${p.first_name} ${p.last_name}`.toLowerCase().includes(q) ||
        p.email?.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q),
    );
    setFilteredPatients(filtered);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="text-blue-600" />
            Patient Records
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Manage and search patient database
          </p>
        </div>

        <Link
          href="/dashboard/patients/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all shadow-md shadow-blue-100"
        >
          <Plus size={18} />
          <span>New Patient</span>
        </Link>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <PatientSearch onSearch={handleSearch} />
        </div>
        <button className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm hover:bg-slate-50 transition-colors">
          <Filter size={16} />
          <span>Filters</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      <PatientTable patients={filteredPatients} isLoading={isLoading} />
    </div>
  );
}
