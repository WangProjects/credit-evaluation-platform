## Governance (technical)

This document describes how to operate this repo as a responsible AI system.
It focuses on engineering artifacts and processes that support audits and oversight.

### Model lifecycle

- **Data sourcing**: record provenance, consent basis, retention policy.
- **Training**: produce immutable artifacts (model + feature contract + reports).
- **Evaluation**: record performance + calibration + subgroup metrics where lawful.
- **Approval**: require human review before promotion to “current”.
- **Deployment**: serve only approved versions.
- **Monitoring**: track drift, performance, fairness metrics, and incident response.

### Required artifacts

Each released model version should ship with:

- `model.joblib` (or equivalent)
- `model_card.json` (metadata, limitations, intended use)
- `eval_report.json` (metrics)
- `fairness_report.json` (if measuring protected class outcomes)
- `feature_contract.json` (expected inputs; schema hash)

This repo stores a minimal version of these in:

- `artifacts/registry/model_registry.json`
- `artifacts/reports/`

### Human-in-the-loop (HITL)

Serving should be configurable to:

- return **recommendation** vs fully automated decision
- require manual review for borderline scores
- support appeals/reconsideration workflows (out of scope here; interface stubs only)

### Incident response

Examples:

- materially increased denial rate for a subgroup
- degraded calibration after distribution shift
- data leakage or PII exposure

Actions:

- freeze model promotion
- roll back to prior version
- publish incident report and mitigation steps


