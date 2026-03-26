import { useState } from "react";
import { Prescription, PrescriptionCreate } from "@/lib/types/prescription";
import { fetchAPI } from "@/lib/api";

export function usePrescription() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createPrescription = async (data: PrescriptionCreate) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetchAPI("/prescriptions", {
        method: "POST",
        body: JSON.stringify(data),
        headers: { "Content-Type": "application/json" },
      });
      return response;
    } catch (err: any) {
      setError(err.message || "Failed to create prescription");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getPrescription = async (visitId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetchAPI(`/prescriptions/${visitId}`);
      return response;
    } catch (err: any) {
      setError(err.message || "Failed to load prescription");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { createPrescription, getPrescription, isLoading, error };
}
