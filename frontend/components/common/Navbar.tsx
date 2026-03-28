"use client";

import { useAuth } from "@/app/providers";
import { useRouter } from "next/navigation";
import { LogOut, Settings, User } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <nav className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between h-16">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-slate-900">
            ChairSide Companion
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-slate-900">{user?.email}</p>
            <p className="text-xs text-slate-700 font-medium">
              {user?.role === "DOCTOR" ? "🩺 Doctor" : "👨‍💼 Staff"}
            </p>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100 hover:bg-indigo-200 transition-colors"
            >
              <User size={20} className="text-indigo-600" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1">
                <div className="px-4 py-3 border-b border-slate-100">
                  <p className="text-sm font-medium text-slate-900">
                    {user?.email}
                  </p>
                </div>
                <button
                  onClick={() => {
                    router.push("/dashboard/settings/profile");
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                >
                  <Settings size={16} /> Settings
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 border-t border-slate-100"
                >
                  <LogOut size={16} /> Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
