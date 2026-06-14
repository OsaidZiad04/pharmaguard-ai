import type {
  CounselingRequest,
  CounselingResponse,
  DrugLookupResponse,
  PatientContext,
  PrescriptionAnalysisResponse
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function analyzePrescription(
  rawText: string,
  patientContext?: PatientContext
): Promise<PrescriptionAnalysisResponse> {
  return request<PrescriptionAnalysisResponse>("/prescriptions/analyze-text", {
    method: "POST",
    body: JSON.stringify({
      raw_text: rawText,
      patient_context: patientContext
    })
  });
}

export function getDrug(drugName: string): Promise<DrugLookupResponse> {
  return request<DrugLookupResponse>(`/drugs/${encodeURIComponent(drugName)}`);
}

export function generateCounseling(
  payload: CounselingRequest
): Promise<CounselingResponse> {
  return request<CounselingResponse>("/counseling/generate", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
