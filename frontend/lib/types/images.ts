export interface Image {
  id: string;
  visit_id: string;
  patient_id: string;
  type: "XRAY" | "INTRAORAL" | "EXTRAORAL" | "CBCT" | "BITEWING" | "PANORAMIC";
  url: string;
  thumbnail_url?: string;
  annotations?: Annotation[];
  analysis?: ImageAnalysis;
  uploaded_by?: string;
  uploaded_at?: string;
  created_at?: string;
}

export interface Annotation {
  id?: string;
  type: string;
  coordinates: number[];
  label?: string;
  created_by?: string;
  created_at?: string;
}

export interface ImageAnalysis {
  pathologies_detected: string[];
  confidence: number;
  regions_affected: string[];
  severity?: string;
  recommendations?: string[];
}

export interface ImageUpload {
  file: File;
  type: "XRAY" | "INTRAORAL" | "EXTRAORAL" | "CBCT" | "BITEWING" | "PANORAMIC";
  visit_id: string;
}
