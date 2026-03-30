export type QueueStatus = 'Waiting' | 'In_Consultation' | 'Completed' | 'Cancelled';

export interface QueueItem {
  id: string;
  patient_id: string;
  patient_name: string;
  patient_phone?: string;
  check_in_time: string;
  status: QueueStatus;
  priority: 'NORMAL' | 'URGENT' | 'EMERGENCY';
  assigned_doctor_id?: string;
  doctor_name?: string;
  position_in_queue?: number;
  estimated_wait_time?: number;
  reason_of_visit?: string;
  notes?: string;
  created_at?: string;
}
