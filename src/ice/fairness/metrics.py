from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple


def selection_rate(decisions: Iterable[bool]) -> float:
    ds = list(decisions)
    if not ds:
        return 0.0
    return sum(1 for d in ds if d) / len(ds)


def disparate_impact_ratio(group_a: Iterable[bool], group_b: Iterable[bool]) -> float:
    """
    Returns selection_rate(A) / selection_rate(B). If denominator is 0, returns 0.
    """
    ra = selection_rate(group_a)
    rb = selection_rate(group_b)
    return (ra / rb) if rb > 0 else 0.0


def confusion_counts(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def rates_from_counts(c: Dict[str, int]) -> Dict[str, float]:
    tp, tn, fp, fn = c["tp"], c["tn"], c["fp"], c["fn"]
    tpr = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return {"tpr": tpr, "fpr": fpr}


def group_rates(
    y_true: List[int], y_pred: List[int], group: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Compute TPR/FPR by group label.
    """
    buckets: Dict[str, Tuple[List[int], List[int]]] = {}
    for t, p, g in zip(y_true, y_pred, group):
        yt, yp = buckets.get(g, ([], []))
        yt.append(int(t))
        yp.append(int(p))
        buckets[g] = (yt, yp)

    out: Dict[str, Dict[str, float]] = {}
    for g, (yt, yp) in buckets.items():
        out[g] = rates_from_counts(confusion_counts(yt, yp))
    return out


def selection_rates_by_group(
    groups: List[str], y_pred: List[int], positive_label: int = 1
) -> Dict[str, float]:
    counts: Dict[str, int] = defaultdict(int)
    positives: Dict[str, int] = defaultdict(int)
    for group_name, prediction in zip(groups, y_pred, strict=True):
        counts[group_name] += 1
        if prediction == positive_label:
            positives[group_name] += 1
    return {
        group_name: (positives[group_name] / counts[group_name]) if counts[group_name] else 0.0
        for group_name in sorted(counts.keys())
    }


def tpr_by_group(
    groups: List[str], y_true: List[int], y_pred: List[int], positive_label: int = 1
) -> Dict[str, float]:
    true_positives: Dict[str, int] = defaultdict(int)
    positives: Dict[str, int] = defaultdict(int)
    for group_name, truth, prediction in zip(groups, y_true, y_pred, strict=True):
        if truth == positive_label:
            positives[group_name] += 1
            if prediction == positive_label:
                true_positives[group_name] += 1
    return {
        group_name: (true_positives[group_name] / positives[group_name]) if positives[group_name] else 0.0
        for group_name in sorted(positives.keys())
    }


def demographic_parity_difference(selection_rate_by_group: Dict[str, float]) -> float:
    if not selection_rate_by_group:
        return 0.0
    values = list(selection_rate_by_group.values())
    return float(max(values) - min(values))


def equal_opportunity_difference(tpr_by_group_map: Dict[str, float]) -> float:
    if not tpr_by_group_map:
        return 0.0
    values = list(tpr_by_group_map.values())
    return float(max(values) - min(values))

