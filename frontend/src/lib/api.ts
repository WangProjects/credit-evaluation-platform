import { demoAuditEvents, demoFairness, demoScoreResult } from "../data/demo";
import {
  AuditEventList,
  FairnessReport,
  FairnessRow,
  ScorePayload,
  ScoreResult,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const USE_API =
  typeof import.meta.env.VITE_API_BASE_URL !== "undefined" &&
  import.meta.env.VITE_API_BASE_URL !== "" &&
  import.meta.env.VITE_API_BASE_URL !== "mock";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function scoreApplicant(payload: ScorePayload): Promise<ScoreResult> {
  if (!USE_API) {
    return Promise.resolve({
      ...demoScoreResult,
      request_id: `req_mock_${Date.now()}`,
      score: Math.max(0, Math.min(1, 0.55 + Math.random() * 0.25)),
      decision: Math.random() > 0.35 ? "APPROVE" : "REVIEW",
    });
  }
  return postJson<ScoreResult>("/v1/score", payload);
}

export async function fetchFairnessReport(rows: FairnessRow[]): Promise<FairnessReport> {
  if (!USE_API) {
    return Promise.resolve(demoFairness);
  }
  return postJson<FairnessReport>("/v1/audit/fairness", { rows, positive_label: 1 });
}

export async function fetchAuditEvents(limit = 20): Promise<AuditEventList> {
  if (!USE_API) {
    return Promise.resolve({
      total: demoAuditEvents.length,
      limit,
      offset: 0,
      events: demoAuditEvents.slice(0, limit),
    });
  }
  return getJson<AuditEventList>(`/v1/audit/events?limit=${limit}`);
}
