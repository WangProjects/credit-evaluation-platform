## Threat model (overview)

This document captures common threats for credit scoring APIs and suggested mitigations.

### Assets

- applicant features (potentially sensitive)
- model artifact + thresholds
- decision logs (audit trail)
- registry metadata (model cards, reports)

### Threats and mitigations (examples)

- **Unauthorized access**
  - API key / OAuth2 integration in serving layer (demo uses API key header)
  - network controls, TLS, WAF (deployment-dependent)

- **Data exfiltration**
  - minimize logged raw features; prefer hashes in logs (configurable)
  - encrypt storage at rest (deployment-dependent)

- **Prompt/feature injection (schema abuse)**
  - strict request schema validation (`pydantic`)
  - reject unknown fields

- **Model inversion / membership inference**
  - avoid returning excessively granular explanations by default
  - rate limiting and monitoring (deployment-dependent)

- **Tampering with audit logs**
  - append-only storage conventions
  - periodic sealing (hash chains) — TODO for production


