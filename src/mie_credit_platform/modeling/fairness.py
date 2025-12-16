from __future__ import annotations

from collections import defaultdict


def _safe_rate(numer: float, denom: float) -> float:
    return float(numer / denom) if denom else 0.0


def selection_rates_by_group(groups: list[str], y_pred: list[int], positive_label: int = 1) -> dict[str, float]:
    counts = defaultdict(int)
    pos = defaultdict(int)
    for g, yp in zip(groups, y_pred, strict=True):
        counts[g] += 1
        if yp == positive_label:
            pos[g] += 1
    return {g: _safe_rate(pos[g], counts[g]) for g in sorted(counts.keys())}


def tpr_by_group(groups: list[str], y_true: list[int], y_pred: list[int], positive_label: int = 1) -> dict[str, float]:
    tp = defaultdict(int)
    p = defaultdict(int)
    for g, yt, yp in zip(groups, y_true, y_pred, strict=True):
        if yt == positive_label:
            p[g] += 1
            if yp == positive_label:
                tp[g] += 1
    return {g: _safe_rate(tp[g], p[g]) for g in sorted(p.keys())}


def demographic_parity_difference(selection_rate: dict[str, float]) -> float:
    if not selection_rate:
        return 0.0
    vals = list(selection_rate.values())
    return float(max(vals) - min(vals))


def equal_opportunity_difference(tpr: dict[str, float]) -> float:
    if not tpr:
        return 0.0
    vals = list(tpr.values())
    return float(max(vals) - min(vals))


