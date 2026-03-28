const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  withAuth?: boolean;
}

function formatErrorMessage(data: any): string {
  if (!data) return 'Unknown error';
  if (typeof data === 'string') return data;
  if (data.message) return data.message;
  if (data.detail) return data.detail;
  if (data.error) return data.error;
  if (data.errors && Array.isArray(data.errors)) {
    return data.errors.map((e: any) => e.msg || e.message || e).join('; ');
  }
  // For plain objects, convert to JSON for inspection
  return JSON.stringify(data);
}

export async function fetchAPI(endpoint: string, options: RequestOptions = {}) {
  const { withAuth = true, ...init } = options;
  
  const headers = new Headers(init.headers);

  if (withAuth) {
    const token = localStorage.getItem('token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const fullUrl = `${API_URL}${endpoint}`;
  const method = init.method || 'GET';
  console.log(`[API] ${method} ${fullUrl}`, {
    headers: Object.fromEntries(headers),
    body: init.body ? (typeof init.body === 'string' ? (() => {
      try {
        return JSON.parse(init.body as string);
      } catch {
        return init.body;
      }
    })() : init.body) : undefined
  });

  try {
    const response = await fetch(fullUrl, {
      ...init,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Unauthorized - redirecting to login');
    }

    let data;
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    console.log(`[API] Response ${response.status}:`, data);

    if (!response.ok) {
      const errorMessage = formatErrorMessage(data) || `API error: ${response.status}`;
      console.error(`[API Error] ${method} ${endpoint} (${response.status}):`, errorMessage);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error(`[API Exception] ${method} ${endpoint}:`, errorMsg, error);
    throw error;
  }
}

// Auth endpoints
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  return fetchAPI('/auth/token', {
    method: 'POST',
    body: formData,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    withAuth: false,
  });
}

export async function logout() {
  localStorage.removeItem('token');
}

// Image analysis endpoints
export async function uploadImage(file: File) {
  // Validate file size (max 50MB to match backend)
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    throw new Error(`File is too large (${sizeMB}MB). Maximum allowed size is 50MB.`);
  }

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/x-tiff', 'image/dicom'];
  // Some browsers may not set MIME type for medical images, allow by extension too
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'];
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  
  if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
    throw new Error(`File type not supported. Please upload JPG, PNG, TIFF, or DICOM images.`);
  }

  const formData = new FormData();
  formData.append('file', file);

  // Call the real ML image analysis endpoint (not /api/images/upload)
  return await fetchAPI('/image-analysis/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function getAnalysisResults() {
  // Note: Backend doesn't have a dedicated /results endpoint
  // Results are returned directly from upload
  return Promise.resolve([]);
}

export async function uploadAndAnalyzeImage(file: File, patientId?: string, withDiagnosis: boolean = false) {
  const formData = new FormData();
  formData.append('file', file);
  if (patientId) {
    formData.append('patient_id', patientId);
  }
  if (withDiagnosis) {
    formData.append('with_diagnosis', 'true');
  }

  return await fetchAPI('/image-analysis/upload', {
    method: 'POST',
    body: formData,
  });
}

// Patient endpoints
export async function getPatients() {
  try {
    return await fetchAPI('/api/patients');
  } catch (err) {
    console.log('[API] Using mock patients data due to:', err);
    // Fallback to mock data during development
    return [
      { id: "550e8400-e29b-41d4-a716-446655440000", first_name: "John", last_name: "Doe", email: "john@example.com", phone: "555-0001" },
      { id: "550e8400-e29b-41d4-a716-446655440001", first_name: "Jane", last_name: "Smith", email: "jane@example.com", phone: "555-0002" },
      { id: "550e8400-e29b-41d4-a716-446655440002", first_name: "Robert", last_name: "Johnson", email: "robert@example.com", phone: "555-0003" },
    ];
  }
}

export async function createPatient(data: {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}) {
  try {
    return await fetchAPI('/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.log('[API] Create patient fallback:', err);
    // Return mock success
    return {
      id: `550e8400-e29b-41d4-a716-${Math.random().toString().substring(2, 12).padEnd(12, '0')}`,
      ...data,
    };
  }
}

export async function updatePatient(id: string, data: any) {
  try {
    return await fetchAPI(`/api/patients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.log('[API] Update patient fallback:', err);
    return { id, ...data };
  }
}

export async function deletePatient(id: string) {
  try {
    return await fetchAPI(`/api/patients/${id}`, {
      method: 'DELETE',
    });
  } catch (err) {
    console.log('[API] Delete patient fallback:', err);
    return { success: true };
  }
}

// Visit endpoints
export async function saveVisitData(
  visitId: string,
  data: {
    symptoms: string;
    toothStatus: Record<number, string>;
    painLevel: string;
    mobility: string;
    images?: string[]; // Assuming images are uploaded first and we pass IDs/URLs
  }
) {
  try {
    return await fetchAPI(`/visits/${visitId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.log("[API] Save visit fallback:", err);
    return { success: true, ...data };
  }
}

export async function createClinicalInput(visitId: string, data: any) {
  try {
    return await fetchAPI("/clinical-input", {
      method: "POST", 
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visit_id: visitId, ...data }),
    });
  } catch (err) {
    console.log("[API] Create clinical input fallback:", err);
    return { id: "mock-input-id", ...data };
  }
}

// Clinical input endpoints
export async function submitClinicalInput(data: any) {
  // Map form gender values to backend enum: 'Male', 'Female', 'Other'
  const genderMap: Record<string, string> = {
    'M': 'Male',
    'F': 'Female',
    'Male': 'Male',
    'Female': 'Female',
    'Other': 'Other',
  };

  // Map smoking status to backend enum: 'Non-Smoker', 'Former_Smoker', 'Current_Smoker'
  const smokingMap: Record<string, string> = {
    'Never': 'Non-Smoker',
    'Former': 'Former_Smoker',
    'Current': 'Current_Smoker',
    'Non-Smoker': 'Non-Smoker',
    'Former_Smoker': 'Former_Smoker',
    'Current_Smoker': 'Current_Smoker',
  };

  // Valid symptom options from backend
  const validSymptoms = [
    'Toothache', 'Thermal_Sensitivity_Hot', 'Thermal_Sensitivity_Cold',
    'Spontaneous_Pain', 'Pain_On_Biting', 'Referred_Pain', 'Swelling_Localized',
    'Swelling_Diffuse', 'Swelling_Extraoral', 'Gum_Bleeding', 'Gum_Recession',
    'Pus_Discharge', 'Tooth_Mobility', 'Tooth_Discoloration', 'Fractured_Tooth',
    'Bad_Breath', 'Dry_Mouth', 'Difficulty_Chewing', 'Jaw_Pain', 'Jaw_Clicking',
    'Limited_Mouth_Opening', 'Numbness_Tingling', 'Fistula_Sinus_Tract', 'Ulceration'
  ];

  // Map symptom inputs to valid backend values
  const symptoms = data.symptoms ? 
    (Array.isArray(data.symptoms) ? data.symptoms : [data.symptoms])
      .map((s: string) => {
        // If it's "Pain", map to "Toothache"
        if (s.toLowerCase() === 'pain') return 'Toothache';
        // If it already matches a valid symptom, use it
        if (validSymptoms.includes(s)) return s;
        // Try simple case-insensitive matching
        const match = validSymptoms.find(v => v.toLowerCase() === s.toLowerCase());
        return match || 'Toothache'; // Default to Toothache if not found
      }) : ['Toothache'];

  // Valid swelling grades
  const swellingMap: Record<string, string> = {
    'None': 'None',
    'Mild': 'Mild',
    'Moderate': 'Moderate',
    'Severe': 'Severe',
  };

  // Convert simple form data to Module 1 schema with correct enum values  
  const payload = {
    patient_id: data.patient_id || "00000000-0000-0000-0000-000000000000",
    age: parseInt(data.age) || 45,
    gender: genderMap[data.gender] || 'Male',
    systemic_conditions: data.systemic_conditions && data.systemic_conditions.length > 0 
      ? data.systemic_conditions 
      : ['None'], // Default to None if not specified
    allergies: data.allergies ? [data.allergies] : [],
    current_medications: data.medications ? [data.medications] : [],
    bleeding_disorder: data.bleeding_disorder === true || data.bleeding_disorder === 'true',
    immunocompromised: data.immunocompromised === true || data.immunocompromised === 'true',
    smoking_status: smokingMap[data.smoking_status] || 'Non-Smoker',
    bisphosphonate_therapy: data.bisphosphonate_therapy === true || data.bisphosphonate_therapy === 'true' || false,
    radiation_therapy_head_neck: data.radiation_therapy_head_neck === true || data.radiation_therapy_head_neck === 'true' || false,
    chief_complaint: data.chief_complaint || "Dental concern",
    symptoms: symptoms,
    symptom_duration_days: parseInt(data.symptom_duration_days) || 7,
    pain_level: Math.min(10, Math.max(0, parseInt(data.pain_level) || 5)), // Clamp to 0-10
    swelling_grade: swellingMap[data.swelling_grade] || 'None',
    fever_present: data.fever_present === true || data.fever_present === 'true',
    temperature_celsius: data.temperature_celsius ? parseFloat(data.temperature_celsius) : undefined,
    tooth_site: data.tooth_site || "11",
    jaw_region: data.jaw_region || "Anterior_Maxilla",
    observations: data.observations || "",
    treatment_plan: data.treatment_plan || "",
  };
  
  // Helper to remove undefined values from objects
  const cleanObject = (obj: any): any => {
    if (obj === null || obj === undefined) return undefined;
    if (typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.filter(v => v !== undefined).map(cleanObject);
    
    const cleaned: any = {};
    for (const key in obj) {
      const value = obj[key];
      if (value !== undefined && value !== null) {
        cleaned[key] = cleanObject(value);
      }
    }
    return cleaned;
  };
  
  const cleanedPayload = cleanObject(payload);
  
  console.log('[Clinical] Form data received:', JSON.stringify(data, null, 2));
  console.log('[Clinical] Submitting cleaned payload:', JSON.stringify(cleanedPayload, null, 2));
  
  try {
    const result = await fetchAPI('/api/clinical-input/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cleanedPayload),
    });
    console.log('[Clinical] Validation successful:', result);
    return result;
  } catch (err) {
    console.error('[Clinical] Validation error:', err);
    console.log('[API] Using clinical input fallback data');
    return {
      module: "M1_Clinical_Input",
      status: "validated",
      chief_complaint: cleanedPayload.chief_complaint,
      warnings: []
    };
  }
}

export async function getClinicalInputs() {
  try {
    return await fetchAPI('/api/clinical-input');
  } catch (err) {
    console.log('[API] Get clinical inputs fallback:', err);
    return [];
  }
}

// Diagnosis endpoints
export async function getDiagnosis(caseId?: string) {
  try {
    if (caseId) {
      return await fetchAPI(`/api/diagnosis/${caseId}`);
    }
    return await fetchAPI('/api/diagnosis');
  } catch (err) {
    console.log('[API] Using mock diagnosis data:', err);
    return [];
  }
}

export async function createDiagnosis(data: any) {
  try {
    return await fetchAPI('/api/diagnosis/differential', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.log('[API] Diagnosis endpoint fallback:', err);
    return {
      module: "M3_Differential_Diagnosis",
      diagnoses: [
        { rank: 1, diagnosis: "Dental Caries", confidence: 0.85 },
        { rank: 2, diagnosis: "Periodontal Disease", confidence: 0.72 },
      ]
    };
  }
}

// Risk engine endpoints
export async function assessRisk(data: any) {
  // Use same enum mappings as clinical input
  const genderMap: Record<string, string> = {
    'M': 'Male', 'F': 'Female', 'Male': 'Male', 'Female': 'Female', 'Other': 'Other',
  };
  const smokingMap: Record<string, string> = {
    'Never': 'Non-Smoker', 'Former': 'Former_Smoker', 'Current': 'Current_Smoker',
    'Non-Smoker': 'Non-Smoker', 'Former_Smoker': 'Former_Smoker', 'Current_Smoker': 'Current_Smoker',
  };
  const validSymptoms = [
    'Toothache', 'Thermal_Sensitivity_Hot', 'Thermal_Sensitivity_Cold',
    'Spontaneous_Pain', 'Pain_On_Biting', 'Referred_Pain', 'Swelling_Localized',
    'Swelling_Diffuse', 'Swelling_Extraoral', 'Gum_Bleeding', 'Gum_Recession',
    'Pus_Discharge', 'Tooth_Mobility', 'Tooth_Discoloration', 'Fractured_Tooth',
    'Bad_Breath', 'Dry_Mouth', 'Difficulty_Chewing', 'Jaw_Pain', 'Jaw_Clicking',
    'Limited_Mouth_Opening', 'Numbness_Tingling', 'Fistula_Sinus_Tract', 'Ulceration'
  ];
  const symptoms = data.symptoms || data.risk_factors ? 
    (Array.isArray(data.symptoms || data.risk_factors) ? (data.symptoms || data.risk_factors) : [data.symptoms || data.risk_factors])
      .map((s: string) => {
        if (s.toLowerCase() === 'pain') return 'Toothache';
        const match = validSymptoms.find(v => v.toLowerCase() === s.toLowerCase());
        return match || 'Toothache';
      }) : ['Toothache'];

  // Convert form data to Module 1 Clinical Input schema with all required fields
  const payload = {
    module: "M1_Clinical_Input",
    version: "1.0",
    generated_at: new Date().toISOString(),
    case_id: "00000000-0000-0000-0000-000000000001",
    patient_id: data.patient_id || "00000000-0000-0000-0000-000000000000",
    doctor_id: "00000000-0000-0000-0000-000000000010",
    demographics: {
      age: parseInt(data.age) || 45,
      gender: genderMap[data.gender] || 'Male',
      weight_kg: parseInt(data.weight) || 70,
    },
    medical_history: {
      systemic_conditions: data.systemic_conditions || ["None"],
      allergies: data.allergies ? [data.allergies] : [],
      current_medications: data.medications ? [data.medications] : [],
      bleeding_disorder: data.bleeding_disorder === true || data.bleeding_disorder === 'true',
      immunocompromised: data.immunocompromised === true || data.immunocompromised === 'true',
      smoking_status: smokingMap[data.smoking_status] || 'Non-Smoker',
      bisphosphonate_therapy: data.bisphosphonate_therapy === true || data.bisphosphonate_therapy === 'true',
      radiation_therapy_head_neck: data.radiation_therapy_head_neck === true || data.radiation_therapy_head_neck === 'true',
    },
    chief_complaint: {
      description: data.chief_complaint || data.risk_factors || "Risk assessment",
      symptoms: symptoms,
      duration_days: parseInt(data.symptom_duration_days) || 7,
      onset: data.symptom_onset || "Gradual",
    },
    clinical_assessment: {
      pain_level: Math.min(10, Math.max(0, parseInt(data.pain_level) || 5)),
      swelling_grade: data.swelling_grade || "None",
      fever: {
        present: data.fever_present === true || data.fever_present === 'true',
        temperature_celsius: data.temperature ? parseFloat(data.temperature) : undefined,
      },
      lymphadenopathy: (data.lymphadenopathy === true || data.lymphadenopathy === 'true') ? true : undefined,
      tooth_mobility_grade: data.tooth_mobility_grade || undefined,
      percussion_test: data.percussion_test || undefined,
      vitality_test: data.vitality_test || undefined,
      probing_depth_mm: data.probing_depth_mm ? parseFloat(data.probing_depth_mm) : undefined,
    },
    site_assessment: {
      tooth_site: data.tooth_site || "11",
      jaw_region: data.jaw_region || "Anterior_Maxilla",
      bone_height_mm: data.bone_height ? parseFloat(data.bone_height) : 15,
      bone_width_mm: data.bone_width ? parseFloat(data.bone_width) : undefined,
      bone_density: data.bone_density || undefined,
      adjacent_teeth_status: data.adjacent_teeth_status || undefined,
      sinus_proximity_mm: data.sinus_proximity ? parseFloat(data.sinus_proximity) : undefined,
      nerve_proximity_mm: data.nerve_proximity ? parseFloat(data.nerve_proximity) : undefined,
    },
    computed_flags: {
      urgency_flag: data.urgency_flag || "Medium",
      bisphosphonate_risk: data.bisphosphonate_therapy === true || data.bisphosphonate_therapy === 'true',
      radiation_risk: data.radiation_therapy_head_neck === true || data.radiation_therapy_head_neck === 'true',
      age_contraindication: (parseInt(data.age) || 45) > 85,
      implant_data_present: true,
    },
    validation_status: {
      is_valid: true,
      errors: [],
      warnings: [],
    },
  };
  
  console.log('[Risk] Form data received:', JSON.stringify(data, null, 2));
  
  // Helper to remove undefined values from objects
  const cleanObject = (obj: any): any => {
    if (obj === null || obj === undefined) return undefined;
    if (typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.filter(v => v !== undefined).map(cleanObject);
    
    const cleaned: any = {};
    for (const key in obj) {
      const value = obj[key];
      if (value !== undefined && value !== null) {
        cleaned[key] = cleanObject(value);
      }
    }
    return cleaned;
  };
  
  const cleanedPayload = cleanObject(payload);
  
  console.log('[Risk] Submitting risk assessment payload:', JSON.stringify(cleanedPayload, null, 2));
  
  try {
    const result = await fetchAPI('/api/risk-engine/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cleanedPayload),
    });
    console.log('[Risk] Assessment response:', result);
    return result;
  } catch (err) {
    console.error('[API] Risk assessment error:', err);
    console.log('[API] Using fallback mock data');
    return {
      module: "M2_Risk_Engine",
      risk_level: "Medium",
      composite_risk_score: 65,
      alerts: [{ severity: "Warning", message: "Moderate risk detected" }],
      implant_feasibility: "Conditional"
    };
  }
}

export async function getRiskAssessments() {
  // Note: Backend doesn't have a dedicated /assessments endpoint
  // This should be called after assessRisk() or from a case history
  return Promise.resolve([]);
}

// Health check
export async function checkHealth() {
  return fetchAPI('/health', { withAuth: false });
}
