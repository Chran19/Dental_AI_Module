"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/app/providers";
import { useEffect } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, isLoading } = useAuth();

  useEffect(() => {
    // Redirect immediately when ready, don't wait for render
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    // Role-based redirect with smoother transition
    const targetPath =
      user?.role === "RECEPTIONIST"
        ? "/dashboard/receptionist"
        : "/dashboard/doctor";

    // Prefetch the route before navigating
    router.prefetch(targetPath);

    // Use replace instead of push to prevent back button issues
    router.replace(targetPath);
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading || !isAuthenticated) {
    const roleLabel = user?.role === "RECEPTIONIST" ? "Receptionist" : "Doctor";

    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mt-4">
            Loading {roleLabel} Dashboard
          </h2>
          <p className="text-gray-600 text-sm mt-2">
            {isLoading
              ? "Authenticating..."
              : "Redirecting you to your dashboard..."}
          </p>
        </div>
      </div>
    );
  }

  // This page is now pure redirect - content never renders
  return null;
}
