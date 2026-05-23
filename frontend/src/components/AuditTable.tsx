import React from "react";
import { AuditEvent, AuditFilters } from "../types";

type Props = {
  events: AuditEvent[];
  filters: AuditFilters;
  loading?: boolean;
  total?: number;
  onFiltersChange: (next: AuditFilters) => void;
};

const formatDate = (ts: number) => new Date(ts * 1000).toLocaleString();

const eventOptions = ["decision", "explain", "fairness_report", "portfolio_analysis", "outcome"];

export function AuditTable({ events, filters, loading, total, onFiltersChange }: Props) {
  return (
    <section className="glass card">
      <div className="section-title">
        <span className="badge">Audit explorer</span>
        <span className="muted">{loading ? "Refreshing..." : `${total ?? events.length} events indexed`}</span>
      </div>

      <div className="audit-filter-bar">
        <select
          className="input"
          value={filters.event_type ?? ""}
          onChange={(event) => onFiltersChange({ ...filters, event_type: event.target.value || undefined })}
        >
          <option value="">All event types</option>
          {eventOptions.map((eventType) => (
            <option key={eventType} value={eventType}>
              {eventType}
            </option>
          ))}
        </select>
        <input
          className="input"
          placeholder="Filter by application id"
          value={filters.application_id ?? ""}
          onChange={(event) => onFiltersChange({ ...filters, application_id: event.target.value || undefined })}
        />
      </div>

      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>When</th>
              <th>Type</th>
              <th>Request</th>
              <th>Application</th>
              <th>Model</th>
              <th>Payload</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>{formatDate(event.ts)}</td>
                <td>
                  <span className="chip">{event.event_type}</span>
                </td>
                <td className="muted">{event.request_id ?? "—"}</td>
                <td className="muted">{event.application_id ?? "—"}</td>
                <td className="muted">{event.model_version ?? "—"}</td>
                <td>
                  <code className="payload-code">{JSON.stringify(event.payload, null, 2)}</code>
                </td>
              </tr>
            ))}

            {!events.length && (
              <tr>
                <td colSpan={6} className="muted">
                  No audit events matched the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
