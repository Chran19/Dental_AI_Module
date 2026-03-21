"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getPatients, createPatient } from "@/lib/api";
import { useAuth } from "@/app/providers";

export default function PatientsPage() {
  const { isAuthenticated } = useAuth();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
  });

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const data = await getPatients();
        setPatients(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) fetchPatients();
  }, [isAuthenticated]);

  const handleAddPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createPatient(formData);
      setFormData({ first_name: "", last_name: "", email: "", phone: "" });
      setShowForm(false);
      const data = await getPatients();
      setPatients(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Patient Records
              </h1>
              <p className="mt-2 text-gray-600">Manage patient information</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 transition"
            >
              {showForm ? "Cancel" : "Add Patient"}
            </button>
          </div>

          {showForm && (
            <form
              onSubmit={handleAddPatient}
              className="mt-6 space-y-4 border-t pt-6"
            >
              <input
                type="text"
                placeholder="First Name"
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
                required
                className="w-full rounded-lg border px-4 py-2"
              />
              <input
                type="text"
                placeholder="Last Name"
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
                required
                className="w-full rounded-lg border px-4 py-2"
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
                className="w-full rounded-lg border px-4 py-2"
              />
              <input
                type="tel"
                placeholder="Phone"
                value={formData.phone}
                onChange={(e) =>
                  setFormData({ ...formData, phone: e.target.value })
                }
                className="w-full rounded-lg border px-4 py-2"
              />
              <button
                type="submit"
                className="w-full rounded-lg bg-indigo-600 py-2 text-white hover:bg-indigo-700"
              >
                Add Patient
              </button>
            </form>
          )}

          {loading && <p className="mt-6 text-gray-600">Loading patients...</p>}

          {error && (
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
              {error}
            </div>
          )}

          {!loading && patients.length === 0 && (
            <p className="mt-6 text-gray-600">
              No patients yet. Add one to get started.
            </p>
          )}

          {!loading && patients.length > 0 && (
            <div className="mt-6 overflow-x-auto">
              <table className="w-full border-collapse">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border p-3 text-left">Name</th>
                    <th className="border p-3 text-left">Email</th>
                    <th className="border p-3 text-left">Phone</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient, index) => (
                    <tr key={index} className="border hover:bg-gray-50">
                      <td className="border p-3">
                        {patient.first_name} {patient.last_name}
                      </td>
                      <td className="border p-3">{patient.email}</td>
                      <td className="border p-3">{patient.phone || "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
