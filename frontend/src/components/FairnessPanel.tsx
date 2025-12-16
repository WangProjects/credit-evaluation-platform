import React, { useMemo, useState } from "react";
import { fetchFairnessReport } from "../lib/api";
import { FairnessReport, FairnessRow } from "../types";

type Props = {
  onFairness: (report: FairnessReport) => void;
};

const groups = ["group_a", "group_b", "group_c"];

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
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to compute fairness");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="glass card" style={{ padding: 16, marginTop: 12 }}>
      <div className="section-title">
        <span className="badge">Fairness monitor</span>
        <span className="muted">Synthetic batch; replace with outcome events</span>
      </div>
      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
        {groups.map((g) => (
          <div key={g} className="glass card" style={{ padding: 12 }}>
            <div className="label">
              <span>{g}</span>
              <span className="muted">n={sampleStats[g]?.n ?? 0}</span>
            </div>
            <div style={{ marginTop: 4 }}>
              <div className="label">
                <span>Approve rate</span>
                <span>{((sampleStats[g]?.approve_rate ?? 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="chart-bar">
                <div
                  className="chart-fill"
                  style={{ width: `${Math.min(100, (sampleStats[g]?.approve_rate ?? 0) * 120)}%` }}
                />
              </div>
            </div>
            <div className="muted" style={{ fontSize: 13, marginTop: 4 }}>
              Outcome rate: {((sampleStats[g]?.outcome_rate ?? 0) * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
        <div className="muted" style={{ fontSize: 13 }}>
          Generated rows are anonymized, categorical groupings only. Replace with aggregated outcome events for your
          deployment.
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn" type="button" onClick={() => setRows(makeSyntheticRows())} disabled={loading}>
            Regenerate sample
          </button>
          <button className="btn" type="button" onClick={runReport} disabled={loading}>
            {loading ? "Computing..." : "Run fairness report"}
          </button>
        </div>
      </div>
      {error && (
        <div className="chip" style={{ marginTop: 8, borderColor: "#fca5a5", color: "#fecaca" }}>
          {error}
        </div>
      )}
    </section>
  );
}

function makeSyntheticRows(n = 120): FairnessRow[] {
  const rows: FairnessRow[] = [];
  const groupsLocal = groups;
  for (let i = 0; i < n; i += 1) {
    const g = groupsLocal[i % groupsLocal.length];
    const y_pred = Math.random() > 0.35 ? 1 : 0;
    const y_true = Math.random() > 0.4 ? 1 : 0;
    rows.push({ protected_group: g, y_true, y_pred });
  }
  return rows;
}

function summarize(rows: FairnessRow[]) {
  const out: Record<string, { n: number; approve_rate: number; outcome_rate: number }> = {};
  rows.forEach((r) => {
    const g = out[r.protected_group] || { n: 0, approve_rate: 0, outcome_rate: 0 };
    g.n += 1;
    g.approve_rate += r.y_pred;
    g.outcome_rate += r.y_true;
    out[r.protected_group] = g;
  });
  Object.keys(out).forEach((k) => {
    out[k].approve_rate = out[k].approve_rate / out[k].n;
    out[k].outcome_rate = out[k].outcome_rate / out[k].n;
  });
  return out;
}
