"use client";

import { CheckCircle, AlertTriangle, TrendingUp } from "lucide-react";
import Badge from "@/components/common/Badge";
import { Card } from "@/lib/types/prescription";
import Button from "@/components/common/Button";

interface AISuggestionBoxProps {
  suggestions: Card[];
  isLoading: boolean;
  onApprove: (suggestion: Card) => void;
  onEdit: (suggestion: Card) => void;
  onReject:(suggestion: Card) => void;
}

export default function AISuggestionBox({
  suggestions,
  isLoading,
  onApprove,
  onEdit,
  onReject,
}: AISuggestionBoxProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-blue-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
          <h3 className="font-semibold text-slate-900">AI is analyzing...</h3>
        </div>
        <p className="text-sm text-slate-600">Processing symptoms and generating recommendations</p>
      </div>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-6 text-center">
        <TrendingUp size={32} className="mx-auto text-slate-400 mb-3" />
        <p className="text-slate-600">No suggestions available yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-900">
        AI-Generated Suggestions
      </h3>

      {suggestions.map((suggestion, idx) => (
        <div
          key={idx}
          className="bg-white rounded-lg border border-blue-200 p-4 space-y-3"
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-slate-900">{suggestion.name}</h4>
              <p className="text-sm text-slate-600 mt-1">{suggestion.indication}</p>
            </div>
            <Badge
              label={`${Math.round((suggestion.confidence || 0) * 100)}%`}
              variant="success"
            />
          </div>

          {suggestion.contraindications && suggestion.contraindications.length > 0 && (
            <div className="flex items-start gap-2 bg-red-50 p-3 rounded">
              <AlertTriangle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-900">⚠️ Contraindications</p>
                <ul className="text-xs text-red-800 mt-1 space-y-1">
                  {suggestion.contraindications.map((c, i) => (
                    <li key={i}>• {c}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-slate-600">Dosage</p>
              <p className="font-medium text-slate-900">{suggestion.dosage}</p>
            </div>
            <div>
              <p className="text-slate-600">Frequency</p>
              <p className="font-medium text-slate-900">{suggestion.frequency}</p>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button
              onClick={() => onApprove(suggestion)}
              variant="primary"
              size="sm"
            >
              <CheckCircle size={16} /> Approve
            </Button>
            <Button onClick={() => onEdit(suggestion)} variant="secondary" size="sm">
              Edit
            </Button>
            <Button onClick={() => onReject(suggestion)} variant="secondary" size="sm">
              Reject
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
