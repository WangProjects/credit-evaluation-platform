import React from "react";
import { AuditEvent } from "../types";

type Props = {
  events: AuditEvent[];
  loading?: boolean;
};

const formatDate = (ts: number) => new Date(ts * 1000).toLocaleString();

export function AuditTable({ events, loading }: Props) {
  return (
    <section className="glass card" style={{ padding: 16, marginTop: 12 }}>
      <div className="section-title">
        <span className="badge">Audit events</span>
        <span className="muted">{loading ? "Refreshing..." : "Redacted identifiers, allowlisted payload"}</span>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>When</th>
              <th>Type</th>
              <th>Request</th>
              <th>Applicant</th>
              <th>Model</th>
              <th>Payload</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id}>
                <td>{formatDate(e.ts)}</td>
                <td>{e.event_type}</td>
                <td className="muted">{e.request_id}</td>
                <td className="muted">{e.applicant_id ?? "—"}</td>
                <td className="muted">{e.model_version ?? "—"}</td>
                <td>
                  <code style={{ fontSize: 12 }}>
                    {JSON.stringify(e.payload, null, 0).replace(/"/g, "") || "{}"}
                  </code>
                </td>
              </tr>
            ))}
            {!events.length && (
              <tr>
                <td colSpan={6} className="muted">
                  No audit events yet. Score an applicant to generate one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
