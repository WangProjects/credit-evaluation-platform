export type ApplicantFeatures = {
  rent_on_time_ratio_12m: number;
  utilities_on_time_ratio_12m: number;
  cashflow_volatility_90d: number;
  income_stability_6m: number;
  avg_monthly_net_inflow_6m: number;
  avg_daily_balance_90d: number;
  overdraft_count_12m: number;
  months_at_address: number;
};

export type ScorePayload = {
  applicant_id: string;
  features: ApplicantFeatures;
  audit_context?: {
    age_band?: string | null;
    race_ethnicity?: string | null;
    sex?: string | null;
  };
};

export type ScoreResult = {
  request_id: string;
  model_version: string;
  score: number;
  decision: "APPROVE" | "REVIEW" | string;
  reason_codes: string[];
};

export type ExplainContribution = {
  feature: string;
  value: number;
  weight: number;
  contribution: number;
};

export type ExplainResult = {
  request_id: string;
  model_version: string;
  score: number;
  base_value: number;
  contributions: ExplainContribution[];
};

export type FairnessRow = {
  protected_group: string;
  y_true: number;
  y_pred: number;
};

export type FairnessReport = {
  groups: string[];
  demographic_parity_difference: number;
  equal_opportunity_difference: number;
  selection_rate_by_group: Record<string, number>;
  tpr_by_group: Record<string, number>;
};

export type AuditEvent = {
  id: number;
  ts: number;
  request_id: string;
  event_type: string;
  model_version: string | null;
  applicant_id: string | null;
  payload: Record<string, unknown>;
};

export type AuditEventList = {
  total: number;
  limit: number;
  offset: number;
  events: AuditEvent[];
};
