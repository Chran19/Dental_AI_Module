import { useState, useEffect } from "react";
import { QueueItem } from "@/lib/types/queue";
import { fetchAPI } from "@/lib/api";

export function useQueue() {
  const [items, setItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = async () => {
    try {
      setIsLoading(true);
      const data = await fetchAPI("/queue/active");
      setItems(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load queue");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkIn = async (patientId: string) => {
    try {
      const response = await fetchAPI("/queue/check-in", {
        method: "POST",
        body: JSON.stringify({ patient_id: patientId }),
        headers: { "Content-Type": "application/json" },
      });
      await fetchQueue();
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  const updateStatus = async (patientId: string, status: string) => {
    try {
      const response = await fetchAPI(`/queue/${patientId}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
        headers: { "Content-Type": "application/json" },
      });
      await fetchQueue();
      return response;
    } catch (err: any) {
      throw err;
    }
  };

  return { items, isLoading, error, checkIn, updateStatus, refetch: fetchQueue };
}
