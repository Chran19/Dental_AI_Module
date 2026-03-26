import { useState, useEffect } from "react";
import { RiskAssessment } from "@/lib/types/risk";
import { fetchAPI } from "@/lib/api";

export function useRiskAssessment(patientId: string) {
  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;

    const fetch = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI(`/risk-engine/${patientId}`);
        setAssessment(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load risk assessment");
      } finally {
        setIsLoading(false);
      }
    };

    fetch();
  }, [patientId]);

  return { assessment, isLoading, error };
}
