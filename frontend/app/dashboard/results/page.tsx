"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAnalysisResults } from "@/lib/api";
import { useAuth } from "@/app/providers";

export default function ResultsPage() {
  const { isAuthenticated } = useAuth();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getAnalysisResults();
        setResults(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) fetchResults();
  }, [isAuthenticated]);

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
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="mt-2 text-gray-700 font-medium">
            View all analysis results and reports
          </p>

          {loading && (
            <p className="mt-6 text-gray-700 font-medium">Loading results...</p>
          )}

          {error && (
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
              {error}
            </div>
          )}

          {!loading && results.length === 0 && (
            <p className="mt-6 text-gray-700 font-medium">
              No results yet. Upload an image to get started.
            </p>
          )}

          {!loading && results.length > 0 && (
            <div className="mt-6 space-y-4">
              {results.map((result, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gray-50">
                  <h3 className="font-semibold text-gray-900">
                    Result {index + 1}
                  </h3>
                  <pre className="mt-2 text-sm text-gray-700 whitespace-pre-wrap overflow-auto max-h-64">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
