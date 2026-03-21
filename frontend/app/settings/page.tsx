"use client";

import Link from "next/link";

export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="mx-auto max-w-2xl py-12">
        <Link
          href="/dashboard"
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg">
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-4 text-gray-600">
            Configure system settings and preferences
          </p>
        </div>
      </div>
    </div>
  );
}
