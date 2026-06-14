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
import { PrescriptionIntakeCard } from "@/components/PrescriptionIntakeCard";
import { SafetyAlertPanel } from "@/components/SafetyAlertPanel";
import { WorkflowStepper } from "@/components/WorkflowStepper";

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

        {error && (
          <section className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </section>
        )}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="space-y-5">
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
            <PharmacistReviewPanel
              analysis={analysis}
              isGenerating={isGenerating}
              onGenerateCounseling={handleGenerateCounseling}
            />
            <DrugInfoCard lookup={drugLookup} />
            <KnowledgeBaseContextPanel chunks={knowledgeChunks} />
            <SafetyAlertPanel alerts={alerts} />
          </div>
        </div>
      </div>
    </main>
  );
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
