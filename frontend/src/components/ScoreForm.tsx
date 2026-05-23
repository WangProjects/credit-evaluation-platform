import React, { useEffect, useMemo, useState } from "react";
import { buildDefaultFeatures } from "../data/demo";
import { ApplicantFeatures, FeatureContract, ScorePayload, SensitiveAttributes } from "../types";

type Props = {
  contract: FeatureContract | null;
  loadingScore?: boolean;
  loadingExplain?: boolean;
  onScore: (payload: ScorePayload) => void;
  onExplain: (payload: ScorePayload) => void;
};

const ageBands = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+", "decline_to_state"];

export function ScoreForm({ contract, loadingScore, loadingExplain, onScore, onExplain }: Props) {
  const [applicationId, setApplicationId] = useState("demo_applicant");
  const [features, setFeatures] = useState<ApplicantFeatures>({});
  const [sensitiveAttributes, setSensitiveAttributes] = useState<SensitiveAttributes>({
    age_band: "25-34",
    race_ethnicity: "decline_to_state",
    sex: "decline_to_state",
  });

  useEffect(() => {
    if (!contract) {
      return;
    }
    setFeatures((previous) => mergeFeatureDefaults(previous, contract));
  }, [contract]);

  const groupedDefinitions = useMemo(() => {
    if (!contract) {
      return [];
    }

    const groups = new Map<string, typeof contract.feature_definitions>();
    contract.feature_definitions.forEach((definition) => {
      const existing = groups.get(definition.group) ?? [];
      existing.push(definition);
      groups.set(definition.group, existing);
    });

    return Array.from(groups.entries());
  }, [contract]);

  function buildPayload(): ScorePayload {
    return {
      application_id: applicationId,
      features,
      sensitive_attributes: sanitizeSensitiveAttributes(sensitiveAttributes),
    };
  }

  function resetToDefaults() {
    if (!contract) {
      return;
    }
    setApplicationId("demo_applicant");
    setFeatures(buildDefaultFeatures(contract));
    setSensitiveAttributes({
      age_band: "25-34",
      race_ethnicity: "decline_to_state",
      sex: "decline_to_state",
    });
  }

  if (!contract) {
    return (
      <section id="score-workbench" className="glass card score-form-shell">
        <div className="section-title">
          <span className="badge">Loading contract</span>
          <span className="muted">Fetching live model feature definitions...</span>
        </div>
      </section>
    );
  }

  return (
    <section id="score-workbench" className="glass card score-form-shell">
      <div className="score-form-header">
        <div>
          <div className="section-title">
            <span className="badge">Score applicant</span>
            <span className="muted">Contract-driven fields from the active model</span>
          </div>
          <p className="muted score-form-copy">
            Every input below is generated from the backend feature contract, so the UI stays aligned with the current
            model schema and threshold.
          </p>
        </div>
        <div className="button-row">
          <button className="btn ghost-btn" type="button" onClick={resetToDefaults}>
            Reset defaults
          </button>
          <button className="btn ghost-btn" type="button" onClick={() => onExplain(buildPayload())} disabled={loadingExplain}>
            {loadingExplain ? "Explaining..." : "Explain only"}
          </button>
          <button className="btn" type="button" onClick={() => onScore(buildPayload())} disabled={loadingScore}>
            {loadingScore ? "Scoring..." : "Score applicant"}
          </button>
        </div>
      </div>

      <div className="meta-strip">
        <span className="chip">Model: {contract.model_name}</span>
        <span className="chip">Version: {contract.model_version}</span>
        <span className="chip">Threshold: {(contract.decision_threshold * 100).toFixed(0)} / 100</span>
        <span className="chip">Schema: {contract.feature_schema_hash}</span>
      </div>

      <div className="glass card inline-card">
        <div className="label" style={{ marginBottom: 8 }}>
          <span>Application identifier</span>
          <span className="muted">Hashed in audit payloads</span>
        </div>
        <input className="input" value={applicationId} onChange={(event) => setApplicationId(event.target.value)} />
      </div>

      <div className="grid feature-group-grid">
        {groupedDefinitions.map(([groupName, definitions]) => (
          <div key={groupName} className="glass card feature-group-card">
            <div className="label">
              <span>{humanizeGroup(groupName)}</span>
              <span className="muted">{definitions.length} signals</span>
            </div>

            <div className="feature-card-stack">
              {definitions.map((definition) => {
                const value = features[definition.name] ?? definition.default_value ?? 0;
                const step = definition.step ?? 1;
                const minimum = definition.minimum ?? 0;
                const maximum = definition.maximum ?? Math.max(value + step * 10, value || 1);
                return (
                  <div key={definition.name} className="feature-card">
                    <div className="label">
                      <span>{definition.label}</span>
                      <span className="muted">{formatFeatureValue(value, step)}</span>
                    </div>
                    <p className="muted feature-description">{definition.description}</p>

                    <div className="feature-input-row">
                      <input
                        className="range-input"
                        type="range"
                        min={minimum}
                        max={maximum}
                        step={step}
                        value={value}
                        onChange={(event) =>
                          setFeatures((previous) => ({
                            ...previous,
                            [definition.name]: Number(event.target.value),
                          }))
                        }
                      />
                      <input
                        className="input feature-number-input"
                        type="number"
                        min={minimum}
                        max={maximum}
                        step={step}
                        value={value}
                        onChange={(event) =>
                          setFeatures((previous) => ({
                            ...previous,
                            [definition.name]: Number(event.target.value),
                          }))
                        }
                      />
                    </div>

                    <div className="label">
                      <span className="muted">{definition.required ? "Required" : "Optional"}</span>
                      <span className={`pill ${definition.higher_is_better ? "success" : "warn"}`}>
                        {definition.higher_is_better ? "higher helps" : "lower helps"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="grid sensitive-grid">
        <div className="glass card inline-card">
          <div className="label" style={{ marginBottom: 8 }}>
            <span>Age band</span>
            <span className="muted">Optional monitoring context</span>
          </div>
          <select
            className="input"
            value={sensitiveAttributes.age_band ?? ""}
            onChange={(event) => setSensitiveAttributes((previous) => ({ ...previous, age_band: event.target.value }))}
          >
            {ageBands.map((ageBand) => (
              <option key={ageBand} value={ageBand}>
                {ageBand}
              </option>
            ))}
          </select>
        </div>

        <div className="glass card inline-card">
          <div className="label" style={{ marginBottom: 8 }}>
            <span>Race / ethnicity</span>
            <span className="muted">Aggregated only</span>
          </div>
          <input
            className="input"
            value={sensitiveAttributes.race_ethnicity ?? ""}
            onChange={(event) =>
              setSensitiveAttributes((previous) => ({ ...previous, race_ethnicity: event.target.value }))
            }
          />
        </div>

        <div className="glass card inline-card">
          <div className="label" style={{ marginBottom: 8 }}>
            <span>Sex</span>
            <span className="muted">Aggregated only</span>
          </div>
          <input
            className="input"
            value={sensitiveAttributes.sex ?? ""}
            onChange={(event) => setSensitiveAttributes((previous) => ({ ...previous, sex: event.target.value }))}
          />
        </div>
      </div>
    </section>
  );
}

function mergeFeatureDefaults(previous: ApplicantFeatures, contract: FeatureContract) {
  const defaults = buildDefaultFeatures(contract);
  const next: ApplicantFeatures = {};
  contract.feature_definitions.forEach((definition) => {
    next[definition.name] = previous[definition.name] ?? defaults[definition.name];
  });
  return next;
}

function sanitizeSensitiveAttributes(attributes: SensitiveAttributes) {
  return Object.fromEntries(
    Object.entries(attributes).filter(([, value]) => value !== undefined && value !== null && value !== ""),
  );
}

function humanizeGroup(groupName: string) {
  return groupName.replace(/_/g, " ");
}

function formatFeatureValue(value: number, step: number) {
  return step >= 1 ? value.toFixed(0) : value.toFixed(2);
}
