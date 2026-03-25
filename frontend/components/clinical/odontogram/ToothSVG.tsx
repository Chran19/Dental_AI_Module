"use client";

import React from "react";

interface ToothSVGProps {
  toothNumber: number;
  status?:
    | "healthy"
    | "decayed"
    | "missing"
    | "filled"
    | "selected"
    | "implant";
  onClick?: (num: number) => void;
  className?: string;
  view?: "vestibular" | "occlusal" | "lingual";
}

export default function ToothSVG({
  toothNumber,
  status = "healthy",
  onClick,
  className = "",
  view = "vestibular",
}: ToothSVGProps) {
  // Simple representation of a tooth using paths
  // In a production app, these would be detailed SVG paths for each FDI tooth number

  const getStatusColor = () => {
    switch (status) {
      case "decayed":
        return "fill-red-500 stroke-red-700";
      case "missing":
        return "fill-slate-100 stroke-slate-300 opacity-30";
      case "filled":
        return "fill-blue-400 stroke-blue-600";
      case "selected":
        return "fill-yellow-200 stroke-yellow-600 ring-2 ring-yellow-400";
      case "implant":
        return "fill-slate-700 stroke-slate-900";
      default:
        return "fill-white stroke-slate-400 hover:fill-blue-50";
    }
  };

  return (
    <div
      onClick={() => onClick?.(toothNumber)}
      className={`relative cursor-pointer transition-all duration-200 flex flex-col items-center ${className}`}
    >
      <span className="text-[10px] font-bold text-slate-500 mb-1">
        {toothNumber}
      </span>
      <svg
        width="36"
        height="50"
        viewBox="0 0 40 60"
        className={`transition-colors ${getStatusColor()}`}
      >
        {/* Simplified Tooth Shape */}
        <path
          d="M10,15 C10,5 30,5 30,15 L32,40 C32,45 28,55 20,55 C12,55 8,45 8,40 Z"
          strokeWidth="1.5"
        />
        {/* Occlusal surface detail */}
        <path
          d="M12,18 C15,15 25,15 28,18"
          fill="none"
          strokeWidth="1"
          className="stroke-slate-300"
        />
        {status === "decayed" && (
          <circle cx="20" cy="25" r="4" className="fill-red-800" />
        )}
        {status === "filled" && (
          <rect
            x="15"
            y="20"
            width="10"
            height="10"
            rx="1"
            className="fill-blue-600"
          />
        )}
      </svg>
    </div>
  );
}
