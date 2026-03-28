"use client";

import LoginForm from "@/components/login/LoginForm";
import { Suspense } from "react";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 px-4">
      <div className="w-full max-w-lg">
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center p-3 mb-4 rounded-xl bg-blue-600 shadow-lg shadow-blue-200">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2z"></path>
              <path d="M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"></path>
              <path d="M16 12h.01"></path>
              <path d="M8 12h.01"></path>
              <path d="M12 8.5V12l2.5 2.5"></path>
            </svg>
          </div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
            ChairSide Companion
          </h1>
          <p className="mt-2 text-lg text-slate-700 font-semibold">
            AI-Powered Dental Intelligence
          </p>
        </div>

        <Suspense
          fallback={
            <div className="flex h-64 w-full items-center justify-center bg-white rounded-xl">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            </div>
          }
        >
          <LoginForm />
        </Suspense>

        <div className="mt-12 text-center text-slate-500 text-sm font-medium">
          &copy; {new Date().getFullYear()} ChairSide Companion. All rights
          reserved.
        </div>
      </div>
    </div>
  );
}
