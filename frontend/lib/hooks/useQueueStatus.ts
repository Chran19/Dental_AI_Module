import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/app/providers';
import { updateQueueStatus } from '@/lib/store';

/**
 * Hook to manage queue status updates during clinical workflow
 * Automatically marks patient as "In_Consultation" when entering clinical pages
 * Allows marking as "Completed" when finishing workflow
 */
export function useQueueStatus(patientId: string) {
  const { user } = useAuth();
  const [queueId, setQueueId] = useState<string | null>(null);

  // Auto-mark as In_Consultation when patient detail page is accessed
  useEffect(() => {
    const markAsConsulting = async () => {
      if (patientId && user?.role === 'DOCTOR') {
        try {
          // Find the queue item for this patient and mark as In_Consultation
          const response = await fetch('/api/queue/active', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const queueItems = await response.json();
            const patientQueueItem = queueItems.find(
              (item: any) => item.patient_id === patientId,
            );

            if (patientQueueItem) {
              setQueueId(patientQueueItem.id);
              
              if (patientQueueItem.status === 'Waiting') {
                // Auto-update status to In_Consultation
                await updateQueueStatus(patientQueueItem.id, 'In_Consultation');
              }
            }
          }
        } catch (err) {
          console.error('Failed to update queue status:', err);
        }
      }
    };

    markAsConsulting();
  }, [patientId, user?.role]);

  // Function to mark patient workflow as complete
  const markAsComplete = useCallback(async () => {
    if (queueId) {
      try {
        await updateQueueStatus(queueId, 'Completed');
        return true;
      } catch (err) {
        console.error('Failed to mark patient as complete:', err);
      }
    }
    return false;
  }, [queueId]);

  return { markAsComplete, queueId };
}
