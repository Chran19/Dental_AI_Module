"use client";

import { useState, useEffect } from "react";
import AuthGuard from "@/components/common/AuthGuard";
import Sidebar from "@/components/common/Sidebar";
import React from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed");
    if (stored) setIsCollapsed(JSON.parse(stored));

    // Listen for storage changes (when user toggles sidebar)
    const handleStorageChange = () => {
      const stored = localStorage.getItem("sidebar-collapsed");
      if (stored) setIsCollapsed(JSON.parse(stored));
    };

    window.addEventListener("storage", handleStorageChange);
    // Also listen for custom events from the sidebar
    const handleSidebarToggle = () => {
      const stored = localStorage.getItem("sidebar-collapsed");
      if (stored) setIsCollapsed(JSON.parse(stored));
    };
    window.addEventListener("sidebar-toggle", handleSidebarToggle);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("sidebar-toggle", handleSidebarToggle);
    };
  }, []);

  // Poll for changes to give immediate response
  useEffect(() => {
    const interval = setInterval(() => {
      const stored = localStorage.getItem("sidebar-collapsed");
      if (stored !== null) setIsCollapsed(JSON.parse(stored));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main
          className={`flex-1 transition-all duration-300 ${isCollapsed ? "ml-20" : "ml-64"} p-6 md:p-8`}
        >
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </AuthGuard>
  );
}
