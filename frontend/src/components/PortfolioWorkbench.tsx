import React, { useEffect, useMemo, useState } from "react";
import { buildDemoPortfolioApplications } from "../data/demo";
import { PortfolioAnalysisResult, PortfolioApplicationInput, FeatureContract } from "../types";

type Props = {
  contract: FeatureContract | null;
  loading?: boolean;
  result: PortfolioAnalysisResult | null;
  onRun: (applications: PortfolioApplicationInput[], groupKey: string) => void;
};

const cohortSizes = [12, 24, 40, 60];
const groupOptions = ["age_band", "race_ethnicity", "sex"];

export function PortfolioWorkbench({ contract, loading, result, onRun }: Props) {
  const [size, setSize] = useState(24);
  const [groupKey, setGroupKey] = useState("age_band");
  const [applications, setApplications] = useState<PortfolioApplicationInput[]>([]);

  useEffect(() => {
    if (!contract) {
      return;
    }
    setApplications(buildDemoPortfolioApplications(size, contract));
  }, [contract, size]);

  const approvalCount = useMemo(
    () => applications.filter((application) => application.actual_outcome === 1).length,
    [applications],
  );

  return (
    <section className="glass card">
      <div className="section-title">
        <span className="badge">Portfolio workbench</span>
        <span className="muted">Generate cohort snapshots against the active model</span>
      </div>

      <div className="portfolio-controls">
        <div className="glass card compact-card">
          <div className="label" style={{ marginBottom: 8 }}>
            <span>Cohort size</span>
            <span className="muted">{applications.length} applications</span>
          </div>
          <div className="button-row">
            {cohortSizes.map((cohortSize) => (
              <button
                key={cohortSize}
                className={`btn ${size === cohortSize ? "" : "ghost-btn"}`}
                type="button"
                onClick={() => setSize(cohortSize)}
              >
                {cohortSize}
              </button>
            ))}
          </div>
        </div>

        <div className="glass card compact-card">
          <div className="label" style={{ marginBottom: 8 }}>
            <span>Fairness grouping</span>
            <span className="muted">used only for monitoring</span>
          </div>
          <select className="input" value={groupKey} onChange={(event) => setGroupKey(event.target.value)}>
            {groupOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div className="glass card compact-card">
          <div className="label">
            <span>Label coverage</span>
            <span className="muted">{approvalCount} positive outcomes</span>
          </div>
          <p className="muted" style={{ marginTop: 8 }}>
            The sample cohort carries synthetic outcomes so the backend can compute equal opportunity deltas as part of
            the analysis.
          </p>
          <button className="btn" type="button" disabled={loading || !applications.length} onClick={() => onRun(applications, groupKey)}>
            {loading ? "Analyzing..." : "Run portfolio analysis"}
          </button>
        </div>
      </div>

      {result ? (
        <div className="grid portfolio-results-grid">
          <div className="glass card compact-card">
            <div className="label">
              <span>Portfolio summary</span>
              <span className="muted">{result.model_version}</span>
            </div>
            <div className="metric-pair-grid" style={{ marginTop: 12 }}>
              <SummaryStat label="Average score" value={`${(result.summary.average_score * 100).toFixed(1)}%`} />
              <SummaryStat label="Approval rate" value={`${(result.summary.approval_rate * 100).toFixed(1)}%`} />
              <SummaryStat label="Applications" value={String(result.summary.total_applications)} />
              <SummaryStat label="Threshold" value={`${(result.decision_threshold * 100).toFixed(0)}/100`} />
            </div>
          </div>

          <div className="glass card compact-card">
            <div className="label">
              <span>Top reason codes</span>
              <span className="muted">{result.top_reason_codes.length} returned</span>
            </div>
            <div className="stack-list">
              {result.top_reason_codes.map((reason) => (
                <div key={reason.code} className="stack-row">
                  <div>
                    <div>{reason.code}</div>
                    <div className="muted">{reason.description}</div>
                  </div>
                  <span className="pill warn">{reason.count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass card compact-card">
            <div className="label">
              <span>Decision mix</span>
              <span className="muted">by score band</span>
            </div>
            <div className="stack-list" style={{ marginTop: 12 }}>
              {Object.entries(result.summary.score_bands).map(([scoreBand, count]) => (
                <div key={scoreBand} className="stack-row">
                  <span>{scoreBand}</span>
                  <span className="pill muted">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass card compact-card">
            <div className="label">
              <span>Cohort preview</span>
              <span className="muted">top 6 rows</span>
            </div>
            <div className="stack-list" style={{ marginTop: 12 }}>
              {result.applications.slice(0, 6).map((application) => (
                <div key={application.application_id} className="stack-row">
                  <div>
                    <div>{application.application_id}</div>
                    <div className="muted">{application.reason_codes.join(", ") || "No reason codes"}</div>
                  </div>
                  <span className={`pill ${application.decision === "approve" ? "success" : "warn"}`}>
                    {(application.score * 100).toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <p className="muted" style={{ marginTop: 12 }}>
          Run the cohort through the API to get approval rates, score-band distribution, and optional fairness deltas
          tied to the selected grouping.
        </p>
      )}
    </section>
  );
}

function SummaryStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <div className="muted">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}
