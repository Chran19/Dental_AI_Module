"use client";

import React, { useCallback, useState } from "react";
import { Upload, X, FileImage, AlertCircle, CheckCircle } from "lucide-react";

interface ImageUploaderProps {
  onUpload: (files: File[]) => void;
  isUploading?: boolean;
}

export default function ImageUploader({
  onUpload,
  isUploading = false,
}: ImageUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const validateFile = (file: File) => {
    const validTypes = [
      "image/jpeg",
      "image/png",
      "image/tiff",
      "application/dicom",
    ];
    if (
      !validTypes.some(
        (type) => file.type.includes(type) || file.name.endsWith(".dcm"),
      )
    ) {
      return "Unsupported file format. Please use JPEG, PNG, or DICOM.";
    }
    if (file.size > 10 * 1024 * 1024) {
      return "File size exceeds 10MB limit.";
    }
    return null;
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      setError(null);

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const files = Array.from(e.dataTransfer.files);
        const validFiles: File[] = [];

        for (const file of files) {
          const validationError = validateFile(file);
          if (validationError) {
            setError(validationError);
            return;
          }
          validFiles.push(file);
        }

        if (validFiles.length > 0) {
          onUpload(validFiles);
        }
      }
    },
    [onUpload],
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setError(null);
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      const validFiles: File[] = [];

      for (const file of files) {
        const validationError = validateFile(file);
        if (validationError) {
          setError(validationError);
          return;
        }
        validFiles.push(file);
      }

      if (validFiles.length > 0) {
        onUpload(validFiles);
      }
    }
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-slate-200 hover:border-blue-400 bg-slate-50/50"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={handleChange}
          accept="image/jpeg,image/png,image/tiff,.dcm"
          disabled={isUploading}
        />

        <div className="flex flex-col items-center justify-center pointer-events-none">
          {isUploading ? (
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-10 w-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3"></div>
              <p className="text-sm font-bold text-blue-600">
                Uploading & Analyzing...
              </p>
            </div>
          ) : (
            <>
              <div className="h-12 w-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-4">
                <Upload className="text-blue-500" size={24} />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Click or drag to upload X-rays
              </h3>
              <p className="text-xs text-slate-500">
                Supports JPG, PNG, DICOM (Max 10MB)
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 text-red-600 text-xs rounded-lg flex items-center gap-2 font-medium animate-in slide-in-from-top-1">
          <AlertCircle size={14} />
          {error}
        </div>
      )}
    </div>
  );
}
