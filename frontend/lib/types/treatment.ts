export interface TreatmentPlan {
  id: string;
  patient_id: string;
  diagnosis_id?: string;
  title: string;
  procedures: Procedure[];
  total_cost?: number;
  status: "PLANNING" | "APPROVED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  start_date?: string;
  due_date?: string;
  notes?: string;
  created_at?: string;
  created_by?: string;
  updated_at?: string;
}

export interface Procedure {
  id?: string;
  name: string;
  description?: string;
  cost?: number;
  duration_minutes?: number;
  tooth_numbers?: string[];
  status?: "PENDING" | "COMPLETED";
  completion_date?: string;
}

export interface TreatmentPlanCreate {
  patient_id: string;
  diagnosis_id?: string;
  title: string;
  procedures: Procedure[];
  total_cost?: number;
  due_date?: string;
  notes?: string;
}
