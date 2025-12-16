import React from "react";

type Props = {
  onPrimaryAction?: () => void;
};

export function Navbar({ onPrimaryAction }: Props) {
  return (
    <header className="glass card" style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 12,
            background: "linear-gradient(135deg, #22d3ee, #6366f1)",
            display: "grid",
            placeItems: "center",
            fontWeight: 800,
            color: "#0b1021",
            boxShadow: "0 10px 30px rgba(99, 102, 241, 0.3)",
          }}
        >
          Q
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>Inclusive Credit UI</div>
          <div className="muted" style={{ fontSize: 13 }}>
            Open-source, privacy-first decisioning console
          </div>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span className="badge">PII-light mode</span>
        <button className="btn" onClick={onPrimaryAction}>
          New applicant
        </button>
      </div>
    </header>
  );
}
