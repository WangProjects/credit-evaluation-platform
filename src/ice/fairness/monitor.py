from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ice.fairness.metrics import disparate_impact_ratio, group_rates, selection_rate


@dataclass(frozen=True)
class FairnessReport:
    attribute: str
    groups: List[str]
    selection_rates: Dict[str, float]
    disparate_impact_pairs: Dict[str, float]
    error_rates: Optional[Dict[str, Dict[str, float]]]


def compute_fairness_report(
    decisions: List[bool],
    sensitive_values: List[str],
    attribute: str,
    outcomes: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Compute basic fairness metrics for one sensitive attribute.

    - decisions: approved=True/False
    - sensitive_values: group label per decision
    - outcomes: optional true labels (e.g., repayment success) to compute TPR/FPR
    """
    if len(decisions) != len(sensitive_values):
        raise ValueError("decisions and sensitive_values must have same length")

    groups = sorted(set(sensitive_values))
    sel: Dict[str, float] = {}
    for g in groups:
        ds = [d for d, s in zip(decisions, sensitive_values) if s == g]
        sel[g] = selection_rate(ds)

    # Pairwise DI relative to the max-selection group (a common reporting pattern)
    ref = max(sel.items(), key=lambda kv: kv[1])[0] if groups else None
    di: Dict[str, float] = {}
    if ref is not None:
        ref_ds = [d for d, s in zip(decisions, sensitive_values) if s == ref]
        for g in groups:
            g_ds = [d for d, s in zip(decisions, sensitive_values) if s == g]
            di[f"{g}_vs_{ref}"] = disparate_impact_ratio(g_ds, ref_ds)

    err_rates = None
    if outcomes is not None:
        if len(outcomes) != len(decisions):
            raise ValueError("outcomes length must match decisions length")
        y_pred = [1 if d else 0 for d in decisions]
        err_rates = group_rates(outcomes, y_pred, sensitive_values)

    report = FairnessReport(
        attribute=attribute,
        groups=groups,
        selection_rates=sel,
        disparate_impact_pairs=di,
        error_rates=err_rates,
    )
    return {
        "attribute": report.attribute,
        "groups": report.groups,
        "selection_rates": report.selection_rates,
        "disparate_impact_pairs": report.disparate_impact_pairs,
        "error_rates": report.error_rates,
    }


