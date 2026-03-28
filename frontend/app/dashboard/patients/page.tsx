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
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    gender: "all",
    registrationDate: "all", // all, week, month, year
  });

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

  const applyFilters = () => {
    let result = [...patients];

    // Apply gender filter
    if (filters.gender !== "all") {
      result = result.filter(
        (p) => p.gender?.toLowerCase() === filters.gender.toLowerCase(),
      );
    }

    // Apply registration date filter (would need created_at field)
    // For now, just demonstration

    setFilteredPatients(result);
    setShowFilters(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="text-blue-600" />
            Patient Records
          </h1>
          <p className="text-slate-700 text-sm mt-1 font-medium">
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
        <button
          onClick={() => setShowFilters(true)}
          className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm hover:bg-slate-50 transition-colors font-medium"
        >
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

      {/* Filters Modal */}
      {showFilters && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-900">
                Filter Patients
              </h2>
              <button
                onClick={() => setShowFilters(false)}
                className="text-slate-500 hover:text-slate-700 font-bold text-xl"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* Gender Filter */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Gender
                </label>
                <select
                  value={filters.gender}
                  onChange={(e) =>
                    setFilters({ ...filters, gender: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Genders</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Registration Date Filter */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Registration Date
                </label>
                <select
                  value={filters.registrationDate}
                  onChange={(e) =>
                    setFilters({ ...filters, registrationDate: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Time</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="year">This Year</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 p-6 border-t border-slate-200">
              <button
                onClick={() => setShowFilters(false)}
                className="flex-1 px-4 py-2 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={applyFilters}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
