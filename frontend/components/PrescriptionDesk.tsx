"use client";

import { useMemo, useState } from "react";
import { ShieldAlert } from "lucide-react";

import { analyzePrescription, generateCounseling, getDrug } from "@/lib/api";
import type {
  CounselingResponse,
  DrugLookupResponse,
  PrescriptionAnalysisResponse,
  RetrievedChunk,
  SafetyAlert
} from "@/lib/types";
import { AppHeader } from "@/components/AppHeader";
import { DrugInfoCard } from "@/components/DrugInfoCard";
import { KnowledgeBaseContextPanel } from "@/components/KnowledgeBaseContextPanel";
import { PatientCounselingSheet } from "@/components/PatientCounselingSheet";
import { PharmacistReviewPanel } from "@/components/PharmacistReviewPanel";
import {
  OcrWorkflowStatus,
  PrescriptionImageUploadCard
} from "@/components/PrescriptionImageUploadCard";
import { PrescriptionIntakeCard } from "@/components/PrescriptionIntakeCard";
import { SafetyAlertPanel } from "@/components/SafetyAlertPanel";
import { SafetyReviewPanel } from "@/components/SafetyReviewPanel";
import { SourceGroundingPanel } from "@/components/SourceGroundingPanel";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { WorkflowStatusPanel, WorkflowStatusStep } from "@/components/WorkflowStatusPanel";

const SAMPLE_TEXT =
  "Rx: Paracetamol 500 mg tablets. Take 1 tablet every 6 hours as needed. Synthetic adult case; no real patient data.";

export function PrescriptionDesk() {
  const [prescriptionText, setPrescriptionText] = useState(SAMPLE_TEXT);
  const [analysis, setAnalysis] = useState<PrescriptionAnalysisResponse | null>(null);
  const [drugLookup, setDrugLookup] = useState<DrugLookupResponse | null>(null);
  const [counseling, setCounseling] = useState<CounselingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [ocrWorkflowStatus, setOcrWorkflowStatus] = useState<OcrWorkflowStatus>({
    ocrUnverified: false,
    correctionRequired: false,
    correctedTextReady: false,
    possibleIdentifierWarningCount: 0
  });

  const alerts = useMemo(
    () =>
      dedupeAlerts([
        ...(analysis?.safety_alerts ?? []),
        ...(drugLookup?.safety_alerts ?? []),
        ...(counseling?.safety_alerts ?? [])
      ]),
    [analysis, drugLookup, counseling]
  );

  const knowledgeChunks = useMemo(
    () =>
      dedupeChunks([
        ...(drugLookup?.retrieved_chunks ?? []),
        ...(drugLookup?.rag_drug_card?.retrieved_sources ?? []),
        ...(counseling?.retrieved_sources ?? [])
      ]),
    [drugLookup, counseling]
  );

  const insufficientKnowledgeBaseContext =
    Boolean(drugLookup?.insufficient_context) ||
    Boolean(counseling?.insufficient_context) ||
    alerts.some((alert) => alert.code === "INSUFFICIENT_KNOWLEDGE_BASE_CONTEXT");

  const workflowSteps = useMemo<WorkflowStatusStep[]>(
    () =>
      buildWorkflowSteps({
        ocrWorkflowStatus,
        analysis,
        knowledgeChunks,
        counseling,
        insufficientKnowledgeBaseContext
      }),
    [ocrWorkflowStatus, analysis, knowledgeChunks, counseling, insufficientKnowledgeBaseContext]
  );

  async function handleAnalyze() {
    setIsAnalyzing(true);
    setError(null);
    setCounseling(null);
    setDrugLookup(null);

    try {
      const nextAnalysis = await analyzePrescription(prescriptionText);
      setAnalysis(nextAnalysis);

      const firstMedication = nextAnalysis.extracted_medications[0];
      if (firstMedication) {
        const nextLookup = await getDrug(firstMedication.name);
        setDrugLookup(nextLookup);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleUseCorrectedOcrText(correctedText: string) {
    setPrescriptionText(correctedText);
    setAnalysis(null);
    setDrugLookup(null);
    setCounseling(null);
    setError(null);
  }

  async function handleGenerateCounseling() {
    const medication = analysis?.extracted_medications[0];
    if (!medication) {
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const nextCounseling = await generateCounseling({
        medication: {
          name: medication.name,
          strength: medication.strength,
          directions: medication.directions,
          pharmacist_confirmed: true
        },
        patient_context_confirmed: false,
        additional_notes: "Draft generated from synthetic review flow."
      });
      setCounseling(nextCounseling);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Counseling generation failed.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="min-h-screen bg-pharma-wash">
      <AppHeader />
      <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-6 sm:px-6 lg:px-8">
        <section className="flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
          <ShieldAlert aria-hidden="true" className="mt-0.5 shrink-0" size={20} />
          <p className="text-sm leading-6">
            Safety-first: PharmaGuard AI provides draft support for pharmacists only. It does not make final
            medical decisions and must not be used with real patient data in this scaffold.
          </p>
        </section>

        <WorkflowStepper />
        <WorkflowStatusPanel steps={workflowSteps} />

        {error && (
          <section className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </section>
        )}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="space-y-5">
            <div>
              <SectionLabel title="Intake and correction" detail="OCR must be confirmed before analysis" />
              <PrescriptionImageUploadCard
                onUseCorrectedText={handleUseCorrectedOcrText}
                onWorkflowStatusChange={setOcrWorkflowStatus}
              />
            </div>
            <PrescriptionIntakeCard
              value={prescriptionText}
              isLoading={isAnalyzing}
              onChange={setPrescriptionText}
              onAnalyze={handleAnalyze}
              onLoadSample={() => setPrescriptionText(SAMPLE_TEXT)}
            />
            <PatientCounselingSheet counseling={counseling} />
          </div>

          <div className="space-y-5">
            <SectionLabel title="Review and grounding" detail="Retrieved context remains draft support" />
            <SafetyReviewPanel
              ocrUnverified={ocrWorkflowStatus.ocrUnverified}
              correctionRequired={ocrWorkflowStatus.correctionRequired}
              correctedTextReady={ocrWorkflowStatus.correctedTextReady}
              possibleIdentifierWarningCount={ocrWorkflowStatus.possibleIdentifierWarningCount}
              ragSourcesAvailable={knowledgeChunks.length > 0}
              insufficientKnowledgeBaseContext={insufficientKnowledgeBaseContext}
              counselingDraftReady={Boolean(counseling)}
              pharmacistReviewRequired
            />
            <PharmacistReviewPanel
              analysis={analysis}
              isGenerating={isGenerating}
              onGenerateCounseling={handleGenerateCounseling}
            />
            <DrugInfoCard lookup={drugLookup} />
            <SourceGroundingPanel
              chunks={knowledgeChunks}
              insufficientContext={insufficientKnowledgeBaseContext}
            />
            <KnowledgeBaseContextPanel chunks={knowledgeChunks} />
            <SafetyAlertPanel alerts={alerts} />
          </div>
        </div>
      </div>
    </main>
  );
}

function SectionLabel({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="mb-3 flex flex-col gap-1">
      <p className="text-xs font-semibold uppercase tracking-wide text-pharma-teal">{title}</p>
      <p className="text-sm text-pharma-muted">{detail}</p>
    </div>
  );
}

function buildWorkflowSteps({
  ocrWorkflowStatus,
  analysis,
  knowledgeChunks,
  counseling,
  insufficientKnowledgeBaseContext
}: {
  ocrWorkflowStatus: OcrWorkflowStatus;
  analysis: PrescriptionAnalysisResponse | null;
  knowledgeChunks: RetrievedChunk[];
  counseling: CounselingResponse | null;
  insufficientKnowledgeBaseContext: boolean;
}): WorkflowStatusStep[] {
  const hasMedication = Boolean(analysis?.extracted_medications.length);
  const hasSources = knowledgeChunks.length > 0;

  return [
    {
      label: "OCR Intake",
      status: ocrWorkflowStatus.ocrUnverified ? "completed" : "waiting",
      summary: ocrWorkflowStatus.ocrUnverified
        ? "OCR captured as unverified."
        : "Upload synthetic image or use text input."
    },
    {
      label: "Pharmacist Correction",
      status: ocrWorkflowStatus.correctedTextReady
        ? "completed"
        : ocrWorkflowStatus.correctionRequired
          ? "required"
          : "waiting",
      summary: ocrWorkflowStatus.correctedTextReady
        ? "Corrected text is ready for analysis."
        : "Correction is required before analysis."
    },
    {
      label: "Prescription Analysis",
      status: analysis ? "completed" : ocrWorkflowStatus.correctedTextReady ? "ready" : "waiting",
      summary: analysis ? "Corrected or entered text analyzed." : "Waiting for confirmed text."
    },
    {
      label: "Medication Extraction",
      status: analysis ? (hasMedication ? "completed" : "blocked") : "waiting",
      summary: hasMedication ? "Medication candidate extracted." : "No supported medication confirmed yet."
    },
    {
      label: "RAG Source Check",
      status: insufficientKnowledgeBaseContext ? "blocked" : hasSources ? "completed" : "waiting",
      summary: hasSources ? "Local source context retrieved." : "Sources appear after medication match."
    },
    {
      label: "Counseling Draft",
      status: counseling ? "completed" : insufficientKnowledgeBaseContext ? "blocked" : hasMedication ? "ready" : "waiting",
      summary: counseling ? "Draft-only counseling generated." : "Requires pharmacist confirmation."
    },
    {
      label: "Pharmacist Review",
      status: "required",
      summary: "Mandatory before patient-facing use."
    }
  ];
}

function dedupeAlerts(alerts: SafetyAlert[]) {
  const seen = new Set<string>();
  return alerts.filter((alert) => {
    const key = `${alert.code}:${alert.message}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function dedupeChunks(chunks: RetrievedChunk[]) {
  const seen = new Set<string>();
  return chunks.filter((chunk) => {
    if (seen.has(chunk.chunk_id)) {
      return false;
    }
    seen.add(chunk.chunk_id);
    return true;
  });
}
