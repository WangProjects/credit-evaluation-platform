import React from "react";
import { FeatureContract, HealthResponse, ModelInfo } from "../types";

type Props = {
  health?: HealthResponse | null;
  modelInfo?: ModelInfo | null;
  contract?: FeatureContract | null;
  mode: "live" | "mock";
};

export function Hero({ health, modelInfo, contract, mode }: Props) {
  const featureCount = contract?.feature_definitions.length ?? 0;
  const groups = new Set(contract?.feature_definitions.map((definition) => definition.group) ?? []);

  return (
    <section className="hero-shell glass card">
      <div className="hero-copy">
        <div className="section-title">
          <span className="badge">{mode === "live" ? "Live API" : "Mock mode"}</span>
          <span className="badge">Alt-data</span>
          <span className="badge">Explainable</span>
          <span className="badge">Portfolio analytics</span>
        </div>
        <h1 className="hero-title">Credit decisions, explanations, and monitoring in one working console.</h1>
        <p className="muted hero-blurb">
          Score individual applicants, inspect model contributions, generate fairness snapshots, and run portfolio
          analysis against the active feature contract without storing direct personal identifiers in the UI.
        </p>
        <div className="hero-chip-row">
          <div className="chip">Contract-driven intake</div>
          <div className="chip">Reason codes + contributions</div>
          <div className="chip">Synthetic cohort stress tests</div>
          <div className="chip">Audit event playback</div>
        </div>
      </div>

      <div className="hero-metrics">
        <StatCard label="API status" value={health?.status?.toUpperCase() ?? "CHECKING"} hint={mode} />
        <StatCard
          label="Active model"
          value={modelInfo?.current?.version ?? "Unavailable"}
          hint={modelInfo?.current?.name ?? "No registry entry"}
        />
        <StatCard label="Feature contract" value={String(featureCount)} hint="scored inputs" />
        <StatCard
          label="Decision threshold"
          value={typeof contract?.decision_threshold === "number" ? contract.decision_threshold.toFixed(2) : "—"}
          hint={`${groups.size || 0} feature groups`}
        />
      </div>
    </section>
  );
}

function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="glass stat-card">
      <div className="label">
        <span>{label}</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="muted stat-hint">{hint}</div>
    </div>
  );
}
