"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/app/providers";
import { Edit3, Save, X, AlertCircle } from "lucide-react";
import Link from "next/link";
import { fetchAPI } from "@/lib/api";

interface PatientData {
  id?: number;
  name: string;
  email: string;
  phone: string;
  age: number;
  gender: string;
  address: string;
  date_of_birth: string;
  medical_conditions: string;
  allergies: string;
  insurance: string;
}

export default function EditPatientPage({
  params,
}: {
  params: { id: string };
}) {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<PatientData>({
    name: "",
    email: "",
    phone: "",
    age: 0,
    gender: "",
    address: "",
    date_of_birth: "",
    medical_conditions: "",
    allergies: "",
    insurance: "",
  });

  // Fetch patient data on mount
  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchAPI(`/patients/${params.id}`);

        if (!response.ok) {
          throw new Error(
            `Failed to fetch patient data: ${response.statusText}`,
          );
        }

        const data = await response.json();
        setFormData({
          id: data.id,
          name: data.name || "",
          email: data.email || "",
          phone: data.phone || "",
          age: data.age || 0,
          gender: data.gender || "",
          address: data.address || "",
          date_of_birth: data.date_of_birth || "",
          medical_conditions: data.medical_conditions || "",
          allergies: data.allergies || "",
          insurance: data.insurance || "",
        });
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load patient data";
        setError(errorMessage);
        console.error("Error fetching patient:", err);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated && params.id) {
      fetchPatientData();
    }
  }, [isAuthenticated, params.id]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === "" ? "" : name === "age" ? parseInt(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveLoading(true);
    setError(null);

    try {
      const response = await fetchAPI(`/patients/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Failed to update patient: ${response.statusText}`);
      }

      const data = await response.json();
      setFormData(data);
      alert("Patient information updated successfully!");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update patient";
      setError(errorMessage);
      console.error("Error updating patient:", err);
      alert(`Error: ${errorMessage}`);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <h3 className="font-medium text-red-900">Error</h3>
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-900">Loading patient information...</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Patient</h1>
          <p className="text-gray-600 mt-1">Update patient information</p>
        </div>
        <Link
          href={`/dashboard/patients/${params.id}`}
          className="inline-flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          <X size={20} />
        </Link>
      </div>

      {/* Form */}
      {!loading ? (
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Left Column - Personal Information */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Personal Information
              </h2>

              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Full Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Enter full name"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Enter email address"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Phone */}
                <div>
                  <label
                    htmlFor="phone"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="Enter phone number"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Date of Birth */}
                <div>
                  <label
                    htmlFor="date_of_birth"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    id="date_of_birth"
                    name="date_of_birth"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Gender */}
                <div>
                  <label
                    htmlFor="gender"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Gender
                  </label>
                  <select
                    id="gender"
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Age */}
                <div>
                  <label
                    htmlFor="age"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Age
                  </label>
                  <input
                    type="number"
                    id="age"
                    name="age"
                    value={formData.age || ""}
                    onChange={handleChange}
                    placeholder="Enter age"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Address */}
                <div>
                  <label
                    htmlFor="address"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Address
                  </label>
                  <input
                    type="text"
                    id="address"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="Enter street address"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Medical Conditions */}
                <div>
                  <label
                    htmlFor="medical_conditions"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Medical Conditions
                  </label>
                  <textarea
                    id="medical_conditions"
                    name="medical_conditions"
                    value={formData.medical_conditions}
                    onChange={handleChange}
                    placeholder="Enter medical conditions (comma-separated)"
                    rows={3}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Allergies */}
                <div>
                  <label
                    htmlFor="allergies"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Allergies
                  </label>
                  <textarea
                    id="allergies"
                    name="allergies"
                    value={formData.allergies}
                    onChange={handleChange}
                    placeholder="Enter known allergies (comma-separated)"
                    rows={3}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Insurance */}
                <div>
                  <label
                    htmlFor="insurance"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Insurance Provider
                  </label>
                  <input
                    type="text"
                    id="insurance"
                    name="insurance"
                    value={formData.insurance}
                    onChange={handleChange}
                    placeholder="Enter insurance provider"
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Summary & Actions */}
          <div>
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-8">
              <h3 className="font-semibold text-gray-900 mb-4">Summary</h3>

              <div className="space-y-3 mb-6 pb-6 border-b border-gray-200">
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Name
                  </p>
                  <p className="font-medium text-gray-900">{formData.name}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Email
                  </p>
                  <p className="font-medium text-gray-900 truncate">
                    {formData.email}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Phone
                  </p>
                  <p className="font-medium text-gray-900">{formData.phone}</p>
                </div>
              </div>

              <div className="space-y-2">
                <button
                  type="submit"
                  disabled={saveLoading}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <Save size={18} />
                  {saveLoading ? "Saving..." : "Save Changes"}
                </button>
                <Link
                  href={`/dashboard/patients/${params.id}`}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </Link>
              </div>
            </div>
          </div>
        </form>
      ) : null}
    </div>
  );
}
