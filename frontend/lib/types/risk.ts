export interface RiskAssessment {
  id: string;
  patient_id: string;
  overall_risk_score: number; // 0-100
  risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  factors: RiskFactor[];
  recommendations: string[];
  created_at?: string;
  updated_at?: string;
}

export interface RiskFactor {
  name: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  description?: string;
  recommendations?: string[];
}

export interface RiskProfile {
  caries_risk: number;
  periodontal_risk: number;
  implant_risk: number;
  infection_risk: number;
  surgical_risk: number;
}
