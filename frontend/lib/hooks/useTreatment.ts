import { useState, useEffect } from "react";
import { TreatmentPlan } from "@/lib/types/treatment";
import { fetchAPI } from "@/lib/api";

export function useTreatmentPlans(patientId: string) {
  const [plans, setPlans] = useState<TreatmentPlan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;

    const fetch = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI(`/treatment/${patientId}`);
        setPlans(Array.isArray(data) ? data : []);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load treatment plans");
      } finally {
        setIsLoading(false);
      }
    };

    fetch();
  }, [patientId]);

  const createPlan = async (planData: any) => {
    try {
      const response = await fetchAPI("/treatment", {
        method: "POST",
        body: JSON.stringify(planData),
        headers: { "Content-Type": "application/json" },
      });
      setPlans([...plans, response]);
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  return { plans, isLoading, error, createPlan };
}
