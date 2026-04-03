"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import StepNavigation from "@/components/clinical/StepNavigation";
import { getAnalysisResults } from "@/lib/api";
import { useAuth } from "@/app/providers";
import { useQueueStatus } from "@/lib/hooks/useQueueStatus";
import {
  ArrowLeft,
  FileText,
  Filter,
  Search,
  Download,
  Share2,
  Eye,
  BarChart2,
  Calendar,
  Layers,
  Activity,
} from "lucide-react";

export default function ResultsPage() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const router = useRouter();
  const patientId = params?.id as string;
  const {
    markAsComplete,
    queueId,
    error: queueError,
    setError: setQueueError,
  } = useQueueStatus(patientId);

  const [results, setResults] = useState<any[]>([]);
  const [filteredResults, setFilteredResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [completingWorkflow, setCompletingWorkflow] = useState(false);
  const [workflowCompleted, setWorkflowCompleted] = useState(false);
  const [workflowError, setWorkflowError] = useState("");

  // Filters
  const [filterType, setFilterType] = useState("All");
  const [minConfidence, setMinConfidence] = useState("Any");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getAnalysisResults(patientId);
        const resultsArray = Array.isArray(data) ? data : [];

        setResults(resultsArray);
        setFilteredResults(resultsArray);
      } catch (err: any) {
        setError(err.message || "Failed to load image analysis results");
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated && patientId) fetchResults();
  }, [isAuthenticated, patientId]);

  useEffect(() => {
    let filtered = [...results];

    if (filterType !== "All") {
      filtered = filtered.filter((r) => r.analysis_type === filterType);
    }

    if (minConfidence !== "Any") {
      const min = parseFloat(minConfidence) / 100;
      filtered = filtered.filter((r) => r.confidence >= min);
    }

    // Patient filter
    if (patientId) {
      filtered = filtered.filter((r) => r.patient_id === patientId);
    }

    setFilteredResults(filtered);
  }, [filterType, minConfidence, results, patientId]);

  const handleCompleteWorkflow = async () => {
    // Check if queueId is available
    if (!queueId) {
      setWorkflowError(
        "Patient not found in queue. Please ensure patient was properly checked in.",
      );
      console.error(
        "[ResultsPage] Cannot complete workflow: queueId is missing",
      );
      return;
    }

    setCompletingWorkflow(true);
    setWorkflowError("");
    try {
      const success = await markAsComplete();
      if (success) {
        setWorkflowCompleted(true);
        setTimeout(() => {
          router.push("/dashboard/patients");
        }, 2000);
      } else {
        setWorkflowError(
          queueError || "Failed to complete workflow. Please try again.",
        );
        console.error("[ResultsPage] markAsComplete returned false", {
          queueError,
        });
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      setWorkflowError(`Error: ${errorMsg}`);
      console.error("[ResultsPage] Exception completing workflow:", err);
    } finally {
      setCompletingWorkflow(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <Link
              href={`/dashboard/patients/${patientId}`}
              className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center mb-4"
            >
              <ArrowLeft size={20} className="mr-1" /> Back to Patient Profile
            </Link>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <FileText className="text-indigo-600" /> Analysis Reports
              </h1>
            </div>
            <p className="text-gray-600 mt-1 font-medium">
              Review and manage structured AI diagnostic results.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Filter Bar */}
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Layers size={12} /> Analysis Type
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 font-bold"
              >
                <option value="All">All Categories</option>
                <option value="Periapical Lesion">Periapical Lesion</option>
                <option value="Caries Detection">Caries Detection</option>
              </select>
            </div>

            <div className="flex-1 w-full">
              <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Activity size={12} /> Min Confidence
              </label>
              <select
                value={minConfidence}
                onChange={(e) => setMinConfidence(e.target.value)}
                className="w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5 font-bold"
              >
                <option value="Any">Any Confidence</option>
                <option value="75">75%+</option>
                <option value="85">85%+</option>
                <option value="95">95%+</option>
              </select>
            </div>

            <div className="flex-1 w-full sm:w-auto">
              <button className="w-full bg-indigo-600 text-white font-bold rounded-lg px-6 py-2.5 hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-sm">
                <Filter size={16} /> Filter Results
              </button>
            </div>
          </div>

          {/* Content Area */}
          <div className="p-6">
            {loading && (
              <div className="space-y-4">
                <div className="h-40 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
                <div className="h-40 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
              </div>
            )}

            {error && (
              <div className="rounded-lg bg-red-50 p-4 font-bold text-red-700 border border-red-200">
                Connection Error: {error}
              </div>
            )}

            {!loading && !error && filteredResults.length === 0 && (
              <div className="text-center py-16 px-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4 text-gray-400">
                  <BarChart2 size={32} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  No results found
                </h3>
                <p className="text-gray-500 font-medium mb-6 max-w-sm mx-auto">
                  There are no analysis records matching your criteria. Try
                  adjusting your filters or upload a new scan.
                </p>
                <Link
                  href="/dashboard/upload"
                  className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 outline-none rounded-lg font-bold hover:bg-indigo-700 transition shadow-sm"
                >
                  Upload Scan
                </Link>
              </div>
            )}

            {!loading && filteredResults.length > 0 && (
              <div className="space-y-4">
                {filteredResults.map((result, index) => (
                  <div
                    key={index}
                    className={`border-l-4 rounded-xl p-5 hover:shadow-md transition bg-white border border-gray-200 ${
                      result.severity === "critical"
                        ? "border-l-red-500"
                        : result.severity === "high"
                          ? "border-l-orange-500"
                          : "border-l-blue-500"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-lg font-black text-gray-900 uppercase">
                            {result.analysis_type}
                          </h3>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              result.severity === "critical"
                                ? "bg-red-100 text-red-700"
                                : result.severity === "high"
                                  ? "bg-orange-100 text-orange-700"
                                  : "bg-blue-100 text-blue-700"
                            }`}
                          >
                            {result.severity} Risk
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-500 mt-2">
                          <span className="flex items-center gap-1 bg-gray-50 px-2 py-1 rounded border border-gray-200 shadow-sm text-gray-800">
                            <strong>ID:</strong> {result.patient_name}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar size={14} />{" "}
                            {new Date(result.timestamp).toLocaleDateString()} at{" "}
                            {new Date(result.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1">
                          Model Confidence
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500 rounded-full"
                              style={{ width: `${result.confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-lg font-black text-green-700">
                            {(result.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-5 p-4 bg-gray-50 rounded-lg border border-gray-100">
                      <p className="text-sm font-medium text-gray-700">
                        <strong className="text-gray-900 mr-2 uppercase text-[11px] tracking-wider">
                          Primary Findings:
                        </strong>
                        {result.diagnosis ||
                          "No specific anomalies detected beyond baseline."}
                      </p>
                    </div>

                    <div className="mt-5 flex flex-wrap gap-3">
                      <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                        <Eye size={16} /> View Details
                      </button>
                      <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                        <Share2 size={16} /> Share
                      </button>
                      <button className="px-5 py-2 bg-white border border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 text-sm flex items-center gap-2 transition shadow-sm">
                        <Download size={16} /> Report
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-8 px-6 pb-6 space-y-4">
            {workflowCompleted ? (
              <div className="p-6 bg-green-50 border-2 border-green-300 rounded-xl text-center">
                <h3 className="text-lg font-bold text-green-700 mb-2">
                  ✓ Workflow Complete!
                </h3>
                <p className="text-green-600 text-sm">
                  Patient has been removed from the queue.
                </p>
              </div>
            ) : (
              <>
                {workflowError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 font-medium text-sm">
                      {workflowError}
                    </p>
                    {!queueId && (
                      <button
                        onClick={() => window.location.reload()}
                        className="mt-2 text-red-600 hover:text-red-800 underline text-sm font-medium"
                      >
                        Reload page
                      </button>
                    )}
                  </div>
                )}
                {queueError && (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-yellow-700 font-medium text-sm">
                      Queue Status: {queueError}
                    </p>
                  </div>
                )}
                <button
                  onClick={handleCompleteWorkflow}
                  disabled={completingWorkflow || !queueId}
                  className="w-full px-6 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  title={
                    !queueId
                      ? "Queue ID not found. Patient may not be checked in."
                      : "Complete this patient's workflow"
                  }
                >
                  {completingWorkflow ? "Completing..." : "✓ Complete Workflow"}
                </button>
                <StepNavigation patientId={patientId} currentStep="results" />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
