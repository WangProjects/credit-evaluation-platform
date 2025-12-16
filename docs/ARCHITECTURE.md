## Architecture

This repository implements a reference architecture for an **inclusive, responsible credit
evaluation platform** with:

- **Offline training pipeline** (Project 1)
- **Online real-time scoring API** (Project 2)
- **Governance + monitoring hooks** (Project 2)

### Core components

#### 1) Feature contract and transformations

- **Input**: alternative financial data that is lawful to use and consented (rent/utilities/cash flow).
- **Output**: normalized, interpretable features used by models.

Implementation:

- `src/ice/types.py` (core request/feature types)
- `src/ice/features/contract.py` (feature schema and validation)

#### 2) Model interface + registry

Models are treated as versioned artifacts with attached metadata:

- training data snapshot id
- feature schema hash
- evaluation metrics
- fairness metrics (when available)

Implementation:

- `src/ice/models/base.py`
- `src/ice/models/sklearn_logreg.py`
- `src/ice/models/registry.py`

#### 3) Explainability layer (reason codes)

The platform returns **reason codes** suitable for adverse-action style explanation patterns
(without asserting any legal sufficiency).

Implementation:

- `src/ice/explain/reason_codes.py`
- optional SHAP/LIME integration points in `src/ice/explain/`

#### 4) Audit/event layer

Every decision is logged with:

- request id + timestamp
- model version
- features used (or hash)
- score + decision + reason codes

Implementation:

- `src/ice/audit/events.py`
- `src/ice/audit/store.py`

#### 5) API service

FastAPI provides:

- scoring
- explanation
- model metadata
- event ingestion for monitoring

Implementation:

- `services/api/app.py` and `services/api/api.py`

### Suggested deployment topology

- **Training**: batch job (cron, Airflow, or CI-triggered) writes artifacts to object storage.
- **Serving**: stateless API loads model artifacts + registry metadata at startup.
- **Monitoring**: periodic job computes drift/fairness from ingested outcomes.


