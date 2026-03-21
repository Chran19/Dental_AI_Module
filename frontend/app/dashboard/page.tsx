"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/app/providers";
import { useEffect } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, logout, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const dashboardButtons = [
    { label: "Upload Image", icon: "📸", action: () => router.push("/upload") },
    {
      label: "Analysis Results",
      icon: "📊",
      action: () => router.push("/results"),
    },
    {
      label: "Patient Records",
      icon: "👥",
      action: () => router.push("/patients"),
    },
    {
      label: "Clinical Input",
      icon: "📝",
      action: () => router.push("/clinical"),
    },
    {
      label: "Risk Assessment",
      icon: "⚠️",
      action: () => router.push("/risk"),
    },
    { label: "Settings", icon: "⚙️", action: () => router.push("/settings") },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto max-w-6xl px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Chairside Companion
          </h1>
          <button
            onClick={handleLogout}
            className="rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 transition font-medium"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-6xl px-4 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="mt-2 text-gray-600">
            Welcome to the Dental AI Analysis System
          </p>
        </div>

        {/* Button Grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {dashboardButtons.map((button, index) => (
            <button
              key={index}
              onClick={button.action}
              className="group rounded-lg bg-white p-6 shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200 active:scale-95"
            >
              <div className="mb-3 text-4xl">{button.icon}</div>
              <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                {button.label}
              </h3>
              <p className="mt-1 text-xs text-gray-500">Click to navigate</p>
            </button>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h3 className="text-gray-600 text-sm font-medium">
              Total Analyses
            </h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h3 className="text-gray-600 text-sm font-medium">Patients</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h3 className="text-gray-600 text-sm font-medium">System Status</h3>
            <p className="mt-2 text-lg font-bold text-green-600">
              ✓ Operational
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
