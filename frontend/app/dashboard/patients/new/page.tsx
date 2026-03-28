"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchAPI } from "@/lib/api";
import { PatientCreate } from "@/lib/types/patient";
import {
  UserPlus,
  ArrowLeft,
  Loader2,
  CheckCircle2,
  AlertCircle,
  User,
  Mail,
  Phone,
  Calendar,
  Layers,
  HeartPulse,
} from "lucide-react";
import Link from "next/link";

export default function PatientIntakePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [createdPatientId, setCreatedPatientId] = useState<string>("");

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    date_of_birth: "",
    gender: "",
    gender_self_describe: "",
    pronouns: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    emergency_contact_relationship: "",
    allergies: "",
    parent_guardian_name: "",
    parent_guardian_phone: "",
    parent_consent: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [potentialDuplicates, setPotentialDuplicates] = useState<any[]>([]);
  const [step, setStep] = useState<'form' | 'review' | 'success'>('form');

  // Load draft from local storage
  useEffect(() => {
    const draft = localStorage.getItem("patient_intake_draft");
    if (draft) {
      setFormData(JSON.parse(draft));
    }
  }, []);

  // Save draft to local storage
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem("patient_intake_draft", JSON.stringify(formData));
    }, 1000);
    return () => clearTimeout(timer);
  }, [formData]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    if (name === "phone" || name === "emergency_contact_phone" || name === "parent_guardian_phone") {
      // Basic formatting for phone
      const cleaned = value.replace(/\D/g, '');
      let formatted = value;
      if (cleaned.length >= 10) {
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        if (match) formatted = `(${match[1]}) ${match[2]}-${match[3]}`;
      }
      setFormData((prev) => ({ ...prev, [name]: formatted }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }

    // Duplicate check simulator on name input blur
    if (name === "last_name" && formData.first_name.length > 2 && value.length > 2) {
      if (formData.first_name.toLowerCase() === "john" && value.toLowerCase() === "doe") {
        setPotentialDuplicates([
          { id: "P-123", first_name: "John", last_name: "Doe", date_of_birth: "1980-01-01" }
        ]);
      } else {
        setPotentialDuplicates([]);
      }
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
    if (!formData.first_name.trim()) newErrors.first_name = "First name is required";
    if (!formData.last_name.trim()) newErrors.last_name = "Last name is required";
    
    if (!formData.email && !formData.phone) {
      newErrors.contact = "Please provide either email or phone number";
      newErrors.email = "Required if phone is empty";
      newErrors.phone = "Required if email is empty";
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    if (isMinor && !formData.parent_guardian_name) {
      newErrors.parent_guardian_name = "Required for minors";
    }
    if (isMinor && !formData.parent_consent) {
      newErrors.parent_consent = "Parent consent is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleReviewPhase = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (validateForm()) {
      setStep('review');
    }
  };

  const submitFinal = async () => {
    setIsSubmitting(true);
    setError(null);

    const submissionData = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
      phone: formData.phone,
      date_of_birth: formData.date_of_birth,
      gender: formData.gender === "Prefer to self-describe" ? formData.gender_self_describe : formData.gender,
    };

    try {
      const result = await fetchAPI("/patients", {
        method: "POST",
        body: JSON.stringify(submissionData),
        headers: { "Content-Type": "application/json" },
      });

      setCreatedPatientId(result.id || "NEW-ID");
      localStorage.removeItem("patient_intake_draft");
      setStep('success');
      
      setTimeout(() => {
        router.push(`/dashboard/patients/${result.id || ""}`);
      }, 5000);
    } catch (err: any) {
      setError(err.message || "Failed to register patient");
      setIsSubmitting(false);
      setStep('form');
    }
  };

  if (step === 'success') {
    return (
      <div className="max-w-md mx-auto mt-20 text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-2">
          <CheckCircle2 size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">
          Patient Registered!
        </h2>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-left space-y-2 text-slate-800">
          <p className="text-sm">
            <strong>Name:</strong> {formData.first_name} {formData.last_name}
          </p>
          <p className="text-sm">
            <strong>Patient ID:</strong> {createdPatientId}
          </p>
          <p className="text-sm text-gray-600">
            You can now assign them to queue or view their record.
          </p>
        </div>
        <p className="text-slate-500 text-sm">Redirecting in 5 seconds...</p>
        <div className="flex gap-2 pt-4">
          <Link
            href="/dashboard/patients"
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700"
          >
            Back to Patients
          </Link>
          <Link
            href={`/dashboard/patients/${createdPatientId}`}
            className="flex-1 px-4 py-2 border border-green-600 text-green-600 rounded-lg font-bold hover:bg-green-50"
          >
            View Profile
          </Link>
        </div>
      </div>
    );
  }

  if (step === 'review') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200 shadow-sm">
          <h2 className="text-xl font-bold text-blue-900 mb-6 flex items-center gap-2">
            <UserPlus size={24} /> Confirm Patient Registration
          </h2>
          <div className="grid grid-cols-2 gap-6 text-sm">
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Name</p>
              <p className="font-bold text-gray-900 text-base">{formData.first_name} {formData.last_name}</p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Date of Birth</p>
              <p className="font-bold text-gray-900 text-base">{formData.date_of_birth} {age !== null && `(${age} years old)`}</p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Phone</p>
              <p className="font-bold text-gray-900">{formData.phone || "N/A"}</p>
            </div>
            <div>
              <p className="text-gray-500 font-medium tracking-wide">Email</p>
              <p className="font-bold text-gray-900">{formData.email || "N/A"}</p>
            </div>
            {isMinor && (
              <div className="col-span-2 mt-4 bg-orange-50 p-3 rounded border border-orange-200">
                <p className="font-bold text-orange-900 mb-1">Guardian Information (Minor)</p>
                <p className="text-orange-800">Name: {formData.parent_guardian_name}</p>
                <p className="text-orange-800">Phone: {formData.parent_guardian_phone}</p>
                <p className="text-orange-800 font-semibold mt-1 flex items-center gap-1">
                  <CheckCircle2 size={16} /> Consent Provided
                </p>
              </div>
            )}
          </div>
          <div className="mt-8 flex gap-4">
            <button
              onClick={() => setStep('form')}
              className="flex-1 px-4 py-3 border border-blue-300 text-blue-700 rounded-lg font-bold hover:bg-blue-100 transition"
            >
              ← Edit Details
            </button>
            <button
              onClick={submitFinal}
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? <><Loader2 className="animate-spin" size={20} /> Registering...</> : "Confirm & Register"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/dashboard/patients"
          className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors font-medium "
        >
          <ArrowLeft size={18} /> Back to Records
        </Link>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <UserPlus className="text-blue-600" size={28} />
            Patient Intake Form
          </h1>
          <p className="text-slate-500 text-sm mt-1 font-medium">
            Register a new patient into the system securely.
          </p>
        </div>

        <form onSubmit={handleReviewPhase} className="p-8 space-y-8">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-3 font-medium">
              <AlertCircle size={20} className="flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {potentialDuplicates.length > 0 && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg shadow-sm">
              <p className="text-sm font-bold text-yellow-900 mb-3 flex items-center gap-2">
                <AlertCircle size={18} /> Similar patient(s) found in system:
              </p>
              <ul className="space-y-2 mb-3">
                {potentialDuplicates.map(dup => (
                  <li key={dup.id} className="text-sm flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => router.push(`/dashboard/patients/${dup.id}`)}
                      className="text-yellow-700 font-bold hover:underline"
                    >
                      {dup.first_name} {dup.last_name} (DOB: {dup.date_of_birth})
                    </button>
                    <span className="text-yellow-600">—</span>
                    <button
                      type="button"
                      onClick={() => setPotentialDuplicates([])}
                      className="text-xs font-bold px-2 py-1 bg-white border border-yellow-300 text-yellow-700 rounded hover:bg-yellow-100"
                    >
                      Not this person
                    </button>
                  </li>
                ))}
              </ul>
              <p className="text-xs text-yellow-800 font-medium opacity-80 mt-1">
                If you are sure this is a new patient, you may continue registering.
              </p>
            </div>
          )}

          <fieldset className="space-y-6 pb-8 border-b border-gray-100">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2"><User size={20} className="text-blue-500" /> Basic Information</legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="first_name" className="text-sm font-semibold text-slate-700">First Name *</label>
                <input
                  id="first_name" name="first_name" type="text"
                  required
                  value={formData.first_name} onChange={handleChange}
                  aria-invalid={!!errors.first_name}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${errors.first_name ? 'border-red-500' : 'border-slate-300'}`}
                />
                {errors.first_name && <p className="text-red-600 text-xs font-bold mt-1">{errors.first_name}</p>}
              </div>
              <div className="space-y-2">
                <label htmlFor="last_name" className="text-sm font-semibold text-slate-700">Last Name *</label>
                <input
                  id="last_name" name="last_name" type="text"
                  required
                  value={formData.last_name} onChange={handleChange}
                  aria-invalid={!!errors.last_name}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${errors.last_name ? 'border-red-500' : 'border-slate-300'}`}
                />
                {errors.last_name && <p className="text-red-600 text-xs font-bold mt-1">{errors.last_name}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Date of Birth *</label>
                <input
                  type="date" name="date_of_birth"
                  required autoComplete="bday"
                  value={formData.date_of_birth} onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium"
                />
                {age !== null && (
                  <p className="text-xs font-bold text-blue-600 mt-1">Calculated Age: {age} years old</p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Gender Identity</label>
                <select
                  name="gender" value={formData.gender} onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium bg-white"
                >
                  <option value="">Select...</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Non-binary">Non-binary</option>
                  <option value="Prefer to self-describe">Prefer to self-describe</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
                {formData.gender === "Prefer to self-describe" && (
                  <input
                    type="text" name="gender_self_describe" placeholder="How do you identify?"
                    value={formData.gender_self_describe} onChange={handleChange}
                    className="w-full mt-2 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm font-medium"
                  />
                )}
              </div>
            </div>
            {isMinor && (
              <div className="bg-blue-50 border border-blue-200 p-5 rounded-xl space-y-4 shadow-sm mt-6">
                <h3 className="font-bold text-blue-900 text-base">Parent/Guardian Information (Required for Minors)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-slate-700">Guardian Full Name *</label>
                    <input
                      name="parent_guardian_name" type="text"
                      value={formData.parent_guardian_name} onChange={handleChange}
                      className={`w-full px-4 py-2 border rounded-lg text-sm font-medium ${errors.parent_guardian_name ? 'border-red-500' : 'border-slate-300'}`}
                    />
                    {errors.parent_guardian_name && <p className="text-red-600 text-xs font-bold">{errors.parent_guardian_name}</p>}
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-slate-700">Guardian Phone</label>
                    <input
                      name="parent_guardian_phone" type="tel" inputMode="tel"
                      value={formData.parent_guardian_phone} onChange={handleChange}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium"
                    />
                  </div>
                </div>
                <label className="flex items-start gap-3 mt-4 p-3 bg-white border border-blue-100 rounded-lg cursor-pointer">
                  <input
                    name="parent_consent" type="checkbox"
                    checked={formData.parent_consent} onChange={handleChange}
                    className={`mt-1 w-5 h-5 rounded ${errors.parent_consent ? 'border-red-500' : ''}`}
                  />
                  <div>
                    <span className="text-sm font-bold text-blue-900 block">I confirm I am the parent/guardian </span>
                    <span className="text-xs font-medium text-slate-600">I consent to medical treatment for this minor.</span>
                  </div>
                </label>
                {errors.parent_consent && <p className="text-red-600 text-xs font-bold">{errors.parent_consent}</p>}
              </div>
            )}
          </fieldset>

          <fieldset className="space-y-6 pb-8 border-b border-gray-100">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2"><Phone size={20} className="text-green-600" /> Contact Details</legend>
            <p className="text-xs font-bold text-slate-500 mb-4 uppercase tracking-wider">Please provide at least one contact method</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Phone Number</label>
                <input
                  type="tel" name="phone" inputMode="tel" autoComplete="tel"
                  value={formData.phone} onChange={handleChange}
                  placeholder="(555) 000-0000"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${errors.phone ? 'border-red-500' : 'border-slate-300'}`}
                />
                {errors.phone && <p className="text-red-600 text-xs font-bold mt-1">{errors.phone}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Email Address</label>
                <input
                  type="email" name="email" inputMode="email" autoComplete="email"
                  value={formData.email} onChange={handleChange}
                  placeholder="patient@example.com"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm font-medium ${errors.email ? 'border-red-500' : 'border-slate-300'}`}
                />
                {errors.email && <p className="text-red-600 text-xs font-bold mt-1">{errors.email}</p>}
                {errors.contact && <p className="text-red-600 text-xs font-bold mt-1">{errors.contact}</p>}
              </div>
            </div>
          </fieldset>
          
          <fieldset className="space-y-6 pb-4">
            <legend className="text-lg font-bold text-slate-900 mb-4 tracking-tight flex items-center gap-2"><HeartPulse size={20} className="text-red-500" /> Emergency & Medical</legend>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Emergency Contact Name</label>
                <input
                  type="text" name="emergency_contact_name"
                  value={formData.emergency_contact_name} onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Emergency Contact Phone</label>
                <input
                  type="tel" name="emergency_contact_phone" inputMode="tel"
                  value={formData.emergency_contact_phone} onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
              <div className="space-y-2 col-span-1 md:col-span-2">
                <label className="text-sm font-semibold text-slate-700">Known Allergies</label>
                <input
                  type="text" name="allergies" placeholder="e.g. Penicillin, Latex (leave blank if none)"
                  value={formData.allergies} onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>
          </fieldset>

          <div className="pt-6 border-t border-slate-100 flex gap-4">
            <button
              type="submit"
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-md flex items-center justify-center gap-2"
            >
              Continue to Review <ArrowLeft size={18} className="rotate-180" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
