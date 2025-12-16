import { AuditEvent, FairnessReport, ScoreResult } from "../types";

export const demoScoreResult: ScoreResult = {
  request_id: "req_demo_001",
  model_version: "v0.1.0",
  score: 0.72,
  decision: "APPROVE",
  reason_codes: ["HIGH_RISK_SIGNAL:cashflow_volatility_90d", "HIGH_RISK_SIGNAL:overdraft_count_12m"],
};

export const demoFairness: FairnessReport = {
  groups: ["group_a", "group_b", "group_c"],
  demographic_parity_difference: -0.05,
  equal_opportunity_difference: 0.08,
  selection_rate_by_group: {
    group_a: 0.61,
    group_b: 0.54,
    group_c: 0.66,
  },
  tpr_by_group: {
    group_a: 0.77,
    group_b: 0.68,
    group_c: 0.80,
  },
};

export const demoAuditEvents: AuditEvent[] = [
  {
    id: 1001,
    ts: Date.now() / 1000 - 3600,
    request_id: "req_demo_001",
    event_type: "score",
    model_version: "v0.1.0",
    applicant_id: "hashed_abcd",
    payload: {
      score: 0.72,
      decision: "APPROVE",
      reason_codes: ["HIGH_RISK_SIGNAL:cashflow_volatility_90d"],
    },
  },
  {
    id: 1000,
    ts: Date.now() / 1000 - 7200,
    request_id: "req_demo_000",
    event_type: "fairness_report",
    model_version: "v0.1.0",
    applicant_id: null,
    payload: {
      equal_opportunity_difference: 0.08,
      demographic_parity_difference: -0.05,
      positive_label: 1,
    },
  },
];
