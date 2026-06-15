"use client";

import { useRef, useState } from "react";
import { CheckCircle2, FileWarning, ImageUp, ShieldAlert, Upload } from "lucide-react";

import { confirmOcrText, uploadPrescriptionImage } from "@/lib/api";
import type { OcrImageUploadResponse, PrivacyWarning } from "@/lib/types";

interface PrescriptionImageUploadCardProps {
  onUseCorrectedText: (correctedText: string) => void;
}

export function PrescriptionImageUploadCard({
  onUseCorrectedText
}: PrescriptionImageUploadCardProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [ocrResult, setOcrResult] = useState<OcrImageUploadResponse | null>(null);
  const [correctedText, setCorrectedText] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);

  async function handleUpload() {
    if (!selectedFile) {
      return;
    }

    setIsUploading(true);
    setError(null);
    setStatusMessage(null);

    try {
      const result = await uploadPrescriptionImage(selectedFile);
      setOcrResult(result);
      setCorrectedText(result.extracted_text);
      setSelectedFile(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "OCR upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleUseCorrectedText() {
    if (!ocrResult || correctedText.trim().length === 0) {
      return;
    }

    setIsConfirming(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await confirmOcrText({
        extracted_text: ocrResult.extracted_text,
        corrected_text: correctedText
      });
      if (response.can_send_to_analysis) {
        onUseCorrectedText(response.corrected_text);
        setStatusMessage("Corrected text is ready in the prescription text panel.");
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "OCR correction failed.");
    } finally {
      setIsConfirming(false);
    }
  }

  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Prescription Image Intake</h2>
          <p className="text-sm text-pharma-muted">Synthetic image upload only</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-900">
          <ShieldAlert aria-hidden="true" size={15} />
          Pharmacist correction required
        </div>
      </div>

      <div className="flex flex-col gap-3 rounded-md border border-dashed border-pharma-line bg-emerald-50/40 p-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="flex min-w-0 flex-1 items-center gap-3 text-sm text-pharma-ink">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-white text-pharma-teal shadow-sm">
            <ImageUp aria-hidden="true" size={19} />
          </span>
          <span className="min-w-0">
            <span className="block font-medium">Upload PNG, JPG, JPEG, or WEBP</span>
            <span className="block truncate text-pharma-muted">
              {selectedFile ? selectedFile.name : "No image selected"}
            </span>
          </span>
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            className="sr-only"
          />
        </label>
        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className="inline-flex min-w-32 items-center justify-center gap-2 rounded-md bg-pharma-teal px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          <Upload aria-hidden="true" size={16} />
          {isUploading ? "Extracting" : "Extract OCR"}
        </button>
      </div>

      <p className="mt-3 text-sm leading-6 text-pharma-muted">
        OCR output is unverified and must be reviewed by a pharmacist before prescription analysis.
      </p>

      {error && (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      {ocrResult && (
        <div className="mt-5 space-y-4">
          <div className="grid gap-3 text-sm sm:grid-cols-3">
            <StatusItem label="Provider" value={ocrResult.provider_name} />
            <StatusItem
              label="Confidence"
              value={`${Math.round(ocrResult.confidence_score * 100)}% unverified`}
            />
            <StatusItem label="Analysis status" value="Correction required" />
          </div>

          <PrivacyWarnings warnings={ocrResult.privacy_warnings} />

          <div>
            <div className="mb-2 flex items-center justify-between gap-3">
              <label
                htmlFor="ocr-corrected-text"
                className="text-sm font-semibold text-pharma-ink"
              >
                Pharmacist-corrected OCR text
              </label>
              <span className="text-xs font-medium text-amber-800">Draft OCR text</span>
            </div>
            <textarea
              id="ocr-corrected-text"
              value={correctedText}
              onChange={(event) => setCorrectedText(event.target.value)}
              rows={7}
              className="min-h-44 w-full rounded-md border border-pharma-line bg-white p-4 text-sm leading-6 text-pharma-ink outline-none transition placeholder:text-gray-400 focus:border-pharma-teal focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {statusMessage ? (
              <div className="inline-flex items-center gap-2 text-sm font-medium text-emerald-700">
                <CheckCircle2 aria-hidden="true" size={16} />
                {statusMessage}
              </div>
            ) : (
              <div className="inline-flex items-center gap-2 text-sm text-pharma-muted">
                <FileWarning aria-hidden="true" size={16} />
                Corrected text is not analyzed until confirmed here.
              </div>
            )}
            <button
              type="button"
              onClick={handleUseCorrectedText}
              disabled={isConfirming || correctedText.trim().length === 0}
              className="inline-flex items-center justify-center gap-2 rounded-md border border-pharma-teal px-4 py-2.5 text-sm font-semibold text-pharma-teal transition hover:bg-emerald-50 disabled:cursor-not-allowed disabled:border-gray-300 disabled:text-gray-400"
            >
              <CheckCircle2 aria-hidden="true" size={16} />
              {isConfirming ? "Confirming" : "Use corrected text for prescription analysis"}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-pharma-line bg-white px-3 py-2">
      <div className="text-xs font-medium uppercase text-pharma-muted">{label}</div>
      <div className="mt-1 break-words font-semibold text-pharma-ink">{value}</div>
    </div>
  );
}

function PrivacyWarnings({ warnings }: { warnings: PrivacyWarning[] }) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 p-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-amber-900">
        <ShieldAlert aria-hidden="true" size={16} />
        Privacy warnings
      </div>
      <ul className="space-y-1 text-sm leading-6 text-amber-900">
        {warnings.map((warning, index) => (
          <li key={`${warning.code}-${index}`}>{warning.message}</li>
        ))}
      </ul>
    </div>
  );
}
