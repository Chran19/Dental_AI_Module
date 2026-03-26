"use client";

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="relative inline-flex">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"></div>
        <span className="ml-3 text-slate-600">Loading...</span>
      </div>
    </div>
  );
}

export function LoadingOverlay() {
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-white border-t-transparent"></div>
    </div>
  );
}
