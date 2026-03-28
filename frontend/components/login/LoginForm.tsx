"use client";

import { useState } from "react";
import { useAuth } from "@/app/providers";
import { useRouter, useSearchParams } from "next/navigation";
import { fetchAPI } from "@/lib/api";
import { AlertCircle, Loader2 } from "lucide-react";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("redirect") || "/dashboard";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Backend expects OAuth2 password flow: form data with 'username' and 'password'
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/token`,
        {
          method: "POST",
          body: formData,
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Invalid credentials");
      }

      login(data.access_token);
      router.push(callbackUrl);
    } catch (err: any) {
      setError(err.message || "An error occurred during login");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border border-slate-100">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-slate-900">Sign In</h2>
        <p className="text-slate-500 mt-2">Access the ChairSide Companion</p>
      </div>

      {error && (
        <div className="p-3 rounded-md bg-red-50 border border-red-200 flex items-center gap-3 text-red-600 text-sm">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-slate-900 placeholder-slate-700"
            placeholder="doctor@example.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-slate-900 placeholder-slate-700"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors flex items-center justify-center gap-2 disabled:bg-blue-400"
        >
          {isSubmitting ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Signing in...</span>
            </>
          ) : (
            "Login"
          )}
        </button>
      </form>

      <div className="text-center mt-4 text-sm text-slate-500">
        <p>
          Don't have an account?{" "}
          <a
            href="/login/register"
            className="text-blue-600 hover:underline font-medium"
          >
            Contact Administrator
          </a>
        </p>
      </div>

      <div className="mt-6 pt-6 border-t border-slate-100 italic text-center text-[10px] text-slate-400">
        Default test credentials available in development mode
      </div>
    </div>
  );
}
