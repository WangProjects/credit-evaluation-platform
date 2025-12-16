from __future__ import annotations

"""Retraining skeleton.

Project 2 calls for periodic model retraining, drift detection, and published fairness reports.
This file is intentionally a placeholder for your production retraining orchestration.

Suggested implementation:
- Pull new loan performance labels + refreshed alternative data
- Validate schema + data quality checks (Great Expectations)
- Train candidate models + evaluate performance + fairness
- Human review gate + signoff
- Publish model card + fairness report
- Promote model to registry + deploy
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrainingRun:
    run_id: str
    status: str


def run_retraining() -> RetrainingRun:
    # TODO: wire into Airflow/Argo/Prefect.
    return RetrainingRun(run_id="placeholder", status="not_implemented")
