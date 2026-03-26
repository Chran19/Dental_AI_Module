export interface Visit {
  id: string;
  patient_id: string;
  doctor_id: string;
  start_time: string;
  end_time?: string;
  status: "ACTIVE" | "COMPLETED" | "CANCELLED";
  chief_complaint?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface VisitCreate {
  patient_id: string;
  chief_complaint?: string;
}

export interface VisitInput {
  tooth_site?: string;
  jaw_region?: string;
  symptoms?: string[];
  symptom_duration_days?: number;
  pain_level?: number;
  swelling_grade?: string;
  fever_present?: boolean;
  clinical_findings?: string;
}
