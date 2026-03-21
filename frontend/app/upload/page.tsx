"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { uploadImage } from "@/lib/api";
import { useAuth } from "@/app/providers";

export default function UploadPage() {
  const { isAuthenticated } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [result, setResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError("");
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

    try {
      const response = await uploadImage(file);
      setSuccess("Image uploaded and analyzed successfully!");
      setResult(response);
      setFile(null);
      setPreview("");
    } catch (err: any) {
      setError(err.message || "Failed to upload image");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <h1 className="text-3xl font-bold text-gray-900">Upload Image</h1>
          <p className="mt-2 text-gray-600">
            Upload a dental image for AI analysis
          </p>

          <form onSubmit={handleUpload} className="mt-8 space-y-6">
            <div
              className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center hover:border-indigo-400 transition cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
              {preview ? (
                <div>
                  <img
                    src={preview}
                    alt="Preview"
                    className="mx-auto max-h-64 rounded-lg mb-4"
                  />
                  <p className="text-sm text-gray-600">{file?.name}</p>
                </div>
              ) : (
                <div>
                  <div className="text-4xl mb-2">📸</div>
                  <p className="text-gray-700 font-medium">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    PNG, JPG, GIF up to 50MB
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-lg bg-green-50 p-4 text-green-700 border border-green-200">
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={!file || loading}
              className="w-full rounded-lg bg-indigo-600 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {loading ? "Uploading..." : "Upload & Analyze"}
            </button>
          </form>

          {result && (
            <div className="mt-8 border-t pt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Analysis Results
              </h2>
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-auto">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
