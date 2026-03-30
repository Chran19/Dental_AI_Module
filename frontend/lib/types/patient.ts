export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  contact_email?: string;
  phone?: string;
  contact_phone?: string;
  date_of_birth?: string;
  dob?: string;
  gender?: string;
  medical_history?: Record<string, any>;
  reason_of_visit?: string;
  doctor_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  dob: string;
  gender: string;
  contact_email?: string;
  contact_phone?: string;
  medical_history?: Record<string, any>;
  reason_of_visit?: string;
}
