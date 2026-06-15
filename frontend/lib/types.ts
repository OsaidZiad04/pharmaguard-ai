export interface PatientContext {
  age?: number | null;
  pregnancy_status?: string | null;
  allergies?: string[];
  current_medications?: string[];
}

export interface SafetyAlert {
  code: string;
  severity: "info" | "warning" | "critical";
  message: string;
  requires_pharmacist_review: boolean;
}

export interface ExtractedMedication {
  name: string;
  matched_text: string;
  strength?: string | null;
  directions?: string | null;
  source_text: string;
  confidence: number;
  is_known: boolean;
}

export interface PrescriptionAnalysisResponse {
  extracted_medications: ExtractedMedication[];
  confidence_score: number;
  missing_information: string[];
  safety_alerts: SafetyAlert[];
  pharmacist_review_required: boolean;
}

export interface RetrievedChunk {
  chunk_id: string;
  drug_name: string;
  source_file: string;
  section_title: string;
  text: string;
  score: number;
}

export interface RagDrugCard {
  name: string;
  overview: string[];
  key_counseling_points: string[];
  safety_notes: string[];
  pharmacist_checks: string[];
  retrieved_sources: RetrievedChunk[];
  grounded_answer: string;
  insufficient_context: boolean;
  source: string;
  pharmacist_review_required: boolean;
}

export interface DrugCard {
  name: string;
  generic_name: string;
  aliases: string[];
  category: string;
  common_uses: string[];
  pharmacist_notes: string[];
  counseling_points: string[];
  safety_considerations: string[];
  source: string;
  pharmacist_review_required: boolean;
}

export interface DrugLookupResponse {
  found: boolean;
  drug: DrugCard | null;
  rag_drug_card: RagDrugCard | null;
  retrieved_chunks: RetrievedChunk[];
  grounded_answer?: string | null;
  insufficient_context: boolean;
  safety_alerts: SafetyAlert[];
  pharmacist_review_required: boolean;
}

export interface CounselingRequest {
  medication: {
    name: string;
    strength?: string | null;
    directions?: string | null;
    pharmacist_confirmed: boolean;
  };
  patient_context_confirmed: boolean;
  additional_notes?: string | null;
}

export interface CounselingResponse {
  counseling_note: string;
  safety_alerts: SafetyAlert[];
  retrieved_sources: RetrievedChunk[];
  insufficient_context: boolean;
  pharmacist_review_required: boolean;
}

export interface RagQueryResponse {
  query: string;
  retrieved_chunks: RetrievedChunk[];
  grounded_answer: string;
  review_required: boolean;
  insufficient_context: boolean;
}

export interface PrivacyWarning {
  code: string;
  severity: "info" | "warning" | "critical";
  message: string;
}

export interface OcrImageUploadResponse {
  filename: string;
  content_type: string;
  extracted_text: string;
  confidence_score: number;
  provider_name: string;
  unverified_ocr_output: boolean;
  pharmacist_review_required: boolean;
  privacy_warnings: PrivacyWarning[];
  detected_possible_identifiers: string[];
  correction_required: boolean;
  can_send_to_analysis: boolean;
}

export interface OcrCorrectionRequest {
  extracted_text: string;
  corrected_text: string;
}

export interface OcrCorrectionResponse {
  corrected_text: string;
  pharmacist_review_required: boolean;
  correction_required: boolean;
  can_send_to_analysis: boolean;
  privacy_warnings: PrivacyWarning[];
  detected_possible_identifiers: string[];
}
