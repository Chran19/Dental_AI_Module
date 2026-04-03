/**
 * Print Utilities - Generate formatted patient records for printing
 */

import { Patient } from '@/lib/types/patient';

export interface PrintOptions {
  title?: string;
  showHeader?: boolean;
  showFooter?: boolean;
  includeAllergies?: boolean;
  includeMedicalHistory?: boolean;
  includeContactInfo?: boolean;
}

/**
 * Generate formatted HTML for patient records
 */
function generatePatientRecordHTML(patient: Patient, options: PrintOptions = {}): string {
  const {
    title = 'Patient Medical Record',
    showHeader = true,
    showFooter = true,
    includeAllergies = true,
    includeMedicalHistory = true,
    includeContactInfo = true,
  } = options;

  // Helper functions
  const getAge = (dobStr: string | null | undefined): number | null => {
    if (!dobStr) return null;
    const today = new Date();
    const birthDate = new Date(dobStr);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const formatDate = (dateStr: string | null | undefined): string => {
    if (!dateStr) return 'Not provided';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const fullName = `${patient.first_name} ${patient.last_name}`;
  const dob = patient.dob || patient.date_of_birth;
  const age = getAge(dob);
  const gender = patient.gender || 'Not specified';
  const email = patient.contact_email || patient.email || 'Not provided';
  const phone = patient.contact_phone || patient.phone || 'Not provided';
  const allergies = patient.medical_history?.allergies || [];
  const conditions = patient.medical_history?.conditions || [];
  const reasonOfVisit = patient.reason_of_visit || patient.medical_history?.reason_of_visit;

  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const css = `
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        color: #1f2937;
        background: #fff;
        line-height: 1.6;
      }

      .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 40px;
      }

      /* ═══════════════════════════════════════════════════════════════ */
      /* HEADER */
      /* ═══════════════════════════════════════════════════════════════ */
      .header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 35px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
      }

      .clinic-name {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
      }

      .record-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        opacity: 0.95;
      }

      .record-meta {
        font-size: 11px;
        display: flex;
        justify-content: space-between;
        opacity: 0.85;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        padding-top: 10px;
        margin-top: 10px;
      }

      /* ═══════════════════════════════════════════════════════════════ */
      /* PATIENT NAME SECTION */
      /* ═══════════════════════════════════════════════════════════════ */
      .patient-name-section {
        background: linear-gradient(to right, #f3f4f6, #ffffff);
        border-left: 5px solid #4f46e5;
        padding: 20px 25px;
        border-radius: 8px;
        margin-bottom: 35px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      }

      .patient-name {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
      }

      .patient-id {
        font-size: 12px;
        color: #6b7280;
        letter-spacing: 0.5px;
        font-family: 'Courier New', monospace;
      }

      /* ═══════════════════════════════════════════════════════════════ */
      /* TWO-COLUMN LAYOUT */
      /* ═══════════════════════════════════════════════════════════════ */
      .content-wrapper {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        margin-bottom: 35px;
      }

      .content-column {
        display: flex;
        flex-direction: column;
        gap: 25px;
      }

      /* ═══════════════════════════════════════════════════════════════ */
      /* SECTION STYLES */
      /* ═══════════════════════════════════════════════════════════════ */
      .section {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 20px;
        transition: all 0.2s ease;
      }

      .section:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #d1d5db;
      }

      .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #fff;
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        padding: 10px 12px;
        margin: -20px -20px 15px -20px;
        border-radius: 8px 8px 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* INFO GRID */
      /* ─────────────────────────────────────────────────────────────── */
      .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 8px;
      }

      .info-grid.full {
        grid-template-columns: 1fr;
      }

      .info-item {
        padding-bottom: 0;
      }

      .info-label {
        font-size: 10px;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        display: block;
      }

      .info-value {
        font-size: 14px;
        font-weight: 500;
        color: #1f2937;
      }

      .info-value.placeholder {
        color: #9ca3af;
        font-style: italic;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* ALERT BOX */
      /* ─────────────────────────────────────────────────────────────── */
      .alert {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 0;
        border-left: 5px solid;
      }

      .alert-danger {
        background: #fef2f2;
        border-left-color: #dc2626;
        color: #991b1b;
      }

      .alert-danger .alert-title {
        font-weight: 700;
        margin-bottom: 8px;
        font-size: 13px;
      }

      .alert-danger ul {
        margin-left: 18px;
        margin-top: 6px;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* LIST STYLES */
      /* ─────────────────────────────────────────────────────────────── */
      .list-items {
        list-style: none;
        margin: 0;
        padding: 0;
      }

      .list-items li {
        padding: 6px 0;
        padding-left: 22px;
        position: relative;
        font-size: 13px;
        color: #374151;
      }

      .list-items li:before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #10b981;
        font-weight: bold;
        font-size: 14px;
      }

      .alert-danger .list-items li:before {
        content: '⚠';
        color: #dc2626;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* BADGE */
      /* ─────────────────────────────────────────────────────────────── */
      .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
      }

      .badge-blue {
        background: #dbeafe;
        color: #1e40af;
      }

      .badge-red {
        background: #fee2e2;
        color: #991b1b;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* REASON BOX */
      /* ─────────────────────────────────────────────────────────────── */
      .reason-box {
        padding: 14px;
        background: #f0f9ff;
        border-left: 4px solid #4f46e5;
        border-radius: 6px;
        font-size: 13px;
        line-height: 1.6;
        color: #1e3a8a;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* FOOTER */
      /* ─────────────────────────────────────────────────────────────── */
      .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid #e5e7eb;
        font-size: 11px;
        color: #9ca3af;
        text-align: center;
      }

      .footer p {
        margin: 6px 0;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* PRINT STYLES */
      /* ─────────────────────────────────────────────────────────────── */
      @media print {
        .container {
          padding: 20px;
        }

        .section {
          page-break-inside: avoid;
        }

        .content-wrapper {
          page-break-inside: avoid;
        }

        body {
          background: white;
        }

        .header {
          box-shadow: none;
        }

        .section {
          box-shadow: none;
          border: 1px solid #d1d5db;
        }
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* EMPTY STATE */
      /* ─────────────────────────────────────────────────────────────── */
      .empty {
        font-size: 13px;
        color: #9ca3af;
        font-style: italic;
        padding: 12px 0;
      }

      /* ─────────────────────────────────────────────────────────────── */
      /* DIVIDER */
      /* ─────────────────────────────────────────────────────────────── */
      .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 12px 0;
      }
    </style>
  `;

  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${fullName} - ${title}</title>
      ${css}
    </head>
    <body>
      <div class="container">
        ${showHeader ? `
          <div class="header">
            <div class="clinic-name">🦷 Dental Clinic Management System</div>
            <div class="record-title">${title}</div>
            <div class="record-meta">
              <span>📅 Generated: ${currentDate}</span>
              <span>📋 Document ID: ${patient.id?.substring(0, 12)}</span>
            </div>
          </div>
        ` : ''}

        <!-- PATIENT OVERVIEW -->
        <div class="patient-name-section">
          <div class="patient-name">${fullName}</div>
          <div class="patient-id">Patient ID: ${patient.id}</div>
        </div>

        <!-- TWO-COLUMN CONTENT LAYOUT -->
        <div class="content-wrapper">
          <!-- LEFT COLUMN -->
          <div class="content-column">
            ${includeContactInfo ? `
              <!-- CONTACT INFORMATION SECTION -->
              <div class="section">
                <div class="section-title">👤 Personal Information</div>
                <div class="info-grid full">
                  <div class="info-item">
                    <span class="info-label">Date of Birth</span>
                    <div class="info-value">
                      ${dob ? formatDate(dob) : '--'}
                    </div>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Age</span>
                    <div class="info-value">
                      ${age !== null ? `${age} years` : '--'}
                    </div>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Gender</span>
                    <div class="info-value">${gender}</div>
                  </div>
                </div>
              </div>

              <!-- CONTACT DETAILS SECTION -->
              <div class="section">
                <div class="section-title">📞 Contact Details</div>
                <div class="info-grid full">
                  <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <div class="info-value">${email}</div>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <div class="info-value">${phone}</div>
                  </div>
                </div>
              </div>
            ` : ''}

            ${reasonOfVisit ? `
              <!-- REASON OF VISIT SECTION -->
              <div class="section">
                <div class="section-title">📝 Reason of Visit</div>
                <div class="reason-box">${reasonOfVisit}</div>
              </div>
            ` : ''}
          </div>

          <!-- RIGHT COLUMN -->
          <div class="content-column">
            ${includeMedicalHistory ? `
              <!-- MEDICAL CONDITIONS SECTION -->
              <div class="section">
                <div class="section-title">⚕️ Medical History</div>
                ${conditions.length > 0 ? `
                  <div>
                    <div class="info-label" style="margin-bottom: 10px;">Medical Conditions</div>
                    <div>
                      ${conditions.map((condition: string) => `<span class="badge badge-blue">${condition}</span>`).join('')}
                    </div>
                  </div>
                ` : `<div class="empty">No medical conditions recorded</div>`}
              </div>
            ` : ''}

            ${includeAllergies && allergies.length > 0 ? `
              <!-- ALLERGIES WARNING SECTION -->
              <div class="alert alert-danger">
                <div class="alert-title">⚠️ Known Allergies</div>
                <ul class="list-items">
                  ${allergies.map((allergy: string) => `<li>${allergy}</li>`).join('')}
                </ul>
              </div>
            ` : includeAllergies ? `
              <div class="section">
                <div class="section-title">✅ Allergies</div>
                <div class="empty">No known allergies recorded</div>
              </div>
            ` : ''}

            <!-- RECORD METADATA SECTION -->
            <div class="section">
              <div class="section-title">📂 Record Information</div>
              <div class="info-grid full">
                <div class="info-item">
                  <span class="info-label">Registration Date</span>
                  <div class="info-value">${formatDate(patient.created_at || null)}</div>
                </div>
                <div class="info-item">
                  <span class="info-label">Last Updated</span>
                  <div class="info-value">${formatDate(patient.updated_at || null)}</div>
                </div>
                ${patient.doctor_id ? `
                  <div class="info-item">
                    <span class="info-label">Assigned Doctor</span>
                    <div class="info-value">${patient.doctor_id.substring(0, 8)}...</div>
                  </div>
                ` : ''}
              </div>
            </div>
          </div>
        </div>

        ${showFooter ? `
          <div class="footer">
            <p>⚖️ This is a confidential medical document. Do not share without patient authorization.</p>
            <p>For inquiries or corrections, contact the clinic administration office.</p>
          </div>
        ` : ''}
      </div>
    </body>
    </html>
  `;

  return html;
}

/**
 * Print patient records using browser print dialog
 */
export function printPatientRecord(patient: Patient, options?: PrintOptions): void {
  try {
    const html = generatePatientRecordHTML(patient, options);
    
    // Create a new window
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      throw new Error('Failed to open print window. Check your pop-up settings.');
    }

    // Write HTML to the new window
    printWindow.document.write(html);
    printWindow.document.close();

    // Wait for content to load, then print
    printWindow.onload = () => {
      printWindow.print();
    };

    console.log('[PrintUtils] Patient record print dialog opened');
  } catch (error) {
    console.error('[PrintUtils] Failed to print patient record:', error);
    throw error;
  }
}

/**
 * Export patient record as HTML file
 */
export function exportPatientRecordHTML(patient: Patient, options?: PrintOptions): void {
  try {
    const html = generatePatientRecordHTML(patient, options);
    const blob = new Blob([html], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${patient.first_name}_${patient.last_name}_Medical_Record_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('[PrintUtils] Patient record exported as HTML');
  } catch (error) {
    console.error('[PrintUtils] Failed to export patient record:', error);
    throw error;
  }
}

/**
 * Export patient record as PDF (requires PDF library)
 * This creates an HTML that can be saved as PDF using browser's print dialog
 */
export function exportPatientRecordPDF(patient: Patient, options?: PrintOptions): void {
  try {
    // For now, we'll use the print dialog which allows Save as PDF
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      throw new Error('Failed to open PDF window. Check your pop-up settings.');
    }

    const html = generatePatientRecordHTML(patient, options);
    printWindow.document.write(html);
    printWindow.document.close();

    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print();
      }, 250);
    };

    console.log('[PrintUtils] Patient record PDF export dialog opened (use "Save as PDF")');
  } catch (error) {
    console.error('[PrintUtils] Failed to export patient record as PDF:', error);
    throw error;
  }
}
