"use client";

import { useState, useEffect, use } from "react";
import { useAuth } from "@/app/providers";
import { Edit3, Save, X, AlertCircle } from "lucide-react";
import Link from "next/link";
import { fetchAPI } from "@/lib/api";

interface PatientData {
  id?: string;
  first_name: string;
  last_name: string;
  contact_email: string;
  contact_phone: string;
  age?: number;
  gender: string;
  address?: string;
  dob: string;
  medical_conditions?: string;
  allergies?: string;
  insurance?: string;
}

export default function EditPatientPage({
  params: paramsPromise,
}: {
  params: Promise<{ id: string }>;
}) {
  const params = use(paramsPromise);
  const patientId = params.id;
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<PatientData>({
    first_name: "",
    last_name: "",
    contact_email: "",
    contact_phone: "",
    gender: "",
    dob: "",
  });

  // Fetch patient data on mount
  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log("[EditPatient] Fetching patient:", {
          patientId,
          isAuthenticated,
          url: `/patients/${patientId}`,
        });

        // fetchAPI already returns parsed data and throws on errors
        const data = await fetchAPI(`/patients/${patientId}`);

        console.log("[EditPatient] Loaded data:", data);

        setFormData({
          id: data.id,
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          contact_email: data.contact_email || "",
          contact_phone: data.contact_phone || "",
          gender: data.gender || "",
          dob: data.dob || "",
        });
      } catch (err) {
        console.error("[EditPatient] Caught error:", err);
        const errorMessage =
          err instanceof Error
            ? err.message
            : typeof err === "string"
              ? err
              : JSON.stringify(err) || "Failed to load patient data";
        setError(errorMessage);
        console.error("Error fetching patient:", {
          error: err,
          errorType: typeof err,
          message: errorMessage,
          patientId,
          isAuthenticated,
        });
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated && patientId) {
      fetchPatientData();
    } else {
      console.warn("[EditPatient] Skipping fetch:", {
        isAuthenticated,
        patientId,
      });
    }
  }, [isAuthenticated, patientId]);

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
      const data = await fetchAPI(`/patients/${patientId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      // fetchAPI returns parsed data directly and throws on error
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
          href={`/dashboard/patients/${patientId}`}
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
                {/* First Name */}
                <div>
                  <label
                    htmlFor="first_name"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    First Name *
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    placeholder="Enter first name"
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                    required
                  />
                </div>

                {/* Last Name */}
                <div>
                  <label
                    htmlFor="last_name"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    Last Name *
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    placeholder="Enter last name"
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="contact_email"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="contact_email"
                    name="contact_email"
                    value={formData.contact_email}
                    onChange={handleChange}
                    placeholder="Enter email address"
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                    required
                  />
                </div>

                {/* Phone */}
                <div>
                  <label
                    htmlFor="phone"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    id="contact_phone"
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleChange}
                    placeholder="Enter phone number"
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                    required
                  />
                </div>

                {/* Date of Birth */}
                <div>
                  <label
                    htmlFor="dob"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    id="dob"
                    name="dob"
                    value={formData.dob}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Gender */}
                <div>
                  <label
                    htmlFor="gender"
                    className="block text-sm font-medium text-black mb-2"
                  >
                    Gender
                  </label>
                  <select
                    id="gender"
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-gray-300 bg-white text-black rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
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
                  <p className="font-medium text-gray-900">
                    {formData.first_name} {formData.last_name}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Email
                  </p>
                  <p className="font-medium text-gray-900 truncate">
                    {formData.contact_email}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Phone
                  </p>
                  <p className="font-medium text-gray-900">
                    {formData.contact_phone}
                  </p>
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
