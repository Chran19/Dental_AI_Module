"use client";

import React, { useState } from "react";
import ToothSVG from "./ToothSVG";
import { HelpCircle, Info } from "lucide-react";

interface OdontogramProps {
  initialStatus?: Record<number, string>;
  onSelect?: (toothNumber: number) => void;
  onUpdateStatus?: (toothNumber: number, status: string) => void;
  readOnly?: boolean;
}

export default function Odontogram({
  initialStatus = {},
  onSelect,
  onUpdateStatus,
  readOnly = false,
}: OdontogramProps) {
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);

  // FDI Quadrant System: 1 (Upper Right), 2 (Upper Left), 3 (Lower Left), 4 (Lower Right)
  const quadrants = {
    upperRight: [18, 17, 16, 15, 14, 13, 12, 11],
    upperLeft: [21, 22, 23, 24, 25, 26, 27, 28],
    lowerRight: [48, 47, 46, 45, 44, 43, 42, 41],
    lowerLeft: [31, 32, 33, 34, 35, 36, 37, 38],
  };

  const handleToothClick = (num: number) => {
    if (readOnly) return;
    setSelectedTooth(num);
    onSelect?.(num);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 select-none">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          Diagnostic Odontogram
          <span className="text-xs font-medium text-slate-400 uppercase tracking-tighter bg-slate-100 px-2 py-0.5 rounded">
            FDI ISO 3950
          </span>
        </h3>
        <div className="flex gap-4">
          <LegendItem color="bg-red-500" label="Decay" />
          <LegendItem color="bg-blue-400" label="Filling" />
          <LegendItem color="bg-slate-700" label="Implant" />
          <LegendItem color="bg-slate-100 border-slate-300" label="Missing" />
        </div>
      </div>

      <div className="flex flex-col gap-12 justify-center items-center overflow-x-auto py-4">
        {/* Upper Arch */}
        <div className="flex gap-8 border-b-2 border-dashed border-slate-200 pb-10 relative">
          <SectionLabel text="Upper Right" position="left" />
          <div className="flex gap-1">
            {quadrants.upperRight.map((num) => (
              <ToothSVG
                key={num}
                toothNumber={num}
                status={
                  selectedTooth === num
                    ? "selected"
                    : (initialStatus[num] as any) || "healthy"
                }
                onClick={handleToothClick}
              />
            ))}
          </div>
          <div className="w-1 bg-slate-300 mx-2 rounded-full h-24 absolute left-1/2 -ml-0.5 -mt-6"></div>
          <div className="flex gap-1">
            {quadrants.upperLeft.map((num) => (
              <ToothSVG
                key={num}
                toothNumber={num}
                status={
                  selectedTooth === num
                    ? "selected"
                    : (initialStatus[num] as any) || "healthy"
                }
                onClick={handleToothClick}
              />
            ))}
          </div>
          <SectionLabel text="Upper Left" position="right" />
        </div>

        {/* Lower Arch */}
        <div className="flex gap-8 pt-6 relative">
          <SectionLabel text="Lower Right" position="left" />
          <div className="flex gap-1">
            {quadrants.lowerRight.map((num) => (
              <ToothSVG
                key={num}
                toothNumber={num}
                status={
                  selectedTooth === num
                    ? "selected"
                    : (initialStatus[num] as any) || "healthy"
                }
                onClick={handleToothClick}
              />
            ))}
          </div>
          <div className="w-1 bg-slate-300 mx-2 rounded-full h-24 absolute left-1/2 -ml-0.5 -mt-2"></div>
          <div className="flex gap-1">
            {quadrants.lowerLeft.map((num) => (
              <ToothSVG
                key={num}
                toothNumber={num}
                status={
                  selectedTooth === num
                    ? "selected"
                    : (initialStatus[num] as any) || "healthy"
                }
                onClick={handleToothClick}
              />
            ))}
          </div>
          <SectionLabel text="Lower Left" position="right" />
        </div>
      </div>

      <div className="mt-8 flex items-center gap-3 p-3 bg-blue-50/50 border border-blue-100 rounded-xl text-blue-700 text-xs">
        <Info size={14} className="flex-shrink-0" />
        <p>
          Click on any tooth to view diagnosis history or update status. System
          uses FDI notation (11-48).
        </p>
      </div>
    </div>
  );
}

function SectionLabel({
  text,
  position,
}: {
  text: string;
  position: "left" | "right";
}) {
  return (
    <div
      className={`absolute -top-10 text-[9px] font-black text-slate-400 uppercase tracking-widest ${position === "left" ? "left-0" : "right-0"}`}
    >
      {text}
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-3 h-3 rounded-full ${color} border border-slate-300 shadow-sm`}
      ></div>
      <span className="text-[10px] font-bold text-slate-500 uppercase">
        {label}
      </span>
    </div>
  );
}
