"use client";

import { useAuth } from "@/app/providers";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
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
  Moon
} from "lucide-react";

export default function SettingsPage() {
  const { isAuthenticated, logout, user } = useAuth();
  const router = useRouter();

  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");

  // State Categories
  const [profile, setProfile] = useState({
    fullName: "Dr. Admin User",
    email: user?.email || "admin@dental.ai",
    phone: "+1 (555) 123-4567"
  });

  const [settings, setSettings] = useState({
    enableNotifications: true,
    darkMode: false,
    autoSaveNotes: true,
  });

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    inAppAlerts: true,
    urgentCaseAlerts: true,
  });

  useEffect(() => {
    // Dynamic connection check
    const checkConnection = async () => {
      try {
        const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        // Mocking a health check ping
        await new Promise(r => setTimeout(r, 600)); 
        setConnectionStatus("connected");
      } catch (err) {
        setConnectionStatus("disconnected");
      }
    };
    checkConnection();
  }, []);

  const handleProfileChange = (key: string, value: string) => {
    setProfile(prev => ({ ...prev, [key]: value }));
  };

  const handleSettingChange = (key: string, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    // Simulate API save
    await new Promise(r => setTimeout(r, 800));
    setSaving(false);
    setSaveMessage("Settings saved securely.");
    setTimeout(() => setSaveMessage(""), 3000);
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isAuthenticated) return null;

  return (
    <div className="space-y-6 bg-gray-50 min-h-screen pb-10">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6 shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
               <Settings className="text-gray-700" /> Account Preferences
            </h1>
            <p className="text-gray-600 mt-1 font-medium">
              Manage personal details, security, and alerting configurations.
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
                ) : <Save size={16} />} 
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
               <h2 className="text-lg font-bold text-gray-900">Personal Profile</h2>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="md:col-span-2">
                 <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Full Legal Name</label>
                 <input
                   type="text"
                   value={profile.fullName}
                   onChange={(e) => handleProfileChange("fullName", e.target.value)}
                   className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-bold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
                 />
               </div>
               <div>
                 <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Email Address</label>
                 <input
                   type="email"
                   value={profile.email}
                   onChange={(e) => handleProfileChange("email", e.target.value)}
                   className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-bold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
                 />
               </div>
               <div>
                 <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Mobile Phone</label>
                 <input
                   type="tel"
                   value={profile.phone}
                   onChange={(e) => handleProfileChange("phone", e.target.value)}
                   className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 font-bold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
                 />
               </div>
            </div>
         </div>

         {/* General Preferences */}
         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
               <Settings size={18} className="text-gray-600" />
               <h2 className="text-lg font-bold text-gray-900">System Preferences</h2>
            </div>
            <div className="p-0">
               <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
                  <div>
                     <p className="font-bold text-gray-900">Enable Global Notifications</p>
                     <p className="text-xs text-gray-500 font-medium mt-0.5">Toggle all browser and system alerts simultaneously.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.enableNotifications}
                    onChange={(e) => handleSettingChange("enableNotifications", e.target.checked)}
                    className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                  />
               </label>
               <label className="flex items-center justify-between p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
                  <div>
                     <p className="font-bold text-gray-900 flex items-center gap-2">Dark Mode Interface <Moon size={14}/></p>
                     <p className="text-xs text-gray-500 font-medium mt-0.5">Switch application theme to high-contrast dark mode.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.darkMode}
                    onChange={(e) => handleSettingChange("darkMode", e.target.checked)}
                    className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                  />
               </label>
               <label className="flex items-center justify-between p-5 cursor-pointer hover:bg-gray-50 transition">
                  <div>
                     <p className="font-bold text-gray-900">Auto-Save Clinical Notes</p>
                     <p className="text-xs text-gray-500 font-medium mt-0.5">Automatically persist drafts every 30 seconds.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.autoSaveNotes}
                    onChange={(e) => handleSettingChange("autoSaveNotes", e.target.checked)}
                    className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                  />
               </label>
            </div>
         </div>

         {/* Detailed Notifications */}
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
                   onChange={(e) => handleNotificationChange("emailAlerts", e.target.checked)}
                   className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
                 />
                 <span className="font-bold text-gray-900">Email Alerts (Digest)</span>
               </label>
               <label className="flex items-center space-x-4 p-5 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition">
                 <input
                   type="checkbox"
                   checked={notifications.inAppAlerts}
                   onChange={(e) => handleNotificationChange("inAppAlerts", e.target.checked)}
                   className="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
                 />
                 <span className="font-bold text-gray-900">In-Application Toast Notifications</span>
               </label>
               <label className="flex items-center space-x-4 p-5 cursor-pointer hover:bg-gray-50 transition">
                 <input
                   type="checkbox"
                   checked={notifications.urgentCaseAlerts}
                   onChange={(e) => handleNotificationChange("urgentCaseAlerts", e.target.checked)}
                   className="w-5 h-5 rounded text-red-600 focus:ring-red-500 border-gray-300"
                 />
                 <span className="font-bold text-red-900">Critical / Urgent Case Breaches (SMS)</span>
               </label>
            </div>
         </div>

         {/* Security & Sessions */}
         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-5 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
               <Shield size={18} className="text-green-600" />
               <h2 className="text-lg font-bold text-gray-900">Security & Access</h2>
            </div>
            <div className="p-6 space-y-4">
               <div className="flex flex-col sm:flex-row gap-4">
                  <button className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-bold text-gray-800 hover:bg-gray-50 shadow-sm flex justify-center items-center gap-2 transition">
                     <Lock size={16} /> Upgrade Password
                  </button>
                  <button className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg font-bold text-gray-800 hover:bg-gray-50 shadow-sm flex justify-center items-center gap-2 transition">
                     <Smartphone size={16} /> Setup Two-Factor Auth
                  </button>
               </div>
               
               <div className="pt-4">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Active Device Sessions</h3>
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                     <div className="flex items-center justify-between p-4 bg-gray-50">
                        <div>
                           <p className="font-bold text-gray-900">Windows PC - Chrome Browser</p>
                           <p className="text-xs font-medium text-green-600 mt-1">Current Session (Connected)</p>
                        </div>
                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Active</span>
                     </div>
                  </div>
               </div>
            </div>
         </div>

         {/* Diagnostics */}
         <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-5 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
               <div className="flex items-center gap-2">
                  <Server size={18} className="text-gray-600" />
                  <h2 className="text-lg font-bold text-gray-900">API Diagnostics</h2>
               </div>
               {connectionStatus === "connecting" && <span className="text-[10px] font-bold text-gray-500 uppercase flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-ping"></div> Pinging</span>}
               {connectionStatus === "connected" && <span className="text-[10px] font-bold text-green-700 uppercase bg-green-100 px-2 py-0.5 rounded flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> Connected</span>}
               {connectionStatus === "disconnected" && <span className="text-[10px] font-bold text-red-700 uppercase bg-red-100 px-2 py-0.5 rounded flex items-center gap-1"><AlertCircle size={10} /> Disconnected</span>}
            </div>
            <div className="p-6 space-y-4">
               <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Endpoint Resolution URL</label>
                  <input
                    type="text"
                    readOnly
                    value={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                    className="w-full px-4 py-3 bg-gray-100 border border-gray-200 text-gray-600 rounded-lg font-mono text-sm shadow-inner"
                  />
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-2">Environment mapping is locked for security integrity.</p>
               </div>
            </div>
         </div>

         {/* Danger Zone */}
         <div className="bg-red-50 rounded-xl border border-red-200 overflow-hidden">
            <div className="p-6 flex flex-col sm:flex-row justify-between items-center gap-4">
               <div>
                  <h3 className="font-bold text-red-900">Terminate Session</h3>
                  <p className="text-xs text-red-700 font-medium mt-1">End your current session across all local tabs safely.</p>
               </div>
               <button
                  onClick={handleLogout}
                  className="px-6 py-2.5 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 transition flex items-center gap-2 shadow-sm"
               >
                  <LogOut size={16} /> Disconnect
               </button>
            </div>
         </div>

      </div>
    </div>
  );
}
