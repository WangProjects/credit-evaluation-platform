## Compliance mapping (engineering controls)

This is a **technical mapping** of common controls used in regulated lending contexts.
It is **not legal advice** and does not claim that any configuration satisfies any law.

### FCRA / ECOA (conceptual)

- **Data provenance & consent**
  - store source + consent basis for each data feed (out of scope for this demo; interfaces provided)
  - keep data minimization defaults in `ice.config.Settings`

- **Notice / explanation**
  - return **reason codes** for decisions (`ice.explain.reason_codes`)
  - persist decision logs for audit (`ice.audit.store`)

- **Auditability**
  - versioned models + feature schema hash (`ice.models.registry`)
  - immutable-ish event logs (append-only JSONL; optional SQLite)

- **Adverse-action style patterns**
  - provide ranked reason codes and supporting values
  - keep decision thresholds configurable and documented

### NIST AI RMF 1.0 (high-level)

- **Govern**
  - documented model lifecycle (`docs/GOVERNANCE.md`)
  - threat model and security controls (`docs/THREAT_MODEL.md`)

- **Map**
  - intended use + limitations in registry metadata

- **Measure**
  - performance, calibration, drift and subgroup metrics (stubs in `ice.fairness`)

- **Manage**
  - rollback, promotion gates, incident response process

### Blueprint for an AI Bill of Rights (technical alignment)

- **Notice and explanation**
  - reason codes + explanation endpoint

- **Algorithmic discrimination protections**
  - fairness metrics hooks + monitoring stubs

- **Data privacy**
  - strict separation between features and sensitive attributes; default exclude from model


