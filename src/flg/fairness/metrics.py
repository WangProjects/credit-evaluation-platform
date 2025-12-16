from __future__ import annotations

from collections import defaultdict

import numpy as np
from fairlearn.metrics import MetricFrame, selection_rate, true_positive_rate


def group_fairness_report(*, y_true: np.ndarray, y_score: np.ndarray, group: np.ndarray) -> dict:
    """Compute a small fairness report for demo purposes.

    Production deployments typically require a richer set of metrics and
    alignment with the institution's ECOA/fair-lending program.
    """

    y_pred = (y_score >= 0.5).astype(int)

    mf = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "tpr": true_positive_rate,
        },
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=group,
    )

    per_group = {k: {g: float(v) for g, v in series.items()} for k, series in mf.by_group.items()}

    # Simple gaps
    gaps = defaultdict(float)
    for metric_name, series in mf.by_group.items():
        vals = list(series.values)
        if len(vals) >= 2:
            gaps[f"{metric_name}_gap_max_minus_min"] = float(max(vals) - min(vals))

    return {
        "overall": {k: float(v) for k, v in mf.overall.items()},
        "by_group": per_group,
        "gaps": dict(gaps),
    }
