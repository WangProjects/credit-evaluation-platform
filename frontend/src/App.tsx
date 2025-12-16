import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AuditEvent, FairnessReport, ScorePayload, ScoreResult } from "./types";
import { fetchAuditEvents, scoreApplicant } from "./lib/api";
import { Navbar } from "./components/Navbar";
import { Hero } from "./components/Hero";
import { ScoreForm } from "./components/ScoreForm";
import { MetricsGrid } from "./components/MetricsGrid";
import { AuditTable } from "./components/AuditTable";
import { FairnessPanel } from "./components/FairnessPanel";

export default function App() {
  const [score, setScore] = useState<ScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fairness, setFairness] = useState<FairnessReport | null>(null);

  const auditQuery = useQuery<AuditEvent[]>({
    queryKey: ["audit-events"],
    queryFn: async () => (await fetchAuditEvents(25)).events,
  });

  useEffect(() => {
    auditQuery.refetch();
  }, [score?.request_id]); // refresh audit after scoring

  async function handleScore(payload: ScorePayload) {
    try {
      setLoading(true);
      setError(null);
      const res = await scoreApplicant(payload);
      setScore(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to score applicant");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <Navbar onPrimaryAction={() => window.scrollTo({ top: 0, behavior: "smooth" })} />
      <Hero />
      <MetricsGrid score={score} fairness={fairness} />
      <ScoreForm onSubmit={handleScore} loading={loading} />
      {error && (
        <div className="chip" style={{ marginTop: 10, borderColor: "#fca5a5", color: "#fecaca" }}>
          {error}
        </div>
      )}
      <FairnessPanel onFairness={(report) => setFairness(report)} />
      <AuditTable events={auditQuery.data ?? []} loading={auditQuery.isLoading} />
    </div>
  );
}
