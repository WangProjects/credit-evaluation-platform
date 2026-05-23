import React, { useMemo, useState } from "react";
import { fetchFairnessReport } from "../lib/api";
import { FairnessReport, FairnessRow } from "../types";

type Props = {
  onFairness: (report: FairnessReport) => void;
};

const groups = ["18-24", "25-34", "35-44"];

export function FairnessPanel({ onFairness }: Props) {
  const [rows, setRows] = useState<FairnessRow[]>(() => makeSyntheticRows());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sampleStats = useMemo(() => summarize(rows), [rows]);

  async function runReport() {
    try {
      setLoading(true);
      setError(null);
      const report = await fetchFairnessReport(rows);
      onFairness(report);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to compute fairness");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="glass card">
      <div className="section-title">
        <span className="badge">Fairness monitor</span>
        <span className="muted">Synthetic approval/outcome batch mapped to monitoring groups</span>
      </div>

      <div className="grid fairness-card-grid">
        {groups.map((groupName) => (
          <div key={groupName} className="glass card compact-card">
            <div className="label">
              <span>{groupName}</span>
              <span className="muted">n={sampleStats[groupName]?.n ?? 0}</span>
            </div>
            <div style={{ marginTop: 8 }}>
              <div className="label">
                <span>Selection rate</span>
                <span>{((sampleStats[groupName]?.approve_rate ?? 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="chart-bar">
                <div
                  className="chart-fill"
                  style={{ width: `${Math.min(100, (sampleStats[groupName]?.approve_rate ?? 0) * 100)}%` }}
                />
              </div>
            </div>
            <div className="muted" style={{ marginTop: 8 }}>
              Positive outcome rate: {((sampleStats[groupName]?.outcome_rate ?? 0) * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>

      <div className="panel-footer">
        <p className="muted">
          Use this to simulate parity checks before plugging in aggregated outcomes from a deployment environment.
        </p>
        <div className="button-row">
          <button className="btn ghost-btn" type="button" onClick={() => setRows(makeSyntheticRows())} disabled={loading}>
            Regenerate batch
          </button>
          <button className="btn" type="button" onClick={runReport} disabled={loading}>
            {loading ? "Computing..." : "Run fairness report"}
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
    </section>
  );
}

function makeSyntheticRows(n = 120): FairnessRow[] {
  const rows: FairnessRow[] = [];
  for (let index = 0; index < n; index += 1) {
    const groupName = groups[index % groups.length];
    const wave = (index % 12) / 12;
    const selectionBias = groupName === "25-34" ? 0.68 : groupName === "35-44" ? 0.61 : 0.55;
    const outcomeBias = groupName === "25-34" ? 0.74 : groupName === "35-44" ? 0.69 : 0.63;
    const y_pred = wave < selectionBias ? 1 : 0;
    const y_true = wave < outcomeBias ? 1 : 0;
    rows.push({ protected_group: groupName, y_true, y_pred });
  }
  return rows;
}

function summarize(rows: FairnessRow[]) {
  const out: Record<string, { n: number; approve_rate: number; outcome_rate: number }> = {};
  rows.forEach((row) => {
    const current = out[row.protected_group] || { n: 0, approve_rate: 0, outcome_rate: 0 };
    current.n += 1;
    current.approve_rate += row.y_pred;
    current.outcome_rate += row.y_true;
    out[row.protected_group] = current;
  });
  Object.keys(out).forEach((groupName) => {
    out[groupName].approve_rate /= out[groupName].n;
    out[groupName].outcome_rate /= out[groupName].n;
  });
  return out;
}
