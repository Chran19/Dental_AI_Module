"use client";

import { AlertTriangle, TrendingUp, AlertCircle } from "lucide-react";
import { RiskAssessment } from "@/lib/types/risk";
import Card from "@/components/common/Card";
import Badge from "@/components/common/Badge";

interface RiskDashboardProps {
  assessment: RiskAssessment;
}

const getRiskColor = (level: string) => {
  switch (level) {
    case "LOW":
      return "bg-green-100 text-green-800";
    case "MODERATE":
      return "bg-yellow-100 text-yellow-800";
    case "HIGH":
      return "bg-orange-100 text-orange-800";
    case "CRITICAL":
      return "bg-red-100 text-red-800";
    default:
      return "bg-slate-100 text-slate-800";
  }
};

export default function RiskDashboard({ assessment }: RiskDashboardProps) {
  return (
    <div className="space-y-6">
      {/* Overall Risk Score */}
      <Card>
        <div className="text-center py-6">
          <div className="flex justify-center mb-4">
            <div className="relative w-32 h-32">
              <svg
                className="w-full h-full transform -rotate-90"
                viewBox="0 0 100 100"
              >
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e2e8f0"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  strokeDasharray={`${(assessment.overall_risk_score / 100) * 282.7} 282.7`}
                  className={
                    assessment.risk_level === "CRITICAL"
                      ? "text-red-600"
                      : assessment.risk_level === "HIGH"
                        ? "text-orange-600"
                        : assessment.risk_level === "MODERATE"
                          ? "text-yellow-600"
                          : "text-green-600"
                  }
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-3xl font-bold text-slate-900">
                    {assessment.overall_risk_score}
                  </p>
                  <p className="text-xs text-slate-600">Risk Score</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <Badge
              label={assessment.risk_level}
              variant={
                assessment.risk_level === "CRITICAL"
                  ? "danger"
                  : assessment.risk_level === "HIGH"
                    ? "warning"
                    : "success"
              }
            />
          </div>
        </div>
      </Card>

      {/* Risk Factors */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-3">
          Risk Factors
        </h3>
        <div className="space-y-3">
          {assessment.factors.map((factor, idx) => (
            <Card key={idx}>
              <div className="flex items-start gap-3">
                {factor.severity === "HIGH" ? (
                  <AlertTriangle
                    size={20}
                    className="text-red-600 flex-shrink-0 mt-0.5"
                  />
                ) : (
                  <AlertCircle
                    size={20}
                    className="text-yellow-600 flex-shrink-0 mt-0.5"
                  />
                )}
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-slate-900">
                      {factor.name}
                    </h4>
                    <Badge
                      label={factor.severity}
                      variant={
                        factor.severity === "HIGH" ? "danger" : "warning"
                      }
                    />
                  </div>
                  {factor.description && (
                    <p className="text-sm text-slate-600 mt-1">
                      {factor.description}
                    </p>
                  )}
                  {factor.recommendations &&
                    factor.recommendations.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-slate-700">
                          Recommendations:
                        </p>
                        <ul className="text-xs text-slate-600 mt-1 space-y-1">
                          {factor.recommendations.map((rec, i) => (
                            <li key={i}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Overall Recommendations */}
      {assessment.recommendations && assessment.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-slate-900 mb-3">
            Recommendations
          </h3>
          <Card className="bg-blue-50 border-blue-200">
            <ul className="space-y-2">
              {assessment.recommendations.map((rec, idx) => (
                <li key={idx} className="flex gap-2 text-sm text-blue-900">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      )}
    </div>
  );
}
