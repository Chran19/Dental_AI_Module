"use client";

import { Diagnosis } from "@/lib/types/diagnosis";
import Card from "@/components/common/Card";
import Badge from "@/components/common/Badge";

interface DiagnosisCardProps {
  diagnosis: Diagnosis;
  onClick?: () => void;
}

const severityConfig = {
  MILD: { variant: "success" as const, icon: "🟢" },
  MODERATE: { variant: "warning" as const, icon: "🟡" },
  SEVERE: { variant: "danger" as const, icon: "🔴" },
};

export default function DiagnosisCard({
  diagnosis,
  onClick,
}: DiagnosisCardProps) {
  const config = severityConfig[diagnosis.severity];

  return (
    <Card onClick={onClick} className={onClick ? "cursor-pointer" : ""}>
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="text-lg font-semibold text-slate-900">
              {config.icon} {diagnosis.condition}
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              {new Date(diagnosis.created_at || "").toLocaleDateString()}
            </p>
          </div>
          <Badge label={diagnosis.severity} variant={config.variant} />
        </div>

        {diagnosis.findings && (
          <div className="bg-slate-50 p-3 rounded">
            <p className="text-sm text-slate-700">{diagnosis.findings}</p>
          </div>
        )}

        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">Confidence Score:</span>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-600"
                style={{ width: `${diagnosis.confidence * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-slate-900">
              {Math.round(diagnosis.confidence * 100)}%
            </span>
          </div>
        </div>

        {diagnosis.observations && diagnosis.observations.length > 0 && (
          <div>
            <p className="text-xs font-medium text-slate-700 mb-2">
              Clinical Observations:
            </p>
            <ul className="text-xs text-slate-600 space-y-1">
              {diagnosis.observations.map((obs, idx) => (
                <li key={idx}>• {obs}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}
