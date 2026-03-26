import { useState, useEffect } from "react";
import { Diagnosis } from "@/lib/types/diagnosis";
import { fetchAPI } from "@/lib/api";

export function useDiagnosis(diagnosisId: string) {
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!diagnosisId) return;

    const fetch = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI(`/diagnosis/${diagnosisId}`);
        setDiagnosis(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load diagnosis");
      } finally {
        setIsLoading(false);
      }
    };

    fetch();
  }, [diagnosisId]);

  return { diagnosis, isLoading, error };
}

export function usePatientDiagnoses(patientId: string) {
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;

    const fetch = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI(`/diagnosis/patient/${patientId}`);
        setDiagnoses(Array.isArray(data) ? data : []);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load diagnoses");
      } finally {
        setIsLoading(false);
      }
    };

    fetch();
  }, [patientId]);

  const createDiagnosis = async (diagnosisData: any) => {
    try {
      const response = await fetchAPI("/diagnosis", {
        method: "POST",
        body: JSON.stringify(diagnosisData),
        headers: { "Content-Type": "application/json" },
      });
      setDiagnoses([...diagnoses, response]);
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  return { diagnoses, isLoading, error, createDiagnosis };
}
