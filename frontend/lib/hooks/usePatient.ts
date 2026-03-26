import { useState, useEffect } from "react";
import { Patient } from "@/lib/types/patient";
import { fetchAPI } from "@/lib/api";

export function usePatient(patientId: string) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;

    const fetchPatient = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI(`/patients/${patientId}`);
        setPatient(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load patient");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPatient();
  }, [patientId]);

  return { patient, isLoading, error };
}

export function usePatients() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAPI("/patients");
        setPatients(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load patients");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const createPatient = async (patientData: any) => {
    try {
      const response = await fetchAPI("/patients", {
        method: "POST",
        body: JSON.stringify(patientData),
        headers: { "Content-Type": "application/json" },
      });
      setPatients([...patients, response]);
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  const updatePatient = async (patientId: string, patientData: any) => {
    try {
      const response = await fetchAPI(`/patients/${patientId}`, {
        method: "PATCH",
        body: JSON.stringify(patientData),
        headers: { "Content-Type": "application/json" },
      });
      setPatients(
        patients.map((p) => (p.id === patientId ? response : p))
      );
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  return { patients, isLoading, error, createPatient, updatePatient };
}
