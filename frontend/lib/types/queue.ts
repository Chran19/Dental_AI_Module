export type QueueStatus = 'WAITING' | 'IN_CONSULTATION' | 'COMPLETED' | 'CANCELLED';

export interface QueueItem {
  id: string;
  patient_id: string;
  patient_name: string;
  check_in_time: string;
  status: QueueStatus;
  priority: 'NORMAL' | 'URGENT' | 'EMERGENCY';
  assigned_doctor_id?: string;
}
