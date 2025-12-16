import React from "react";
import { FairnessReport, ScoreResult } from "../types";

type Props = {
  score?: ScoreResult | null;
  fairness?: FairnessReport | null;
};

const formatPct = (v: number | undefined) => (typeof v === "number" ? `${(v * 100).toFixed(1)}%` : "—");

export function MetricsGrid({ score, fairness }: Props) {
  return (
    <section className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", marginTop: 12 }}>
      <div className="glass card">
        <div className="label">
          <span>Decision</span>
          <span className="muted">{score?.model_version ?? "—"}</span>
        </div>
        <h2 style={{ margin: "8px 0" }}>{score?.decision ?? "Waiting..."}</h2>
        <div className="progress" style={{ marginTop: 6 }}>
          <div className="progress-bar" style={{ width: `${((score?.score ?? 0) * 100).toFixed(0)}%` }} />
        </div>
        <div className="muted" style={{ fontSize: 13, marginTop: 6 }}>
          Score: {score ? (score.score * 100).toFixed(1) : "—"} / 100
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 10 }}>
          {(score?.reason_codes || []).map((r) => (
            <span key={r} className="chip">
              {r}
            </span>
          ))}
          {!score && <span className="muted">Reason codes appear after scoring.</span>}
        </div>
      </div>

      <div className="glass card">
        <div className="label">
          <span>Fairness snapshot</span>
          <span className="muted">demo or live API</span>
        </div>
        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", marginTop: 8 }}>
          <Metric name="Demographic parity Δ" value={fairness?.demographic_parity_difference} />
          <Metric name="Equal opportunity Δ" value={fairness?.equal_opportunity_difference} />
        </div>
        <div style={{ marginTop: 12 }}>
          <div className="label">Selection rate by group</div>
          {fairness ? (
            Object.entries(fairness.selection_rate_by_group).map(([g, v]) => (
              <div key={g} style={{ marginTop: 6 }}>
                <div className="label">
                  <span>{g}</span>
                  <span>{formatPct(v)}</span>
                </div>
                <div className="chart-bar">
                  <div className="chart-fill" style={{ width: `${Math.min(100, v * 120)}%` }} />
                </div>
              </div>
            ))
          ) : (
            <p className="muted" style={{ marginTop: 6 }}>
              Run a fairness report to populate this section.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

function Metric({ name, value }: { name: string; value?: number }) {
  const badge =
    value === undefined
      ? { label: "pending", tone: "muted" }
      : Math.abs(value) <= 0.1
        ? { label: "good", tone: "success" }
        : { label: "review", tone: "warn" };

  return (
    <div>
      <div className="label">
        <span>{name}</span>
        <span className={`pill ${badge.tone}`}>{badge.label}</span>
      </div>
      <div style={{ fontSize: 24, fontWeight: 700, marginTop: 4 }}>{formatPct(value)}</div>
    </div>
  );
}
