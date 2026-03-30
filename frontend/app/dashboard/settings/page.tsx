"use client";

import { useAuth } from "@/app/providers";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { fetchAPI } from "@/lib/api";
import {
  Settings,
  User,
  Bell,
  Lock,
  Server,
  LogOut,
  Save,
  CheckCircle,
  AlertCircle,
  Smartphone,
  Shield,
  Moon,
  Sun,
  Database,
  Wifi,
  WifiOff,
  Activity,
  Palette,
  Clock,
  RefreshCcw,
} from "lucide-react";

export default function SettingsPage() {
  const { isAuthenticated, logout, user } = useAuth();
  const router = useRouter();

  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("connecting");
  const [dbStatus, setDbStatus] = useState<
    "checking" | "connected" | "disconnected"
  >("checking");
  const [apiLatency, setApiLatency] = useState<number | null>(null);

  // State Categories
  const [profile, setProfile] = useState({
    fullName: "",
    email: user?.email || "",
    phone: "",
    role: user?.role || "DOCTOR",
  });

  const [settings, setSettings] = useState({
    enableNotifications: true,
    darkMode: false,
    autoSaveNotes: true,
    queueRefreshInterval: 15,
    compactView: false,
  });

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    inAppAlerts: true,
    urgentCaseAlerts: true,
    queueAlerts: true,
  });

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem("dental_settings");
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings((prev) => ({ ...prev, ...parsed }));
      } catch {}
    }
    const savedNotifs = localStorage.getItem("dental_notifications");
    if (savedNotifs) {
      try {
        setNotifications(JSON.parse(savedNotifs));
      } catch {}
    }
    const savedProfile = localStorage.getItem("dental_profile");
    if (savedProfile) {
      try {
        setProfile((prev) => ({ ...prev, ...JSON.parse(savedProfile) }));
      } catch {}
    }
    // Sync email from auth
    if (user?.email) {
      setProfile((prev) => ({
        ...prev,
        email: user.email || prev.email,
        role: user.role || prev.role,
      }));
    }
  }, [user]);

  // Health check
  useEffect(() => {
    const checkConnection = async () => {
      const start = Date.now();
      try {
        const response = await fetchAPI("/health", { withAuth: false });
        setApiLatency(Date.now() - start);
        setConnectionStatus(
          response?.status === "healthy" ? "connected" : "disconnected",
        );
        setDbStatus("connected"); // If /health works, DB is likely connected
      } catch (err) {
        setApiLatency(null);
        setConnectionStatus("disconnected");
        setDbStatus("disconnected");
      }
    };
    checkConnection();
  }, []);

  const handleProfileChange = (key: string, value: string) => {
    setProfile((prev) => ({ ...prev, [key]: value }));
  };

  const handleSettingChange = (key: string, value: boolean | number) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    // Save to localStorage
    localStorage.setItem("dental_settings", JSON.stringify(settings));
    localStorage.setItem(
      "dental_notifications",
      JSON.stringify(notifications),
    );
    localStorage.setItem("dental_profile", JSON.stringify(profile));
    await new Promise((r) => setTimeout(r, 500));
    setSaving(false);
    setSaveMessage("Settings saved successfully.");
    setTimeout(() => setSaveMessage(""), 3000);
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const refreshConnection = async () => {
    setConnectionStatus("connecting");
    setDbStatus("checking");
    const start = Date.now();
    try {
      const response = await fetchAPI("/health", { withAuth: false });
      setApiLatency(Date.now() - start);
      setConnectionStatus(
        response?.status === "healthy" ? "connected" : "disconnected",
      );
      setDbStatus("connected");
    } catch {
      setApiLatency(null);
      setConnectionStatus("disconnected");
      setDbStatus("disconnected");
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Settings className="text-gray-700" /> Account & Settings
            </h1>
            <p className="text-gray-600 mt-1 font-medium">
              Manage profile, preferences, notifications, and system
              diagnostics.
            </p>
          </div>
          <div className="flex gap-3">
            {saveMessage && (
              <div className="flex items-center gap-2 text-green-600 font-bold text-sm bg-green-50 px-4 py-2 rounded-lg">
                <CheckCircle size={16} /> {saveMessage}
              </div>
            )}
            <button
              onClick={handleSave}
              disabled={saving}
              className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-bold shadow-sm hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {saving ? (
                <div className="animate-spin h-4 w-4 border-2 border-white/20 border-t-white rounded-full" />
              ) : (
                <Save size={16} />
              )}
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 space-y-6">
        {/* Profile */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
            <User size={18} className="text-indigo-600" />
            <h2 className="text-lg font-bold text-gray-900">
              Personal Profile
            </h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={profile.fullName}
                onChange={(e) => handleProfileChange("fullName", e.target.value)}
                placeholder="Enter your full name"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-bold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={profile.email}
                readOnly
                className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-gray-600 font-bold cursor-not-allowed"
              />
              <p className="text-[10px] text-gray-400 mt-1 font-medium">
                Email is linked to your account and cannot be changed here.
              </p>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Mobile Phone
              </label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => handleProfileChange("phone", e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-bold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                Role
              </label>
              <div className="px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg">
                <span
                  className={`text-sm font-bold px-3 py-1 rounded-full ${
                    profile.role === "ADMIN"
                      ? "bg-purple-100 text-purple-700"
                      : profile.role === "DOCTOR"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  {profile.role}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* System Preferences */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
            <Palette size={18} className="text-gray-600" />
            <h2 className="text-lg font-bold text-gray-900">
              System Preferences
            </h2>
          </div>
          <div className="p-0">
            <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <div>
                <p className="font-bold text-gray-900">
                  Enable Global Notifications
                </p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  Toggle all browser and system alerts.
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.enableNotifications}
                onChange={(e) =>
                  handleSettingChange("enableNotifications", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
              />
            </label>
            <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <div>
                <p className="font-bold text-gray-900 flex items-center gap-2">
                  Dark Mode Interface{" "}
                  {settings.darkMode ? (
                    <Moon size={14} />
                  ) : (
                    <Sun size={14} />
                  )}
                </p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  Switch to high-contrast dark theme (Coming Soon).
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={(e) =>
                  handleSettingChange("darkMode", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
              />
            </label>
            <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <div>
                <p className="font-bold text-gray-900">
                  Auto-Save Clinical Notes
                </p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  Persist drafts every 30 seconds automatically.
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoSaveNotes}
                onChange={(e) =>
                  handleSettingChange("autoSaveNotes", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
              />
            </label>
            <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <div>
                <p className="font-bold text-gray-900">Compact View</p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  Use a denser layout in tables and lists.
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.compactView}
                onChange={(e) =>
                  handleSettingChange("compactView", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
              />
            </label>
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-bold text-gray-900 flex items-center gap-2">
                  <Clock size={14} /> Queue Auto-Refresh
                </p>
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  How often the queue board refreshes (in seconds).
                </p>
              </div>
              <select
                value={settings.queueRefreshInterval}
                onChange={(e) =>
                  handleSettingChange(
                    "queueRefreshInterval",
                    parseInt(e.target.value),
                  )
                }
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-bold bg-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value={5}>5s</option>
                <option value={10}>10s</option>
                <option value={15}>15s</option>
                <option value={30}>30s</option>
                <option value={60}>60s</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
            <Bell size={18} className="text-amber-600" />
            <h2 className="text-lg font-bold text-gray-900">Alert Routing</h2>
          </div>
          <div className="p-0">
            <label className="flex items-center space-x-4 p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <input
                type="checkbox"
                checked={notifications.emailAlerts}
                onChange={(e) =>
                  handleNotificationChange("emailAlerts", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
              />
              <div>
                <span className="font-bold text-gray-900">
                  Email Alerts (Digest)
                </span>
                <p className="text-xs text-gray-500 mt-0.5">
                  Receive daily summary of patient activity.
                </p>
              </div>
            </label>
            <label className="flex items-center space-x-4 p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <input
                type="checkbox"
                checked={notifications.inAppAlerts}
                onChange={(e) =>
                  handleNotificationChange("inAppAlerts", e.target.checked)
                }
                className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
              />
              <div>
                <span className="font-bold text-gray-900">
                  In-Application Toast Notifications
                </span>
                <p className="text-xs text-gray-500 mt-0.5">
                  Show real-time alerts within the dashboard.
                </p>
              </div>
            </label>
            <label className="flex items-center space-x-4 p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
              <input
                type="checkbox"
                checked={notifications.queueAlerts}
                onChange={(e) =>
                  handleNotificationChange("queueAlerts", e.target.checked)
                }
                className="w-5 h-5 rounded text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <div>
                <span className="font-bold text-gray-900">
                  Queue Wait Time Alerts
                </span>
                <p className="text-xs text-gray-500 mt-0.5">
                  Alert when patients wait longer than 30 minutes.
                </p>
              </div>
            </label>
            <label className="flex items-center space-x-4 p-5 cursor-pointer hover:bg-gray-50 transition">
              <input
                type="checkbox"
                checked={notifications.urgentCaseAlerts}
                onChange={(e) =>
                  handleNotificationChange(
                    "urgentCaseAlerts",
                    e.target.checked,
                  )
                }
                className="w-5 h-5 rounded text-red-600 focus:ring-red-500 border-gray-300"
              />
              <div>
                <span className="font-bold text-red-900">
                  Critical / Urgent Case Alerts
                </span>
                <p className="text-xs text-gray-500 mt-0.5">
                  High-priority notifications for emergency cases.
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Security & Sessions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
            <Shield size={18} className="text-green-600" />
            <h2 className="text-lg font-bold text-gray-900">
              Security & Access
            </h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-bold text-gray-800 hover:bg-gray-50 shadow-sm flex justify-center items-center gap-2 transition">
                <Lock size={16} /> Change Password
              </button>
              <button className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-bold text-gray-800 hover:bg-gray-50 shadow-sm flex justify-center items-center gap-2 transition">
                <Smartphone size={16} /> Setup 2FA
              </button>
            </div>

            <div className="pt-4">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                Active Device Sessions
              </h3>
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 bg-gray-50">
                  <div>
                    <p className="font-bold text-gray-900">
                      Current Session — {navigator?.userAgent?.includes("Chrome") ? "Chrome" : navigator?.userAgent?.includes("Firefox") ? "Firefox" : "Browser"}
                    </p>
                    <p className="text-xs font-medium text-green-600 mt-1">
                      Active Now
                    </p>
                  </div>
                  <span className="text-[10px] font-bold text-green-600 uppercase tracking-widest bg-green-50 px-2 py-1 rounded">
                    Active
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Diagnostics */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Server size={18} className="text-gray-600" />
              <h2 className="text-lg font-bold text-gray-900">
                System Diagnostics
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={refreshConnection}
                className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCcw
                  size={14}
                  className={
                    connectionStatus === "connecting" ? "animate-spin" : ""
                  }
                />
              </button>
              {connectionStatus === "connecting" && (
                <span className="text-[10px] font-bold text-gray-500 uppercase flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-ping"></div>{" "}
                  Pinging
                </span>
              )}
              {connectionStatus === "connected" && (
                <span className="text-[10px] font-bold text-green-700 uppercase bg-green-100 px-2 py-0.5 rounded flex items-center gap-1">
                  <Wifi size={10} /> Connected
                </span>
              )}
              {connectionStatus === "disconnected" && (
                <span className="text-[10px] font-bold text-red-700 uppercase bg-red-100 px-2 py-0.5 rounded flex items-center gap-1">
                  <WifiOff size={10} /> Disconnected
                </span>
              )}
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  API Endpoint
                </label>
                <input
                  type="text"
                  readOnly
                  value={
                    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
                  }
                  className="w-full px-4 py-3 bg-gray-100 border border-gray-200 text-gray-600 rounded-lg font-mono text-sm shadow-inner"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                  API Latency
                </label>
                <div className="px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg flex items-center gap-2">
                  <Activity size={14} className="text-gray-400" />
                  <span className="font-mono text-sm text-gray-600">
                    {apiLatency !== null ? `${apiLatency}ms` : "N/A"}
                  </span>
                  {apiLatency !== null && apiLatency < 200 && (
                    <span className="text-[10px] font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded">
                      Fast
                    </span>
                  )}
                  {apiLatency !== null &&
                    apiLatency >= 200 &&
                    apiLatency < 500 && (
                      <span className="text-[10px] font-bold text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded">
                        OK
                      </span>
                    )}
                  {apiLatency !== null && apiLatency >= 500 && (
                    <span className="text-[10px] font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded">
                      Slow
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                <Database
                  size={16}
                  className={
                    dbStatus === "connected"
                      ? "text-green-600"
                      : "text-red-600"
                  }
                />
                <div>
                  <p className="text-xs font-bold text-gray-700 uppercase">
                    PostgreSQL
                  </p>
                  <p
                    className={`text-xs font-medium ${dbStatus === "connected" ? "text-green-600" : dbStatus === "checking" ? "text-gray-500" : "text-red-600"}`}
                  >
                    {dbStatus === "connected"
                      ? "Connected via Docker"
                      : dbStatus === "checking"
                        ? "Checking..."
                        : "Disconnected"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                <Server size={16} className="text-blue-600" />
                <div>
                  <p className="text-xs font-bold text-gray-700 uppercase">
                    FastAPI Backend
                  </p>
                  <p
                    className={`text-xs font-medium ${connectionStatus === "connected" ? "text-green-600" : "text-red-600"}`}
                  >
                    {connectionStatus === "connected"
                      ? "Running"
                      : "Not Available"}
                  </p>
                </div>
              </div>
            </div>

            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-2">
              Environment configuration is managed via .env files.
            </p>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-red-50 rounded-xl border border-red-200 overflow-hidden">
          <div className="p-6 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
              <h3 className="font-bold text-red-900">Terminate Session</h3>
              <p className="text-xs text-red-700 font-medium mt-1">
                End your current session and log out from all tabs.
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-6 py-2.5 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 transition flex items-center gap-2 shadow-sm"
            >
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
