import React from "react";
import { useForm } from "react-hook-form";
import { ApplicantFeatures, ScorePayload } from "../types";

type FormValues = ScorePayload;

type Props = {
  onSubmit: (payload: ScorePayload) => void;
  loading?: boolean;
};

const defaultFeatures: ApplicantFeatures = {
  rent_on_time_ratio_12m: 0.94,
  utilities_on_time_ratio_12m: 0.9,
  cashflow_volatility_90d: 0.35,
  income_stability_6m: 0.82,
  avg_monthly_net_inflow_6m: 4200,
  avg_daily_balance_90d: 1800,
  overdraft_count_12m: 0,
  months_at_address: 24,
};

const ageBands = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"];

export function ScoreForm({ onSubmit, loading }: Props) {
  const { register, handleSubmit, watch, setValue } = useForm<FormValues>({
    defaultValues: {
      applicant_id: "demo_applicant",
      features: defaultFeatures,
      audit_context: { age_band: "25-34", race_ethnicity: "decline_to_state", sex: "decline_to_state" },
    },
  });

  const features = watch("features");

  return (
    <form
      className="glass card"
      style={{ padding: 20, display: "grid", gap: 12 }}
      onSubmit={handleSubmit((values) => onSubmit(values))}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div className="section-title">
          <span className="badge">Score applicant</span>
          <span className="muted" style={{ fontSize: 13 }}>
            Alternative-data only; no PII stored.
          </span>
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Scoring..." : "Score now"}
        </button>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        {[
          {
            label: "Rent on-time ratio (12m)",
            key: "rent_on_time_ratio_12m",
            step: 0.01,
            min: 0,
            max: 1,
          },
          {
            label: "Utilities on-time ratio (12m)",
            key: "utilities_on_time_ratio_12m",
            step: 0.01,
            min: 0,
            max: 1,
          },
          {
            label: "Cashflow volatility (90d)",
            key: "cashflow_volatility_90d",
            step: 0.01,
            min: 0,
            max: 5,
          },
          { label: "Income stability (6m)", key: "income_stability_6m", step: 0.01, min: 0, max: 1 },
          {
            label: "Avg monthly net inflow (6m)",
            key: "avg_monthly_net_inflow_6m",
            step: 50,
            min: -10000,
            max: 100000,
          },
          {
            label: "Avg daily balance (90d)",
            key: "avg_daily_balance_90d",
            step: 25,
            min: -5000,
            max: 100000,
          },
          { label: "Overdraft count (12m)", key: "overdraft_count_12m", step: 1, min: 0, max: 50 },
          { label: "Months at address", key: "months_at_address", step: 1, min: 0, max: 240 },
        ].map((f) => (
          <div key={f.key} className="card glass" style={{ padding: 12 }}>
            <div className="label">
              <span>{f.label}</span>
              <span className="muted">{features[f.key as keyof ApplicantFeatures]}</span>
            </div>
            <input
              type="range"
              min={f.min}
              max={f.max}
              step={f.step}
              className="input"
              {...register(`features.${f.key}` as const, { valueAsNumber: true })}
              onChange={(e) => setValue(`features.${f.key}` as const, Number(e.target.value))}
            />
          </div>
        ))}
      </div>

      <div className="glass card" style={{ padding: 12 }}>
        <div className="label" style={{ marginBottom: 8 }}>
          <span>Applicant identifier (hashed in audit logs)</span>
        </div>
        <input className="input" placeholder="applicant token" {...register("applicant_id")} />
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        <div className="glass card" style={{ padding: 12 }}>
          <div className="label">Age band (optional audit context)</div>
          <select className="input" {...register("audit_context.age_band")}>
            {ageBands.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
            <option value="decline_to_state">Prefer not to say</option>
          </select>
        </div>
        <div className="glass card" style={{ padding: 12 }}>
          <div className="label">Race/ethnicity (optional)</div>
          <input
            className="input"
            placeholder="aggregated categories"
            {...register("audit_context.race_ethnicity")}
          />
        </div>
        <div className="glass card" style={{ padding: 12 }}>
          <div className="label">Sex (optional)</div>
          <input className="input" placeholder="aggregated categories" {...register("audit_context.sex")} />
        </div>
      </div>
    </form>
  );
}
