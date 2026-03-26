export interface Prescription {
  id: string;
  visit_id: string;
  patient_id: string;
  medicines: Card[];
  notes?: string;
  created_at?: string;
  created_by?: string;
}

export interface Card {
  id?: string;
  name: string;
  dosage: string;
  frequency: string;
  duration_days?: number;
 indication?: string;
  confidence?: number;
  contraindications?: string[];
  alternatives?: string[];
  side_effects?: string[];
}

export interface PrescriptionCreate {
  visit_id: string;
  medicines: Card[];
  notes?: string;
}
