"use client";

import React, { useState } from "react";
import Odontogram from "@/components/clinical/odontogram/Odontogram";
import ImageUploader from "@/components/diagnostics/ImageUploader";
import { uploadImage, saveVisitData } from "@/lib/api";
import {
  Stethoscope,
  ArrowLeft,
  Camera,
  BrainCircuit,
  Save,
  History,
  AlertTriangle,
  FileText,
  User,
  Activity,
} from "lucide-react";
import Link from "next/link";

export default function ActiveConsultationPage() {
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);

  // Clinical State
  const [symptoms, setSymptoms] = useState("");
  const [painLevel, setPainLevel] = useState("None");
  const [mobility, setMobility] = useState("Grade 0");
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Mock tooth status
  const [toothStatus, setToothStatus] = useState<Record<number, string>>({
    16: "decayed",
    21: "filled",
    34: "missing",
    35: "missing",
  });

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      // In a real app, upload each file and get URL/ID back
      // For now, we simulate processing
      for (const file of files) {
        await uploadImage(file);
      }
      setUploadedImages((prev) => [...prev, ...files]);
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to analyze one or more images");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSaveVisit = async () => {
    setIsSaving(true);
    try {
      // In a real scenario, we would have a visit ID via params or context
      const visitId = "current-visit-id";

      await saveVisitData(visitId, {
        symptoms,
        toothStatus,
        painLevel,
        mobility,
        images: uploadedImages.map((f) => f.name),
      });

      alert("Clinical data saved successfully!");
      // Here you might redirect to dashboard or clear state
    } catch (error) {
      console.error("Save failed", error);
      alert("Failed to save visit data");
    } finally {
      setIsSaving(false);
    }
    alert("Visit data saved successfully! (Simulated)");
  };

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto">
      {/* Header Consultation Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 text-white p-6 rounded-3xl shadow-xl shadow-slate-200">
        <div className="flex items-center gap-5">
          <Link
            href="/dashboard/doctor"
            className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-2xl transition-all"
          >
            <ArrowLeft size={20} />
          </Link>
          <div className="h-14 w-14 rounded-3xl bg-blue-600 flex items-center justify-center font-bold text-xl shadow-lg border-2 border-white/20">
            AS
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black tracking-tight">Alice Smith</h1>
              <span className="text-[10px] bg-red-600 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest shadow-sm">
                High Risk
              </span>
            </div>
            <div className="flex items-center gap-4 mt-1 text-xs text-white/60 font-medium">
              <span className="flex items-center gap-1">
                <User size={12} className="text-blue-400" /> 34Y | Female
              </span>
              <span className="flex items-center gap-1">
                <Activity size={12} className="text-green-400" /> Session: #6219
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 rounded-2xl font-bold text-sm transition-all border border-white/10">
            <History size={18} />
            <span>History</span>
          </button>
          <button
            onClick={handleSaveVisit}
            disabled={isSaving}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl font-bold text-sm transition-all shadow-lg shadow-blue-900/50"
          >
            {isSaving ? (
              <Activity className="animate-spin" size={18} />
            ) : (
              <Save size={18} />
            )}
            <span>{isSaving ? "Saving..." : "End Visit"}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column - Main Clinical Area */}
        <div className="lg:col-span-8 space-y-6">
          {/* Main Odontogram Card */}
          <Odontogram
            initialStatus={toothStatus}
            onSelect={(num) => setSelectedTooth(num)}
          />

          {/* Clinical Findings & Symptoms */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2 mb-4">
                <FileText size={16} className="text-blue-500" />
                Clinical Notes
              </h3>

              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase">
                    Pain Level
                  </span>
                  <select
                    value={painLevel}
                    onChange={(e) => setPainLevel(e.target.value)}
                    className="text-sm font-bold text-slate-900 bg-transparent outline-none text-right cursor-pointer hover:text-blue-600"
                  >
                    <option value="None">None</option>
                    <option value="Mild">Mild</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Severe">Severe</option>
                  </select>
                </div>

                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase">
                    Mobility
                  </span>
                  <select
                    value={mobility}
                    onChange={(e) => setMobility(e.target.value)}
                    className="text-sm font-bold text-slate-900 bg-transparent outline-none text-right cursor-pointer hover:text-blue-600"
                  >
                    <option value="Grade 0">Grade 0</option>
                    <option value="Grade 1">Grade 1</option>
                    <option value="Grade 2">Grade 2</option>
                    <option value="Grade 3">Grade 3</option>
                  </select>
                </div>

                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  className="w-full h-24 p-4 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-400"
                  placeholder="Record clinical observations for the selected tooth..."
                ></textarea>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden group">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2 mb-4">
              <Camera size={16} className="text-blue-500" />
              Diagnostic Studio
            </h3>

            <ImageUploader onUpload={handleUpload} isUploading={isUploading} />

            {uploadedImages.length > 0 && (
              <div className="mt-4 grid grid-cols-3 gap-2">
                {uploadedImages.map((file, idx) => (
                  <div
                    key={idx}
                    className="relative aspect-square rounded-lg overflow-hidden border border-slate-200 group"
                  >
                    <img
                      src={URL.createObjectURL(file)}
                      alt="preview"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <span className="text-xs text-white font-medium truncat px-2">
                        {file.name}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - AI Intelligence */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 p-6 rounded-3xl text-white shadow-xl shadow-indigo-100 border border-white/5">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold uppercase tracking-widest flex items-center gap-2 text-indigo-200">
                <BrainCircuit size={18} />
                ChairSide AI
              </h3>
              <span className="text-[10px] bg-green-500/20 text-green-400 border border-green-500/30 px-2 py-0.5 rounded-full font-bold">
                READY
              </span>
            </div>

            {selectedTooth ? (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2">
                <div className="p-4 bg-white/5 border border-white/10 rounded-2xl">
                  <p className="text-[10px] text-white/50 uppercase font-black tracking-widest">
                    Selected Tooth
                  </p>
                  <p className="text-2xl font-black text-white mt-1">
                    Tooth #{selectedTooth}
                  </p>
                </div>

                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle size={14} className="text-red-400" />
                    <p className="text-xs font-bold text-red-200">
                      Probable Finding
                    </p>
                  </div>
                  <p className="text-sm text-red-50 font-medium">
                    Distal Occlusal Caries detected from recent bitewing
                  </p>
                </div>

                <div className="space-y-3 pt-2">
                  <p className="text-[10px] text-white/50 uppercase font-black tracking-widest">
                    Recommended Actions
                  </p>
                  <AIActionItem label="Class II Composite" confidence="92%" />
                  <AIActionItem label="Local Anesthesia" confidence="100%" />
                </div>
              </div>
            ) : (
              <div className="py-12 text-center">
                <BrainCircuit
                  size={48}
                  className="mx-auto text-white/10 mb-4 animate-pulse"
                />
                <p className="text-sm text-white/40 font-medium px-8 leading-relaxed">
                  Select a tooth to activate real-time AI cross-referencing and
                  3D diagnostics.
                </p>
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm shadow-slate-100">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
              Patient Alerts
            </h3>
            <div className="space-y-3">
              <AlertItem
                label="Penicillin Allergy"
                color="text-red-600 bg-red-50 border-red-100"
              />
              <AlertItem
                label="Type 2 Diabetes"
                color="text-orange-600 bg-orange-50 border-orange-100"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InputGroup({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
      <span className="text-xs font-bold text-slate-500 uppercase">
        {label}
      </span>
      <span className="text-sm font-bold text-slate-900">{value}</span>
    </div>
  );
}

function AIActionItem({
  label,
  confidence,
}: {
  label: string;
  confidence: string;
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors cursor-pointer group">
      <span className="text-xs font-bold text-blue-200 group-hover:text-white transition-colors">
        {label}
      </span>
      <span className="text-[10px] bg-blue-500 text-white font-black px-2 py-0.5 rounded-full">
        {confidence}
      </span>
    </div>
  );
}

function AlertItem({ label, color }: { label: string; color: string }) {
  return (
    <div
      className={`px-4 py-2 rounded-xl border text-[11px] font-bold shadow-sm ${color}`}
    >
      {label}
    </div>
  );
}
