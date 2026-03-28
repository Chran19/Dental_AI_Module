"use client";

import Link from "next/link";
import { useAuth } from "@/app/providers";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
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
        <div className="mt-8 rounded-lg bg-white p-8 shadow-lg space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="mt-2 text-gray-600">
              Configure system settings and preferences
            </p>
          </div>

          <div className="border-t pt-6 space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Application Settings
              </h2>
              <div className="mt-4 space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span className="text-gray-900 font-medium">
                    Enable notifications
                  </span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span className="text-gray-900 font-medium">Dark mode</span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span className="text-gray-900 font-medium">
                    Auto-save clinical notes
                  </span>
                </label>
              </div>
            </div>
          </div>

          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              API Configuration
            </h2>
            <div className="space-y-3 text-sm text-gray-600">
              <div>
                <p className="font-medium text-gray-900">Backend URL</p>
                <p>
                  {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900">Status</p>
                <p className="text-green-600">✓ Connected</p>
              </div>
            </div>
          </div>

          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Account
            </h2>
            <button
              onClick={handleLogout}
              className="w-full rounded-lg bg-red-600 py-3 font-semibold text-white hover:bg-red-700 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
