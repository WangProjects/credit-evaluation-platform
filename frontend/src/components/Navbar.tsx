import React from "react";

type Props = {
  mode: "live" | "mock";
  onPrimaryAction?: () => void;
};

export function Navbar({ mode, onPrimaryAction }: Props) {
  return (
    <header className="glass nav-shell">
      <div className="nav-brand">
        <div className="nav-mark">Q</div>
        <div>
          <div className="nav-title">Inclusive Credit Command Center</div>
          <div className="muted nav-subtitle">Responsible decisioning, auditability, and cohort monitoring</div>
        </div>
      </div>

      <div className="nav-actions">
        <span className={`pill ${mode === "live" ? "success" : "warn"}`}>{mode === "live" ? "live" : "mock"}</span>
        <span className="badge">PII-light mode</span>
        <button className="btn" type="button" onClick={onPrimaryAction}>
          Jump to scoring
        </button>
      </div>
    </header>
  );
}
