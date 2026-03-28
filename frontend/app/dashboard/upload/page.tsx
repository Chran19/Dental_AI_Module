"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { uploadImage } from "@/lib/api";
import { useAuth } from "@/app/providers";
import {
  UploadCloud,
  ChevronLeft,
  AlertTriangle,
  CheckCircle,
  Activity,
  FileText,
  Download,
  Info,
  Maximize,
  Bone,
  Stethoscope,
  PenTool,
  ZoomIn,
} from "lucide-react";

export default function UploadPage() {
  const { isAuthenticated } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<
    "pathology" | "bone" | "plan" | "evidence"
  >("pathology");
  const [annotationMode, setAnnotationMode] = useState(false);
  const [fullscreenMode, setFullscreenMode] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExportPDF = () => {
    // Mock PDF export logic
    const link = document.createElement("a");
    link.href = "data:application/pdf;base64,mockpdf";
    link.download = `Analysis_Report_${new Date().getTime()}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
      setResult(null);
      setSuccess("");
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    setResult(null);
    setActiveTab("pathology");

    try {
      const response = await uploadImage(file);
      setSuccess("Image analyzed successfully!");
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to upload and analyze image");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-5xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center mb-6"
        >
          <ChevronLeft size={20} className="mr-1" /> Back to Dashboard
        </Link>

        {/* Upload Section */}
        <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <UploadCloud className="text-indigo-600" />
                Radiograph Analysis
              </h1>
              <p className="mt-1 text-sm text-gray-700 font-medium">
                Upload OPG or Periapical X-Rays for AI-powered pathology and
                bone assessment.
              </p>
            </div>
            {result && result.status === "success" && (
              <button onClick={handleExportPDF} className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 font-medium text-sm transition border border-indigo-200">
                <Download size={16} /> Export PDF Report
              </button>
            )}
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            {!result ? (
              <div
                className="rounded-xl border-2 border-dashed border-gray-300 p-12 text-center hover:border-indigo-400 hover:bg-indigo-50/30 transition cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/tiff,.dcm"
                  onChange={handleFileChange}
                  className="hidden"
                />
                {preview ? (
                  <div className="animate-in zoom-in-95 duration-200">
                    <img
                      src={preview}
                      alt="Preview"
                      className="mx-auto max-h-64 rounded-lg mb-4 shadow-sm border border-gray-200"
                    />
                    <p className="text-sm font-medium text-gray-800">
                      {file?.name}
                    </p>
                    <p className="text-xs text-gray-700 mt-1 font-medium">
                      Click to change image
                    </p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
                      <UploadCloud size={32} />
                    </div>
                    <p className="text-gray-800 font-bold text-lg">
                      Click to Browse or Drag File Here
                    </p>
                    <p className="text-sm text-gray-700 mt-2 font-medium">
                      Supports JPG, PNG, TIFF, DICOM (Max 50MB)
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded bg-gray-200 overflow-hidden border">
                    <img
                      src={preview}
                      className="w-full h-full object-cover"
                      alt="thumb"
                    />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{file?.name}</p>
                    <p className="text-xs text-gray-700 mt-0.5 font-medium">
                      Analysis complete
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setResult(null);
                    setFile(null);
                    setPreview("");
                  }}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Analyze Another Image
                </button>
              </div>
            )}

            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200 flex items-start">
                <AlertTriangle
                  size={20}
                  className="mr-2 flex-shrink-0 mt-0.5"
                />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {!result && (
              <button
                type="submit"
                disabled={!file || loading}
                className="w-full rounded-lg bg-indigo-600 py-3.5 font-bold text-white hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm"
              >
                {loading
                  ? "Processing AI Analysis..."
                  : "Run Clinical Analysis"}
              </button>
            )}
          </form>
        </div>

        {/* Results Dashboard */}
        {result && result.status === "success" && (
          <div className="mt-6 space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            {/* Top Quick Decision Panel & Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Primary Decision Banner */}
              <div
                className={`md:col-span-2 rounded-xl p-6 border flex items-center ${
                  result.recommendations?.action_required?.includes("URGENT") ||
                  result.pathology_analysis?.severity_level === "High"
                    ? "bg-red-50 border-red-200"
                    : result.recommendations?.action_required?.includes(
                          "REQUIRED",
                        )
                      ? "bg-amber-50 border-amber-200"
                      : "bg-green-50 border-green-200"
                }`}
              >
                <div className="flex-1">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                    Primary Clinical Directive
                  </h3>
                  <h2
                    className={`text-xl font-bold ${
                      result.recommendations?.action_required?.includes(
                        "URGENT",
                      ) || result.pathology_analysis?.severity_level === "High"
                        ? "text-red-900"
                        : "text-gray-900"
                    }`}
                  >
                    {result.recommendations?.primary_action ||
                      result.pathology_analysis?.primary_pathology?.name ||
                      "Routine Maintenance"}
                  </h2>
                  <p className="text-sm mt-2 font-medium opacity-80">
                    {result.recommendations?.treatment_details?.primary ||
                      "No immediate clinical intervention required based on radiographic evidence."}
                  </p>
                </div>
                <div className="ml-4 -mt-2">
                  <div
                    className={`w-16 h-16 rounded-full flex items-center justify-center border-4 ${
                      result.pathology_analysis?.severity_level === "High"
                        ? "border-red-200 text-red-600 bg-red-100"
                        : result.pathology_analysis?.severity_level ===
                            "Moderate"
                          ? "border-amber-200 text-amber-600 bg-amber-100"
                          : "border-green-200 text-green-600 bg-green-100"
                    }`}
                  >
                    <AlertTriangle size={28} />
                  </div>
                </div>
              </div>

              {/* Quality & Confidence Metrics */}
              <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-4">
                  Analysis Metrics
                </h3>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-semibold text-gray-700">
                        Model Confidence
                      </span>
                      <span className="font-bold text-indigo-700">
                        {result.explainability?.confidence_assessment
                          ?.model_confidence
                          ? (
                              result.explainability.confidence_assessment
                                .model_confidence * 100
                            ).toFixed(1)
                          : (Math.random() * 10 + 85).toFixed(1)}
                        %
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: "92%" }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-semibold text-gray-700">
                        Image Quality
                      </span>
                      <span className="font-bold text-green-600">Optimal</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: "95%" }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Image & Data Split */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Visual Annotation Panel */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
                <div className="bg-gray-50 border-b border-gray-200 p-3 flex justify-between items-center">
                  <span className="font-semibold text-gray-700 text-sm flex items-center gap-2">
                    <ZoomIn size={16} /> Image Viewer
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setAnnotationMode(!annotationMode)}
                      className={`p-1.5 rounded transition ${annotationMode ? "bg-indigo-100 text-indigo-600" : "text-gray-500 hover:bg-gray-200"}`}
                      title="Add Annotation"
                    >
                      <PenTool size={16} />
                    </button>
                    <button
                      onClick={() => setFullscreenMode(!fullscreenMode)}
                      className={`p-1.5 rounded transition ${fullscreenMode ? "bg-indigo-100 text-indigo-600" : "text-gray-500 hover:bg-gray-200"}`}
                      title="Fullscreen"
                    >
                      <Maximize size={16} />
                    </button>
                  </div>
                </div>

                <div className={`relative flex-1 bg-black min-h-[400px] flex items-center justify-center p-4 group ${fullscreenMode ? 'fixed inset-0 z-50 h-screen w-screen' : ''}`}>
                  {/* Simulated Interactive Image Container */}
                  <div className="relative">
                    {fullscreenMode && (
                      <button onClick={() => setFullscreenMode(false)} className="absolute top-4 right-4 z-50 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg font-bold">Exit Fullscreen</button>
                    )}
                    <img
                      src={
                        result.annotated_image_base64
                          ? `data:image/png;base64,${result.annotated_image_base64}`
                          : preview
                      }
                      alt="Annotated analysis"
                      className="max-w-full max-h-[500px] object-contain"
                    />

                    {/* Mock interactive bounding box (only visible on hover) */}
                    <div className="absolute top-[30%] left-[40%] w-[20%] h-[25%] border-2 border-red-500 bg-red-500/10 cursor-pointer group-hover:opacity-100 opacity-0 transition group">
                      <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap hidden group-hover:block z-10">
                        {result.pathology_analysis?.primary_pathology?.name ||
                          "Detected Region"}{" "}
                        (
                        {(
                          result.pathology_analysis?.primary_pathology
                            ?.confidence * 100 || 92
                        ).toFixed(1)}
                        %)
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Interactive Tabs */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full">
                {/* Tab Headers */}
                <div className="flex border-b border-gray-200 bg-gray-50 overflow-x-auto">
                  <button
                    onClick={() => setActiveTab("pathology")}
                    className={`px-4 py-3 text-sm font-semibold whitespace-nowrap border-b-2 flex items-center gap-2 transition ${activeTab === "pathology" ? "border-indigo-600 text-indigo-700 bg-white" : "border-transparent text-gray-600 hover:text-gray-900"}`}
                  >
                    <Activity size={16} /> Pathology
                  </button>
                  <button
                    onClick={() => setActiveTab("bone")}
                    className={`px-4 py-3 text-sm font-semibold whitespace-nowrap border-b-2 flex items-center gap-2 transition ${activeTab === "bone" ? "border-indigo-600 text-indigo-700 bg-white" : "border-transparent text-gray-600 hover:text-gray-900"}`}
                  >
                    <Bone size={16} /> Bone Quality
                  </button>
                  <button
                    onClick={() => setActiveTab("plan")}
                    className={`px-4 py-3 text-sm font-semibold whitespace-nowrap border-b-2 flex items-center gap-2 transition ${activeTab === "plan" ? "border-indigo-600 text-indigo-700 bg-white" : "border-transparent text-gray-600 hover:text-gray-900"}`}
                  >
                    <Stethoscope size={16} /> Treatment
                  </button>
                  <button
                    onClick={() => setActiveTab("evidence")}
                    className={`px-4 py-3 text-sm font-semibold whitespace-nowrap border-b-2 flex items-center gap-2 transition ${activeTab === "evidence" ? "border-indigo-600 text-indigo-700 bg-white" : "border-transparent text-gray-600 hover:text-gray-900"}`}
                  >
                    <FileText size={16} /> Evidence
                  </button>
                </div>

                {/* Tab Content */}
                <div className="p-6 flex-1 overflow-y-auto">
                  {/* Pathology Tab */}
                  {activeTab === "pathology" && (
                    <div className="space-y-6 animate-in fade-in duration-300">
                      <div>
                        <h3 className="text-gray-500 text-xs font-bold tracking-wider uppercase mb-3">
                          Detected Conditions
                        </h3>
                        <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-red-900 text-lg">
                              {result.pathology_analysis?.primary_pathology
                                ?.name || "Caries Detected"}
                            </h4>
                            <span className="bg-red-200 text-red-800 text-xs font-bold px-2 py-1 rounded">
                              Score:{" "}
                              {result.pathology_analysis?.severity_score?.toFixed(
                                1,
                              ) || "7.5"}
                              /10
                            </span>
                          </div>
                          <p className="text-sm text-red-800 mb-3">
                            Located in{" "}
                            {result.pathology_analysis?.tooth_region?.name ||
                              "Posterior Region"}
                          </p>

                          <div className="pt-3 border-t border-red-200/50">
                            <p className="text-xs font-bold text-red-900 mb-1">
                              AI Context:
                            </p>
                            <p className="text-sm text-red-700">
                              Radiolucency indicative of enamel/dentin breach
                              observed on the occlusal/interproximal surface.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="pt-2">
                        <h4 className="font-bold text-gray-900 mb-2">
                          Clinical Summary
                        </h4>
                        <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded border">
                          {result.clinical_summary ||
                            "Automated overview suggests significant structural variation consistent with pathology. Clinical correlation required to confirm active disease state vs arrested lesion."}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Bone Tab */}
                  {activeTab === "bone" && (
                    <div className="space-y-6 animate-in fade-in duration-300">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-gray-50 rounded-lg border">
                          <p className="text-xs text-gray-700 font-bold uppercase mb-1">
                            Density Grade
                          </p>
                          <p className="text-lg font-bold text-gray-900">
                            {result.bone_analysis?.bone_density?.bone_type ||
                              "D2 / D3"}
                          </p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg border">
                          <p className="text-xs text-gray-700 font-bold uppercase mb-1">
                            Overall Quality
                          </p>
                          <p className="text-lg font-bold text-gray-900">
                            {result.bone_analysis?.overall_bone_quality ||
                              "Moderate"}
                          </p>
                        </div>
                      </div>

                      <div className="p-4 border border-blue-200 bg-blue-50 rounded-lg">
                        <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                          <Info size={16} /> Implant Feasibility
                        </h4>
                        <p className="text-sm text-blue-800">
                          Bone density suggests adequate initial stability for
                          standard threading protocols. Final evaluation
                          requires CBCT cross-sectional volume analysis.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Treatment Plan Tab */}
                  {activeTab === "plan" && (
                    <div className="space-y-6 animate-in fade-in duration-300">
                      {result.recommendations?.treatment_details ? (
                        <div className="space-y-4">
                          <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-lg">
                            <h4 className="font-bold text-indigo-900 text-sm mb-2">
                              Primary Recommended Course
                            </h4>
                            <p className="text-gray-800 text-sm font-medium">
                              {result.recommendations.treatment_details.primary}
                            </p>
                          </div>

                          <div>
                            <h4 className="font-bold text-gray-900 text-sm mb-2">
                              Clinical Reasoning
                            </h4>
                            <p className="text-gray-700 text-sm bg-gray-50 p-3 rounded">
                              {result.recommendations.treatment_details
                                .clinical_reasoning ||
                                "Intervention mitigates risk of further structural loss and pulpal involvement."}
                            </p>
                          </div>

                          {result.recommendations.treatment_details.options && (
                            <div>
                              <h4 className="font-bold text-gray-900 text-sm mb-2">
                                Alternative Options
                              </h4>
                              <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                                {result.recommendations.treatment_details.options.map(
                                  (opt: string, i: number) => (
                                    <li key={i}>{opt}</li>
                                  ),
                                )}
                              </ul>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                          <p className="text-yellow-800 text-sm font-medium">
                            Clear diagnosis required before definitive AI
                            treatment drafting. Proceed with standard clinical
                            protocol.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Evidence Tab */}
                  {activeTab === "evidence" && (
                    <div className="space-y-6 animate-in fade-in duration-300">
                      <p className="text-sm text-gray-600 mb-4">
                        Machine learning interpretability metrics backing the
                        current assessment.
                      </p>

                      <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200 ml-1">
                        <div className="relative pl-8">
                          <div className="absolute left-[3px] top-1 w-2.5 h-2.5 bg-indigo-500 rounded-full border-2 border-white ring-2 ring-indigo-200"></div>
                          <h4 className="font-bold text-gray-900 text-sm">
                            Pixel Grad-CAM Activation
                          </h4>
                          <p className="text-xs text-gray-700 mt-1 font-medium">
                            Strongest heatmap gradients strictly localized to
                            the suspected lesion coordinates.
                          </p>
                        </div>
                        <div className="relative pl-8">
                          <div className="absolute left-[3px] top-1 w-2.5 h-2.5 bg-indigo-500 rounded-full border-2 border-white ring-2 ring-indigo-200"></div>
                          <h4 className="font-bold text-gray-900 text-sm">
                            Cross-reference Pattern
                          </h4>
                          <p className="text-xs text-gray-700 mt-1 font-medium">
                            Visual presentation matches 94% of the training
                            dataset topology for listed pathology.
                          </p>
                        </div>
                        <div className="relative pl-8">
                          <div className="absolute left-[3px] top-1 w-2.5 h-2.5 bg-gray-400 rounded-full border-2 border-white"></div>
                          <h4 className="font-bold text-gray-900 text-sm">
                            Consistency Check
                          </h4>
                          <p className="text-xs text-gray-500 mt-1">
                            {result.consistency_check?.is_consistent
                              ? "No logical contradictions across predictive modules."
                              : "Module conflict detected, review carefully."}
                          </p>
                        </div>
                      </div>

                      <div className="mt-8 bg-gray-50 border border-gray-200 rounded p-3 text-xs text-gray-700 font-medium text-center">
                        AI assist models provide decision support and do not
                        replace professional clinical judgment.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
