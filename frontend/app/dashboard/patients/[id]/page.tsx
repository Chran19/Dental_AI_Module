"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/app/providers";
import { useParams, useRouter } from "next/navigation";
import { useQueueStatus } from "@/lib/hooks/useQueueStatus";
import { Patient } from "@/lib/types/patient";
import { fetchPatientById, updateQueueStatus } from "@/lib/store";
import {
  User,
  Phone,
  Mail,
  Calendar,
  Edit2,
  DollarSign,
  AlertTriangle,
  MoreVertical,
  Pill,
  FileText,
  ArrowLeft,
  Loader2,
  Stethoscope,
  BookOpen,
  CheckCircle,
  Activity,
  ChevronRight,
  LogOut,
} from "lucide-react";
import Link from "next/link";

export default function PatientProfilePage() {
  const { isAuthenticated, user } = useAuth();
  const params = useParams();
  const router = useRouter();
  const patientId = params?.id as string;

  // Auto-mark as In_Consultation when doctor accesses patient
  const { queueId } = useQueueStatus(patientId);

  const [patient, setPatient] = useState<Patient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMenu, setShowMenu] = useState(false);
  const [isEndingConsultation, setIsEndingConsultation] = useState(false);

  useEffect(() => {
    if (!patientId) return;

    const loadPatient = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchPatientById(patientId);
        if (data) {
          setPatient(data);
        } else {
          setError("Patient not found");
        }
      } catch (err: any) {
        setError(err.message || "Failed to load patient");
      } finally {
        setIsLoading(false);
      }
    };

    loadPatient();
  }, [patientId]);

  const handleEndConsultation = async () => {
    if (!queueId) {
      console.error("No active queue ID found");
      return;
    }

    setIsEndingConsultation(true);
    try {
      await updateQueueStatus(queueId, "Completed");
      // Redirect back to queue after successful completion
      setTimeout(() => {
        router.push("/dashboard/queue");
      }, 500);
    } catch (err) {
      console.error("Failed to end consultation:", err);
      alert("Failed to end consultation. Please try again.");
      setIsEndingConsultation(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="animate-spin text-blue-600" size={32} />
          <p className="text-slate-500 text-sm font-medium">
            Loading patient record...
          </p>
        </div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="max-w-md mx-auto mt-20 text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 text-red-600 mb-2">
          <AlertTriangle size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Patient Not Found</h2>
        <p className="text-slate-500">
          {error ||
            "The patient record you're looking for doesn't exist or has been removed."}
        </p>
        <Link
          href="/dashboard/patients"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700"
        >
          <ArrowLeft size={16} /> Back to Patients
        </Link>
      </div>
    );
  }

  // Helper: get display values
  const fullName = `${patient.first_name} ${patient.last_name}`;
  const email = patient.contact_email || patient.email || "Not provided";
  const phone = patient.contact_phone || patient.phone || "Not provided";
  const dob = patient.dob || patient.date_of_birth || null;
  const gender = patient.gender || "Not specified";
  const allergies: string[] = patient.medical_history?.allergies || [];
  const reasonOfVisit =
    patient.reason_of_visit || patient.medical_history?.reason_of_visit || null;

  const getAge = (dobStr: string | null) => {
    if (!dobStr) return null;
    const today = new Date();
    const birthDate = new Date(dobStr);
    let ageCalc = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      ageCalc--;
    }
    return ageCalc;
  };

  const age = getAge(dob);

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/dashboard/patients"
        className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-medium text-sm"
      >
        <ArrowLeft size={16} /> Back to Patient Records
      </Link>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-2xl font-bold">
            {patient.first_name?.charAt(0) || "?"}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{fullName}</h1>
            <p className="text-gray-600 text-sm">
              Patient ID: {patient.id?.substring(0, 8)}...
            </p>
            {patient.created_at && (
              <p className="text-gray-400 text-xs mt-0.5">
                Registered: {new Date(patient.created_at).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Link
            href={`/dashboard/patients/${patientId}/edit`}
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
      {allergies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertTriangle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <h3 className="font-semibold text-red-900">Allergies</h3>
            <p className="text-red-700">{allergies.join(", ")}</p>
          </div>
        </div>
      )}

      {/* Reason of Visit */}
      {reasonOfVisit && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex gap-3">
          <FileText className="text-purple-600 flex-shrink-0" size={20} />
          <div>
            <h3 className="font-semibold text-purple-900">
              Latest Reason of Visit
            </h3>
            <p className="text-purple-700">{reasonOfVisit}</p>
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
                  <p className="text-gray-900 font-medium">{phone}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Email
                  </p>
                  <p className="text-gray-900 font-medium">{email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <User className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    Gender
                  </p>
                  <p className="text-gray-900 font-medium">{gender}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="text-gray-400" size={20} />
                <div>
                  <p className="text-xs text-gray-700 font-semibold uppercase">
                    DOB / Age
                  </p>
                  <p className="text-gray-900 font-medium">
                    {dob
                      ? `${new Date(dob).toLocaleDateString()} ${age !== null ? `(${age}y)` : ""}`
                      : "Not provided"}
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
                  {patient.medical_history?.conditions?.length ? (
                    patient.medical_history.conditions.map(
                      (condition: string, idx: number) => (
                        <div
                          key={idx}
                          className="px-3 py-2 bg-blue-50 rounded-lg text-sm"
                        >
                          {condition}
                        </div>
                      ),
                    )
                  ) : (
                    <p className="text-gray-500 text-sm">
                      No conditions recorded
                    </p>
                  )}
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertTriangle size={18} className="text-red-600" />
                  Known Allergies
                </h3>
                <div className="space-y-2">
                  {allergies.length > 0 ? (
                    allergies.map((allergy: string, idx: number) => (
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

          {/* Recent Visits / Activity */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FileText size={20} className="text-purple-600" />
              Patient Record
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <p className="text-gray-900">Registration Date</p>
                <p className="text-sm text-gray-600">
                  {patient.created_at
                    ? new Date(patient.created_at).toLocaleDateString()
                    : "N/A"}
                </p>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <p className="text-gray-900">Last Updated</p>
                <p className="text-sm text-gray-600">
                  {patient.updated_at
                    ? new Date(patient.updated_at).toLocaleDateString()
                    : "N/A"}
                </p>
              </div>
              {patient.doctor_id && (
                <div className="flex justify-between items-center py-3">
                  <p className="text-gray-900">Assigned Doctor ID</p>
                  <p className="text-sm text-gray-600 font-mono">
                    {patient.doctor_id.substring(0, 8)}...
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Quick Info */}
        <div className="space-y-6">
          {/* Patient Summary */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">
              Patient Summary
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500">ID:</span>
                <span className="font-mono text-gray-900 text-xs bg-gray-100 px-2 py-1 rounded">
                  {patient.id?.substring(0, 12)}...
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500">Status:</span>
                <span className="text-green-700 bg-green-50 px-2 py-0.5 rounded text-xs font-bold">
                  Active
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <Link
                href="/dashboard/patients/new"
                className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors block"
              >
                New Visit / Check-in
              </Link>
              <button className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                Print Records
              </button>
              <button className="w-full px-4 py-2 text-left text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                Schedule Appointment
              </button>
              {user?.role === "DOCTOR" && queueId && (
                <button
                  onClick={handleEndConsultation}
                  disabled={isEndingConsultation}
                  className="w-full px-4 py-2 text-left text-sm font-medium text-green-600 hover:bg-green-50 rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  <LogOut size={16} />
                  {isEndingConsultation ? "Completing..." : "End Consultation"}
                </button>
              )}
            </div>
          </div>

          {/* Doctor Tools - Upgraded UI Module */}
          {user?.role === "DOCTOR" && (
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border border-indigo-100 p-6">
              <h3 className="font-bold text-indigo-900 mb-4 flex items-center gap-2">
                <Stethoscope size={20} className="text-indigo-600" />
                Clinical Workflow
              </h3>
              <div className="grid grid-cols-1 gap-3">
                <Link
                  href={`/dashboard/patients/${patientId}/clinical`}
                  className="flex items-center justify-between px-4 py-3 bg-white hover:bg-indigo-50 border border-indigo-100 rounded-lg transition-colors shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <FileText size={18} className="text-indigo-600" />
                    <span className="font-medium text-slate-800">
                      Clinical Input
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-indigo-400" />
                </Link>

                <Link
                  href={`/dashboard/patients/${patientId}/diagnosis`}
                  className="flex items-center justify-between px-4 py-3 bg-white hover:bg-indigo-50 border border-indigo-100 rounded-lg transition-colors shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <BookOpen size={18} className="text-indigo-600" />
                    <span className="font-medium text-slate-800">
                      Diagnosis
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-indigo-400" />
                </Link>

                <Link
                  href={`/dashboard/patients/${patientId}/treatment`}
                  className="flex items-center justify-between px-4 py-3 bg-white hover:bg-indigo-50 border border-indigo-100 rounded-lg transition-colors shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <Pill size={18} className="text-indigo-600" />
                    <span className="font-medium text-slate-800">
                      Treatment Plan
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-indigo-400" />
                </Link>

                <Link
                  href={`/dashboard/patients/${patientId}/results`}
                  className="flex items-center justify-between px-4 py-3 bg-white hover:bg-indigo-50 border border-indigo-100 rounded-lg transition-colors shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle size={18} className="text-indigo-600" />
                    <span className="font-medium text-slate-800">
                      Results & Closure
                    </span>
                  </div>
                  <ChevronRight size={16} className="text-indigo-400" />
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
