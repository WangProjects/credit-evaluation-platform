import React from "react";
import { FairnessReport, ScoreResult } from "../types";

type Props = {
  score?: ScoreResult | null;
  fairness?: FairnessReport | null;
};

const formatPct = (value: number | undefined) =>
  typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "—";

export function MetricsGrid({ score, fairness }: Props) {
  return (
    <section className="grid metrics-grid">
      <div className="glass card">
        <div className="label">
          <span>Latest decision</span>
          <span className="muted">{score?.model_version ?? "no score yet"}</span>
        </div>
        <div className="decision-row">
          <div>
            <h2 className="decision-title">{score?.decision ?? "Waiting..."}</h2>
            <div className="muted">
              {score ? `Threshold ${(score.decision_threshold * 100).toFixed(0)} / 100` : "Submit an applicant"}
            </div>
          </div>
          <div className={`pill ${score && score.score >= (score.decision_threshold ?? 0.5) ? "success" : "warn"}`}>
            {score ? `${(score.score * 100).toFixed(1)}` : "—"}
          </div>
        </div>
        <div className="progress" style={{ marginTop: 10 }}>
          <div className="progress-bar" style={{ width: `${((score?.score ?? 0) * 100).toFixed(0)}%` }} />
        </div>
        <div className="chip-row" style={{ marginTop: 12 }}>
          {(score?.reason_codes || []).map((reason) => (
            <span key={reason} className="chip">
              {reason}
            </span>
          ))}
          {!score && <span className="muted">Reason codes populate after a score response.</span>}
        </div>
      </div>

      <div className="glass card">
        <div className="label">
          <span>Fairness snapshot</span>
          <span className="muted">{fairness ? `${fairness.groups.length} groups` : "awaiting report"}</span>
        </div>
        <div className="grid metric-pair-grid" style={{ marginTop: 10 }}>
          <Metric name="Demographic parity Δ" value={fairness?.demographic_parity_difference} />
          <Metric name="Equal opportunity Δ" value={fairness?.equal_opportunity_difference} />
        </div>
        <div style={{ marginTop: 12 }}>
          <div className="label">
            <span>Selection rate by group</span>
            <span className="muted">{fairness ? `${Object.values(fairness.counts_by_group).reduce((a, b) => a + b, 0)} rows` : ""}</span>
          </div>
          {fairness ? (
            Object.entries(fairness.selection_rate_by_group).map(([groupName, value]) => (
              <div key={groupName} style={{ marginTop: 8 }}>
                <div className="label">
                  <span>{groupName}</span>
                  <span>
                    {formatPct(value)} · n={fairness.counts_by_group[groupName] ?? 0}
                  </span>
                </div>
                <div className="chart-bar">
                  <div className="chart-fill" style={{ width: `${Math.min(100, value * 100)}%` }} />
                </div>
              </div>
            ))
          ) : (
            <p className="muted" style={{ marginTop: 8 }}>
              Run a fairness report or portfolio analysis to populate this section.
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
        ? { label: "stable", tone: "success" }
        : { label: "review", tone: "warn" };

  return (
    <div className="metric-card">
      <div className="label">
        <span>{name}</span>
        <span className={`pill ${badge.tone}`}>{badge.label}</span>
      </div>
      <div className="metric-value">{formatPct(value)}</div>
    </div>
  );
}
