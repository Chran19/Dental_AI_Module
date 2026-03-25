"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/app/providers";
import {
  Users,
  LayoutDashboard,
  BarChart3,
  Stethoscope,
  ShieldAlert,
  Settings,
  LogOut,
  Upload,
  FileText,
  Menu,
  X,
  BookOpen,
  Pill,
} from "lucide-react";

interface MenuItem {
  title: string;
  href: string;
  icon: any;
  roles?: string[];
}

const menuItems: MenuItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Queue Board",
    href: "/dashboard/queue",
    icon: BarChart3,
    roles: ["RECEPTIONIST", "ADMIN"],
  },
  {
    title: "Patient Intake",
    href: "/dashboard/patients/new",
    icon: Users,
    roles: ["RECEPTIONIST", "ADMIN"],
  },
  {
    title: "Clinical",
    href: "/dashboard/clinical",
    icon: Stethoscope,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Diagnosis",
    href: "/dashboard/diagnosis",
    icon: BookOpen,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Treatment",
    href: "/dashboard/treatment",
    icon: Pill,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Risk",
    href: "/dashboard/risk",
    icon: ShieldAlert,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Upload",
    href: "/dashboard/upload",
    icon: Upload,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Results",
    href: "/dashboard/results",
    icon: FileText,
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  // Load collapsed state from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed");
    if (stored) setIsCollapsed(JSON.parse(stored));
  }, []);

  // Save collapsed state to localStorage
  const toggleCollapse = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem("sidebar-collapsed", JSON.stringify(newState));
  };

  const filteredItems = menuItems.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role)),
  );

  return (
    <aside
      className={`bg-gradient-to-b from-slate-900 to-slate-800 text-white h-screen flex flex-col fixed left-0 top-0 transition-all duration-300 z-50 ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Header */}
      <div
        className={`p-6 flex items-center justify-between border-b border-slate-700 ${isCollapsed ? "flex-col gap-2" : ""}`}
      >
        {!isCollapsed && (
          <div>
            <h1 className="text-lg font-bold flex items-center gap-2">
              <span className="text-blue-400">⚕️</span>
              <span>ChairSide</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">Dental AI</p>
          </div>
        )}

        <button
          onClick={toggleCollapse}
          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          title={isCollapsed ? "Expand" : "Collapse"}
        >
          {isCollapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-2 overflow-y-auto">
        {filteredItems.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-900/30"
                  : "text-slate-300 hover:bg-slate-700 hover:text-white"
              } ${isCollapsed ? "justify-center" : ""}`}
              title={isCollapsed ? item.title : ""}
            >
              <item.icon size={22} className="flex-shrink-0" />
              {!isCollapsed && (
                <span className="font-medium text-sm">{item.title}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-slate-700">
        <div
          className={`flex items-center gap-3 px-3 py-2 mb-3 rounded-lg bg-slate-700/40 ${isCollapsed ? "justify-center" : ""}`}
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
            {user?.email?.charAt(0).toUpperCase() || "U"}
          </div>
          {!isCollapsed && (
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium truncate">{user?.email}</p>
              <p className="text-xs text-slate-400 capitalize">
                {user?.role?.toLowerCase()}
              </p>
            </div>
          )}
        </div>

        <button
          onClick={() => logout()}
          className={`w-full flex items-center gap-3 px-3 py-2 text-slate-300 hover:bg-red-600/20 hover:text-red-300 rounded-lg transition-colors ${isCollapsed ? "justify-center" : ""}`}
          title={isCollapsed ? "Logout" : ""}
        >
          <LogOut size={20} className="flex-shrink-0" />
          {!isCollapsed && <span className="text-sm">Logout</span>}
        </button>
      </div>
    </aside>
  );
}
