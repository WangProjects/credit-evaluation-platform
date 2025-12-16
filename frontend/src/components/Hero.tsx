import React from "react";

export function Hero() {
  return (
    <section className="glass card" style={{ padding: 24, marginTop: 16 }}>
      <div className="section-title">
        <span className="badge">Open-source</span>
        <span className="badge">Alt-data</span>
        <span className="badge">Explainable</span>
      </div>
      <h1 style={{ margin: "6px 0 12px", fontSize: 28 }}>
        Inclusive credit decisions with transparency, fairness, and privacy baked in.
      </h1>
      <p className="muted" style={{ maxWidth: 820 }}>
        Run demo scores on alternative-data features, review reason codes, and inspect fairness metrics—all without
        storing raw personal identifiers. The UI uses hashed IDs and an allowlisted audit payload by default.
      </p>
      <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap" }}>
        <div className="chip">PII-light audit logging</div>
        <div className="chip">Adverse-action ready reason codes</div>
        <div className="chip">Fairness monitors</div>
        <div className="chip">API + CLI parity</div>
      </div>
    </section>
  );
}
