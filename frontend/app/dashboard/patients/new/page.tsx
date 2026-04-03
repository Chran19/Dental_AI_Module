"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Patient } from "@/lib/types/patient";
import {
  createPatient,
  searchPatients,
  checkInPatient,
  fetchPatientById,
} from "@/lib/store";
import {
  UserPlus,
  ArrowLeft,
  Loader2,
  CheckCircle2,
  AlertCircle,
  User,
  Phone,
  HeartPulse,
  Search,
  ArrowRight,
  ClipboardList,
  UserCheck,
} from "lucide-react";
import Link from "next/link";

type IntakeMode = "choose" | "new" | "returning";
type Step = "form" | "review" | "success";

export default function PatientIntakePage() {
  const router = useRouter();
  const [mode, setMode] = useState<IntakeMode>("choose");
  const [step, setStep] = useState<Step>("form");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdPatientId, setCreatedPatientId] = useState<string>("");
  const [createdPatientName, setCreatedPatientName] = useState<string>("");

  // ── Returning patient search ──────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Patient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // ── Form data ─────────────────────────────────────────────────────────────
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    date_of_birth: "",
    gender: "",
    gender_self_describe: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    allergies: "",
    parent_guardian_name: "",
    parent_guardian_phone: "",
    parent_consent: false,
    reason_of_visit: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // ── Search for returning patients ─────────────────────────────────────────
  useEffect(() => {
    if (mode !== "returning" || searchQuery.length < 2) {
      setSearchResults([]);
      setSearchError(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      setSearchError(null);
      try {
        const results = await searchPatients(searchQuery);
        setSearchResults(results);
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : "Failed to search patients";
        setSearchError(errorMsg);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [searchQuery, mode]);

  // ── Pre-fill form when a returning patient is selected ────────────────────
  const handleSelectReturningPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    setFormData({
      ...formData,
      first_name: patient.first_name || "",
      last_name: patient.last_name || "",
      email: patient.contact_email || patient.email || "",
      phone: patient.contact_phone || patient.phone || "",
      date_of_birth: patient.dob
        ? new Date(patient.dob).toISOString().split("T")[0]
        : patient.date_of_birth || "",
      gender: patient.gender || "",
      gender_self_describe: "",
      emergency_contact_name: "",
      emergency_contact_phone: "",
      allergies: "",
      parent_guardian_name: "",
      parent_guardian_phone: "",
      parent_consent: false,
      reason_of_visit: "",
    });
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    if (
      name === "phone" ||
      name === "emergency_contact_phone" ||
      name === "parent_guardian_phone"
    ) {
      const cleaned = value.replace(/\D/g, "");
      let formatted = value;
      if (cleaned.length >= 10) {
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        if (match) formatted = `(${match[1]}) ${match[2]}-${match[3]}`;
      }
      setFormData((prev) => ({ ...prev, [name]: formatted }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const getAge = (dob: string) => {
    if (!dob) return null;
    const today = new Date();
    const birthDate = new Date(dob);
    let ageCalc = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      ageCalc--;
    }
    return ageCalc;
  };

  const age = getAge(formData.date_of_birth);
  const isMinor = age !== null && age < 18;

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.first_name.trim())
      newErrors.first_name = "First name is required";
    if (!formData.last_name.trim())
      newErrors.last_name = "Last name is required";
    if (!formData.reason_of_visit.trim())
      newErrors.reason_of_visit = "Reason of visit is required";

    if (mode === "new") {
      if (!formData.date_of_birth)
        newErrors.date_of_birth = "Date of birth is required";
      if (!formData.email && !formData.phone) {
        newErrors.contact = "Please provide either email or phone number";
        newErrors.email = "Required if phone is empty";
        newErrors.phone = "Required if email is empty";
      }
      if (
        formData.email &&
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
      ) {
        newErrors.email = "Invalid email format";
      }
      if (isMinor && !formData.parent_guardian_name) {
        newErrors.parent_guardian_name = "Required for minors";
      }
      if (isMinor && !formData.parent_consent) {
        newErrors.parent_consent = "Parent consent is required";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleReviewPhase = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (validateForm()) {
      setStep("review");
    }
  };

  const submitFinal = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      let patientId: string;
      let patientName: string;

      if (mode === "returning" && selectedPatient) {
        // Use existing patient — just check them in
        patientId = selectedPatient.id;
        patientName = `${selectedPatient.first_name} ${selectedPatient.last_name}`;
      } else {
        // Create new patient
        const genderValue =
          formData.gender === "Prefer to self-describe" ||
          formData.gender === "Other"
            ? "Other"
            : formData.gender;

        const result = await createPatient({
          first_name: formData.first_name,
          last_name: formData.last_name,
          dob: formData.date_of_birth
            ? new Date(formData.date_of_birth).toISOString()
            : new Date().toISOString(),
          gender: genderValue || "Other",
          contact_email: formData.email || undefined,
          contact_phone: formData.phone || undefined,
          medical_history: formData.allergies
            ? { allergies: formData.allergies.split(",").map((a) => a.trim()) }
            : undefined,
          reason_of_visit: formData.reason_of_visit,
        });
        patientId = result.id;
        patientName = `${formData.first_name} ${formData.last_name}`;
      }

      // Add patient to queue automatically
      const queueItem = await checkInPatient(
        patientId,
        undefined,
        formData.reason_of_visit,
      );

      // Validate that check-in was successful
      if (!queueItem) {
        throw new Error("Failed to check in patient - no queue item returned");
      }

      setCreatedPatientId(patientId);
      setCreatedPatientName(patientName);
      localStorage.removeItem("patient_intake_draft");
      setStep("success");
    } catch (err: any) {
      setError(
        err.message || "Failed to register patient or check in to queue",
      );
      setIsSubmitting(false);
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  //  RENDER: MODE CHOOSER
  // ═══════════════════════════════════════════════════════════════════════════

  if (mode === "choose") {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <div className="mb-6">
          <Link
            href="/dashboard/queue"
            className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-medium"
          >
            <ArrowLeft size={18} /> Back to Queue
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
              <ClipboardList className="text-blue-600" size={28} />
              Patient Intake
            </h1>
            <p className="text-slate-500 text-sm mt-1 font-medium">
              Is this a new patient or a previously registered patient?
            </p>
          </div>

          <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* New Patient Card */}
            <button
              onClick={() => setMode("new")}
              id="intake-new-patient"
              className="group p-6 rounded-xl border-2 border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 transition-all text-left flex flex-col gap-4"
            >
              <div className="w-14 h-14 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <UserPlus size={28} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  New Patient
                </h3>
                <p className="text-sm text-slate-500 font-medium mt-1">
                  Register a patient visiting for the first time. Fill out the
                  complete intake form.
                </p>
              </div>
              <div className="flex items-center gap-1 text-blue-600 font-bold text-sm mt-auto">
                Start Registration <ArrowRight size={16} />
              </div>
            </button>

            {/* Returning Patient Card */}
            <button
              onClick={() => setMode("returning")}
              id="intake-returning-patient"
              className="group p-6 rounded-xl border-2 border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/30 transition-all text-left flex flex-col gap-4"
            >
              <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                <UserCheck size={28} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  Registered Patient
                </h3>
                <p className="text-sm text-slate-500 font-medium mt-1">
                  Search for an existing patient in the database and add a new
                  visit.
                </p>
              </div>
              <div className="flex items-center gap-1 text-emerald-600 font-bold text-sm mt-auto">
                Search & Check-in <ArrowRight size={16} />
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  RENDER: RETURNING PATIENT SEARCH
  // ═══════════════════════════════════════════════════════════════════════════

  if (mode === "returning" && !selectedPatient) {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <div className="mb-6">
          <button
            onClick={() => setMode("choose")}
            className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-medium"
          >
            <ArrowLeft size={18} /> Back
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
              <Search className="text-emerald-600" size={28} />
              Search Registered Patient
            </h1>
            <p className="text-slate-500 text-sm mt-1 font-medium">
              Search by name, email, phone, or patient ID
            </p>
          </div>

          <div className="p-8 space-y-6">
            <div className="relative">
              <Search
                size={18}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                id="patient-search-input"
                type="text"
                placeholder="Type patient name, email, or phone..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
                className="w-full pl-12 pr-4 py-3 border border-gray-300 bg-white text-black rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-sm font-medium placeholder-gray-500"
              />
              {isSearching && (
                <Loader2
                  className="absolute right-4 top-1/2 -translate-y-1/2 animate-spin text-slate-400"
                  size={18}
                />
              )}
            </div>

            {searchError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-sm text-red-700 font-medium">
                <AlertCircle size={16} />
                <span>{searchError}</span>
              </div>
            )}

            {searchResults.length > 0 && (
              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  {searchResults.length} patient(s) found
                </p>
                {searchResults.map((patient) => (
                  <button
                    key={patient.id}
                    onClick={() => handleSelectReturningPatient(patient)}
                    className="w-full text-left p-4 rounded-xl border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/30 transition-all flex items-center gap-4 group"
                  >
                    <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-lg flex-shrink-0">
                      {patient.first_name?.[0]}
                      {patient.last_name?.[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-slate-900 truncate">
                        {patient.first_name} {patient.last_name}
                      </p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                        {(patient.contact_phone || patient.phone) && (
                          <span>{patient.contact_phone || patient.phone}</span>
                        )}
                        {(patient.contact_email || patient.email) && (
                          <span className="truncate">
                            {patient.contact_email || patient.email}
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-slate-400 font-mono mt-1">
                        ID: {patient.id.substring(0, 8)}
                      </p>
                    </div>
                    <ArrowRight
                      size={18}
                      className="text-slate-300 group-hover:text-emerald-600 transition-colors flex-shrink-0"
                    />
                  </button>
                ))}
              </div>
            )}

            {searchQuery.length >= 2 &&
              !isSearching &&
              searchResults.length === 0 && (
                <div className="text-center py-8">
                  <div className="mx-auto w-12 h-12 bg-slate-100 flex items-center justify-center rounded-full text-slate-400 mb-3">
                    <User size={24} />
                  </div>
                  <p className="text-slate-600 font-medium">
                    No patients found
                  </p>
                  <p className="text-slate-400 text-sm mt-1">
                    Try a different search or{" "}
                    <button
                      onClick={() => setMode("new")}
                      className="text-blue-600 font-bold hover:underline"
                    >
                      register as new
                    </button>
                  </p>
                </div>
              )}
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  RENDER: SUCCESS SCREEN
  // ═══════════════════════════════════════════════════════════════════════════

  if (step === "success") {
    return (
      <div className="max-w-md mx-auto mt-20 text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-2">
          <CheckCircle2 size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">
          {mode === "returning"
            ? "Patient Checked In!"
            : "Patient Registered & Checked In!"}
        </h2>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-left space-y-2 text-slate-800">
          <p className="text-sm">
            <strong>Name:</strong> {createdPatientName}
          </p>
          <p className="text-sm">
            <strong>Patient ID:</strong> {createdPatientId.substring(0, 8)}...
          </p>
          <p className="text-sm">
            <strong>Reason of Visit:</strong> {formData.reason_of_visit}
          </p>
          <p className="text-sm text-green-700 font-medium">
            Patient has been added to the queue.
          </p>
        </div>
        <div className="flex gap-2 pt-4">
          <Link
            href="/dashboard/queue"
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 text-center"
          >
            View Queue
          </Link>
          <Link
            href={`/dashboard/patients/${createdPatientId}`}
            className="flex-1 px-4 py-2 border border-green-600 text-green-600 rounded-lg font-bold hover:bg-green-50 text-center"
          >
            View Profile
          </Link>
        </div>
        <button
          onClick={() => {
            setMode("choose");
            setStep("form");
            setSelectedPatient(null);
            setFormData({
              first_name: "",
              last_name: "",
              email: "",
              phone: "",
              date_of_birth: "",
              gender: "",
              gender_self_describe: "",
              emergency_contact_name: "",
              emergency_contact_phone: "",
              allergies: "",
              parent_guardian_name: "",
              parent_guardian_phone: "",
              parent_consent: false,
              reason_of_visit: "",
            });
          }}
          className="text-sm text-slate-500 hover:text-slate-700 font-medium mt-2"
        >
          Register Another Patient
        </button>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  RENDER: REVIEW SCREEN
  // ═══════════════════════════════════════════════════════════════════════════

  if (step === "review") {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 shadow-sm">
          <h2 className="text-xl font-bold text-blue-900 mb-6 flex items-center gap-2">
            <UserPlus size={24} />{" "}
            {mode === "returning"
              ? "Confirm Patient Check-In"
              : "Confirm Patient Registration"}
          </h2>
          <div className="grid grid-cols-2 gap-6 text-sm">
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Name</p>
              <p className="font-bold text-gray-900 text-base">
                {formData.first_name} {formData.last_name}
              </p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">
                Date of Birth
              </p>
              <p className="font-bold text-gray-900 text-base">
                {formData.date_of_birth} {age !== null && `(${age} years old)`}
              </p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Phone</p>
              <p className="font-bold text-gray-900">
                {formData.phone || "N/A"}
              </p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Email</p>
              <p className="font-bold text-gray-900">
                {formData.email || "N/A"}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-gray-500 font-medium tracking-wide">
                Reason of Visit
              </p>
              <p className="font-bold text-blue-800 text-base bg-blue-100 px-3 py-2 rounded-lg mt-1">
                {formData.reason_of_visit}
              </p>
            </div>

            {mode === "returning" && selectedPatient && (
              <div className="col-span-2 bg-emerald-50 p-3 rounded border border-emerald-200">
                <p className="font-bold text-emerald-900 text-sm">
                  Returning Patient — ID: {selectedPatient.id.substring(0, 8)}
                  ...
                </p>
                <p className="text-emerald-700 text-xs mt-1">
                  Patient will be added to the queue with updated visit info.
                </p>
              </div>
            )}

            {isMinor && mode === "new" && (
              <div className="col-span-2 mt-4 bg-orange-50 p-3 rounded border border-orange-200">
                <p className="font-bold text-orange-900 mb-1">
                  Guardian Information (Minor)
                </p>
                <p className="text-orange-800">
                  Name: {formData.parent_guardian_name}
                </p>
                <p className="text-orange-800">
                  Phone: {formData.parent_guardian_phone}
                </p>
                <p className="text-orange-800 font-semibold mt-1 flex items-center gap-1">
                  <CheckCircle2 size={16} /> Consent Provided
                </p>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2 text-sm font-medium">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <div className="mt-8 flex gap-4">
            <button
              onClick={() => setStep("form")}
              className="flex-1 px-4 py-3 border border-blue-300 text-blue-700 rounded-lg font-bold hover:bg-blue-100 transition"
            >
              ← Edit Details
            </button>
            <button
              onClick={submitFinal}
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin" size={20} />{" "}
                  {mode === "returning" ? "Checking In..." : "Registering..."}
                </>
              ) : mode === "returning" ? (
                "Confirm & Check In"
              ) : (
                "Confirm & Register"
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  //  RENDER: INTAKE FORM (new or returning with pre-filled data)
  // ═══════════════════════════════════════════════════════════════════════════

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <button
          onClick={() => {
            if (mode === "returning") {
              setSelectedPatient(null);
            } else {
              setMode("choose");
            }
          }}
          className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-medium"
        >
          <ArrowLeft size={18} /> Back
        </button>
        {mode === "returning" && selectedPatient && (
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
            Returning Patient
          </span>
        )}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <UserPlus className="text-blue-600" size={28} />
            {mode === "returning"
              ? "Check-In — Reason of Visit"
              : "Patient Intake Form"}
          </h1>
          <p className="text-slate-500 text-sm mt-1 font-medium">
            {mode === "returning"
              ? `Updating visit for ${selectedPatient?.first_name} ${selectedPatient?.last_name}. You can edit contact info and add the reason for today's visit.`
              : "Register a new patient into the system."}
          </p>
        </div>

        <form onSubmit={handleReviewPhase} className="p-8 space-y-8">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-3 font-medium">
              <AlertCircle size={20} className="flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* ── Basic Information ──────────────────────────────────────────── */}
          <fieldset className="space-y-6 pb-8 border-b border-gray-100">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2">
              <User size={20} className="text-blue-500" /> Basic Information
            </legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label
                  htmlFor="first_name"
                  className="text-sm font-semibold text-slate-700"
                >
                  First Name *
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  readOnly={mode === "returning"}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium bg-white text-black border-gray-300 placeholder-gray-500 ${errors.first_name ? "border-red-500" : ""} ${mode === "returning" ? "bg-gray-100 text-gray-700" : ""}`}
                />
                {errors.first_name && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.first_name}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <label
                  htmlFor="last_name"
                  className="text-sm font-semibold text-slate-700"
                >
                  Last Name *
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  readOnly={mode === "returning"}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium bg-white text-black border-gray-300 placeholder-gray-500 ${errors.last_name ? "border-red-500" : ""} ${mode === "returning" ? "bg-gray-100 text-gray-700" : ""}`}
                />
                {errors.last_name && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.last_name}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Date of Birth {mode === "new" && "*"}
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  required={mode === "new"}
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  readOnly={mode === "returning"}
                  className={`w-full px-4 py-2 border border-gray-300 bg-white text-black rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${mode === "returning" ? "bg-gray-100 text-gray-700" : ""} ${errors.date_of_birth ? "border-red-500" : ""}`}
                />
                {errors.date_of_birth && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.date_of_birth}
                  </p>
                )}
                {age !== null && (
                  <p className="text-xs font-bold text-blue-600 mt-1">
                    Calculated Age: {age} years old
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Gender Identity
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  disabled={mode === "returning"}
                  className={`w-full px-4 py-2 border border-gray-300 bg-white text-black rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${mode === "returning" ? "bg-gray-100 text-gray-700" : ""}`}
                >
                  <option value="">Select...</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>
            </div>

            {/* Minor guardian section */}
            {isMinor && mode === "new" && (
              <div className="bg-blue-50 border border-blue-200 p-5 rounded-xl space-y-4 shadow-sm mt-6">
                <h3 className="font-bold text-blue-900 text-base">
                  Parent/Guardian Information (Required for Minors)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-slate-700">
                      Guardian Full Name *
                    </label>
                    <input
                      name="parent_guardian_name"
                      type="text"
                      value={formData.parent_guardian_name}
                      onChange={handleChange}
                      className={`w-full px-4 py-2 border rounded-lg text-sm font-medium bg-white text-black border-gray-300 placeholder-gray-500 ${errors.parent_guardian_name ? "border-red-500" : ""}`}
                    />
                    {errors.parent_guardian_name && (
                      <p className="text-red-600 text-xs font-bold">
                        {errors.parent_guardian_name}
                      </p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-slate-700">
                      Guardian Phone
                    </label>
                    <input
                      name="parent_guardian_phone"
                      type="tel"
                      value={formData.parent_guardian_phone}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white text-black placeholder-gray-500"
                    />
                  </div>
                </div>
                <label className="flex items-start gap-3 mt-4 p-3 bg-white border border-blue-100 rounded-lg cursor-pointer">
                  <input
                    name="parent_consent"
                    type="checkbox"
                    checked={formData.parent_consent}
                    onChange={handleChange}
                    className={`mt-1 w-5 h-5 rounded ${errors.parent_consent ? "border-red-500" : ""}`}
                  />
                  <div>
                    <span className="text-sm font-bold text-blue-900 block">
                      I confirm I am the parent/guardian
                    </span>
                    <span className="text-xs font-medium text-slate-600">
                      I consent to medical treatment for this minor.
                    </span>
                  </div>
                </label>
                {errors.parent_consent && (
                  <p className="text-red-600 text-xs font-bold">
                    {errors.parent_consent}
                  </p>
                )}
              </div>
            )}
          </fieldset>

          {/* ── Contact Details (editable for returning) ─────────────────── */}
          <fieldset className="space-y-6 pb-8 border-b border-gray-100">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2">
              <Phone size={20} className="text-green-600" /> Contact Details
            </legend>
            {mode === "returning" && (
              <p className="text-xs font-bold text-emerald-600 mb-4 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100">
                You may update the patient's contact information below if
                needed.
              </p>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="(555) 000-0000"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium bg-white text-black border-gray-300 placeholder-gray-500 ${errors.phone ? "border-red-500" : ""}`}
                />
                {errors.phone && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.phone}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="patient@example.com"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium bg-white text-black border-gray-300 placeholder-gray-500 ${errors.email ? "border-red-500" : ""}`}
                />
                {errors.email && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.email}
                  </p>
                )}
                {errors.contact && (
                  <p className="text-red-600 text-xs font-bold mt-1">
                    {errors.contact}
                  </p>
                )}
              </div>
            </div>
          </fieldset>

          {/* ── Reason of Visit (REQUIRED) ───────────────────────────────── */}
          <fieldset className="space-y-6 pb-8 border-b border-gray-100">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2">
              <ClipboardList size={20} className="text-purple-600" /> Reason of
              Visit *
            </legend>
            <div className="space-y-2">
              <textarea
                name="reason_of_visit"
                id="reason_of_visit"
                rows={3}
                required
                value={formData.reason_of_visit}
                onChange={handleChange}
                placeholder="E.g., Routine check-up, Toothache in lower left molar, Crown follow-up..."
                className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition-all text-sm font-medium resize-none bg-white text-black border-gray-300 placeholder-gray-500 ${errors.reason_of_visit ? "border-red-500" : ""}`}
              />
              {errors.reason_of_visit && (
                <p className="text-red-600 text-xs font-bold mt-1">
                  {errors.reason_of_visit}
                </p>
              )}
            </div>
          </fieldset>

          {/* ── Emergency & Medical (only for new patients) ──────────────── */}
          {mode === "new" && (
            <fieldset className="space-y-6 pb-4">
              <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2">
                <HeartPulse size={20} className="text-red-500" /> Emergency &
                Medical
              </legend>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-700">
                    Emergency Contact Name
                  </label>
                  <input
                    type="text"
                    name="emergency_contact_name"
                    value={formData.emergency_contact_name}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white text-black placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-700">
                    Emergency Contact Phone
                  </label>
                  <input
                    type="tel"
                    name="emergency_contact_phone"
                    value={formData.emergency_contact_phone}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white text-black placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div className="space-y-2 col-span-1 md:col-span-2">
                  <label className="text-sm font-semibold text-slate-700">
                    Known Allergies
                  </label>
                  <input
                    type="text"
                    name="allergies"
                    placeholder="e.g. Penicillin, Latex (leave blank if none)"
                    value={formData.allergies}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white text-black placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
            </fieldset>
          )}

          {/* ── Submit ───────────────────────────────────────────────────── */}
          <div className="pt-6 border-t border-slate-100 flex gap-4">
            <button
              type="submit"
              id="intake-continue-review"
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-md flex items-center justify-center gap-2"
            >
              Continue to Review <ArrowRight size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
