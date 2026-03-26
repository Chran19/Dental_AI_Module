export interface Diagnosis {
  id: string;
  patient_id: string;
  visit_id: string;
  condition: string;
  severity: "MILD" | "MODERATE" | "SEVERE";
  confidence: number;
  findings?: string;
  observations?: string[];
  created_at?: string;
  created_by?: string;
  updated_at?: string;
}

export interface DiagnosisCreate {
  patient_id: string;
  visit_id: string;
  condition: string;
  severity: "MILD" | "MODERATE" | "SEVERE";
  confidence: number;
  findings?: string;
  observations?: string[];
}

export interface DiagnosisUpdate {
  condition?: string;
  severity?: "MILD" | "MODERATE" | "SEVERE";
  confidence?: number;
  findings?: string;
  observations?: string[];
}
