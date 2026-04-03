/**
 * Dental Clinic Data Store
 * 
 * Provides a unified data layer that:
 * 1. Calls the real backend API (PostgreSQL via FastAPI)
 * 2. Falls back to localStorage when the backend is unreachable
 * 3. Keeps localStorage in sync as a cache layer
 */

import { Patient, PatientCreate } from '@/lib/types/patient';
import { QueueItem } from '@/lib/types/queue';
import { fetchAPI } from '@/lib/api';

// ─── LocalStorage Keys ──────────────────────────────────────────────────────────
const LS_PATIENTS = 'dental_patients';
const LS_QUEUE = 'dental_queue';
const LS_ACTIVITY = 'dental_activity';

// ─── Activity Log ───────────────────────────────────────────────────────────────
export interface ActivityEntry {
  time: string;
  action: string;
  subject: string;
  timestamp: number;
}

function getLocalActivity(): ActivityEntry[] {
  try {
    const data = localStorage.getItem(LS_ACTIVITY);
    return data ? JSON.parse(data) : [];
  } catch { return []; }
}

function saveLocalActivity(entries: ActivityEntry[]) {
  localStorage.setItem(LS_ACTIVITY, JSON.stringify(entries.slice(0, 50)));
}

export function addActivity(action: string, subject: string) {
  const entries = getLocalActivity();
  entries.unshift({
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    action,
    subject,
    timestamp: Date.now(),
  });
  saveLocalActivity(entries);
}

export function getRecentActivity(limit = 10): ActivityEntry[] {
  return getLocalActivity().slice(0, limit);
}

// ─── Patient Store ──────────────────────────────────────────────────────────────

function getLocalPatients(): Patient[] {
  try {
    const data = localStorage.getItem(LS_PATIENTS);
    return data ? JSON.parse(data) : [];
  } catch { return []; }
}

function saveLocalPatients(patients: Patient[]) {
  localStorage.setItem(LS_PATIENTS, JSON.stringify(patients));
}

export async function fetchPatients(): Promise<Patient[]> {
  try {
    const response = await fetchAPI('/patients', { method: 'GET' });
    const patients = Array.isArray(response) ? response : [];
    // Cache in localStorage
    saveLocalPatients(patients);
    return patients;
  } catch (err) {
    console.warn('[Store] Backend unavailable for patients, using local cache:', err);
    return getLocalPatients();
  }
}

export async function fetchPatientById(id: string): Promise<Patient | null> {
  try {
    const patient = await fetchAPI(`/patients/${id}`, { method: 'GET' });
    return patient;
  } catch (err) {
    console.warn('[Store] Backend unavailable for patient detail, using local cache:', err);
    const locals = getLocalPatients();
    return locals.find(p => p.id === id) || null;
  }
}

export async function searchPatients(query: string): Promise<Patient[]> {
  const patients = await fetchPatients();
  if (!query.trim()) return patients;
  const q = query.toLowerCase();
  return patients.filter(p =>
    `${p.first_name} ${p.last_name}`.toLowerCase().includes(q) ||
    p.contact_email?.toLowerCase().includes(q) ||
    p.contact_phone?.includes(q) ||
    p.id.toLowerCase().includes(q)
  );
}

export async function createPatient(data: PatientCreate): Promise<Patient> {
  try {
    const result = await fetchAPI('/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    // Add to local cache
    const locals = getLocalPatients();
    locals.push(result);
    saveLocalPatients(locals);
    addActivity('Patient registered', `${data.first_name} ${data.last_name}`);
    return result;
  } catch (err) {
    console.warn('[Store] Backend unavailable for create patient, saving locally:', err);
    // Fallback: create locally with generated ID
    const localPatient: Patient = {
      id: crypto.randomUUID(),
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    const locals = getLocalPatients();
    locals.push(localPatient);
    saveLocalPatients(locals);
    addActivity('Patient registered (offline)', `${data.first_name} ${data.last_name}`);
    return localPatient;
  }
}

// ─── Queue Store ────────────────────────────────────────────────────────────────

function getLocalQueue(): QueueItem[] {
  try {
    const data = localStorage.getItem(LS_QUEUE);
    return data ? JSON.parse(data) : [];
  } catch { return []; }
}

function saveLocalQueue(items: QueueItem[]) {
  localStorage.setItem(LS_QUEUE, JSON.stringify(items));
}

export async function fetchQueue(): Promise<QueueItem[]> {
  try {
    const response = await fetchAPI('/queue/active', { method: 'GET' });
    const items = Array.isArray(response) ? response : [];
    // Cache
    saveLocalQueue(items);
    return items;
  } catch (err) {
    console.warn('[Store] Backend unavailable for queue, using local cache:', err);
    return getLocalQueue();
  }
}

export async function checkInPatient(
  patientId: string,
  notes?: string,
  reasonOfVisit?: string,
): Promise<QueueItem> {
  try {
    const result = await fetchAPI('/queue/check-in', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: patientId,
        notes: reasonOfVisit ? `Reason: ${reasonOfVisit}${notes ? '. ' + notes : ''}` : notes,
      }),
    });
    
    // Validate response
    if (!result || !result.id) {
      throw new Error('Invalid response from check-in endpoint');
    }
    
    addActivity('Patient checked in', `Queue #${result.id?.substring(0, 8) || 'new'}`);
    return result;
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to check in patient';
    console.error('[Store] Check-in failed:', errorMessage);
    // Re-throw the error to let the caller handle it
    // IMPORTANT: Do NOT create a local queue item here because:
    // - The queue page fetches from backend only, not localStorage
    // - A local-only item will appear to succeed but won't be synced to backend
    // - This creates confusion when the queue page doesn't show the patient
    throw new Error(`Unable to check in patient: ${errorMessage}`);
  }
}

export async function updateQueueStatus(
  queueId: string,
  status: string,
  assignedDoctorId?: string,
): Promise<boolean> {
  try {
    const response = await fetchAPI(`/queue/${queueId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status,
        assigned_doctor_id: assignedDoctorId,
      }),
    });
    
    if (!response) {
      console.error('[Store] Queue status update returned empty response');
      return false;
    }
    
    addActivity('Queue status updated', `${status}`);
    console.log('[Store] Queue status successfully updated to:', status, { response });
    return true;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error('[Store] Failed to update queue status on backend:', errorMsg);
    
    // OFFLINE FALLBACK: Only for non-critical status updates
    // For "Completed" status, we require backend confirmation
    if (status === 'Completed') {
      console.error('[Store] Cannot complete workflow offline - backend confirmation required');
      throw new Error('Backend connection required to complete workflow: ' + errorMsg);
    }
    
    // For other status updates (like In_Consultation), use local fallback
    const locals = getLocalQueue();
    const idx = locals.findIndex(i => i.id === queueId);
    if (idx >= 0) {
      locals[idx].status = status as QueueItem['status'];
      saveLocalQueue(locals);
      console.warn('[Store] Queue status updated locally (offline mode):', status);
    }
    return true;
  }
}

// ─── Stats Helpers ──────────────────────────────────────────────────────────────

export async function getQueueStats() {
  const items = await fetchQueue();
  return {
    totalWaiting: items.filter(i => i.status === 'Waiting').length,
    inConsultation: items.filter(i => i.status === 'In_Consultation').length,
    total: items.length,
  };
}

export async function getDashboardStats() {
  const [patients, queueItems] = await Promise.all([fetchPatients(), fetchQueue()]);
  const today = new Date().toDateString();
  
  return {
    checkedIn: queueItems.length,
    inQueue: queueItems.filter(i => i.status === 'Waiting').length,
    newPatients: patients.filter(p => {
      const created = p.created_at ? new Date(p.created_at).toDateString() : '';
      return created === today;
    }).length,
    totalPatients: patients.length,
  };
}
