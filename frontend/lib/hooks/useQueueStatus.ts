import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/app/providers';
import { updateQueueStatus, fetchQueue } from '@/lib/store';

/**
 * Hook to manage queue status updates during clinical workflow
 * Automatically marks patient as "In_Consultation" when entering clinical pages
 * Allows marking as "Completed" when finishing workflow
 */
export function useQueueStatus(patientId: string) {
  const { user } = useAuth();
  const [queueId, setQueueId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-mark as In_Consultation when patient detail page is accessed
  useEffect(() => {
    const markAsConsulting = async () => {
      if (patientId && user?.role === 'DOCTOR') {
        try {
          setError(null);
          // Fetch active queue using the backend API via store
          const queueItems = await fetchQueue();
          console.log('[useQueueStatus] Active queue items:', queueItems);
          
          const patientQueueItem = queueItems.find(
            (item: any) => item.patient_id === patientId,
          );

          if (patientQueueItem) {
            console.log('[useQueueStatus] Found queue item for patient:', patientQueueItem.id);
            setQueueId(patientQueueItem.id);
            
            if (patientQueueItem.status === 'Waiting') {
              // Auto-update status to In_Consultation
              console.log('[useQueueStatus] Marking patient as In_Consultation');
              await updateQueueStatus(patientQueueItem.id, 'In_Consultation');
            }
          } else {
            console.warn('[useQueueStatus] No queue item found for patient:', patientId);
            setError('Patient queue item not found. Please ensure patient is checked in.');
          }
        } catch (err) {
          const errorMsg = err instanceof Error ? err.message : 'Unknown error';
          console.error('[useQueueStatus] Failed to fetch queue:', errorMsg);
          setError(`Failed to load queue status: ${errorMsg}`);
        }
      }
    };

    markAsConsulting();
  }, [patientId, user?.role]);

  // Function to mark patient workflow as complete
  const markAsComplete = useCallback(async () => {
    if (!queueId) {
      const err = 'Queue ID not found. Patient may not be checked in.';
      console.error('[useQueueStatus]', err);
      setError(err);
      return false;
    }

    try {
      setError(null);
      console.log('[useQueueStatus] Marking patient as Completed with queueId:', queueId);
      const success = await updateQueueStatus(queueId, 'Completed');
      
      if (!success) {
        const err = 'Failed to update queue status. Please try again.';
        console.error('[useQueueStatus]', err);
        setError(err);
        return false;
      }
      
      console.log('[useQueueStatus] Successfully marked patient as Completed');
      return true;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      console.error('[useQueueStatus] Exception marking patient complete:', errorMsg);
      setError(`Failed to complete workflow: ${errorMsg}`);
      return false;
    }
  }, [queueId]);

  return { markAsComplete, queueId, error, setError };
}
