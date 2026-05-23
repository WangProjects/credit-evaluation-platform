from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

from ice.explain.explainer import explain
from ice.explain.reason_codes import REASONS, generate_reason_codes
from ice.fairness.metrics import (
    demographic_parity_difference,
    equal_opportunity_difference,
    selection_rates_by_group,
    tpr_by_group,
)
from ice.features.transform import sanitize_features, to_model_vector
from ice.models.base import CreditModel


FEATURE_METADATA: dict[str, dict[str, Any]] = {
    "rent_on_time_rate_12m": {
        "label": "Rent on-time rate (12m)",
        "description": "Share of observed rent payments made on time during the last 12 months.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
        "default_value": 0.94,
        "higher_is_better": True,
        "group": "payment_history",
    },
    "utility_on_time_rate_12m": {
        "label": "Utility on-time rate (12m)",
        "description": "Share of observed utility payments made on time during the last 12 months.",
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
        "default_value": 0.91,
        "higher_is_better": True,
        "group": "payment_history",
    },
    "avg_monthly_income_6m": {
        "label": "Average monthly income (6m)",
        "description": "Average verified monthly income over the last six months.",
        "minimum": 0.0,
        "maximum": 15000.0,
        "step": 50.0,
        "default_value": 4200.0,
        "higher_is_better": True,
        "group": "cash_flow",
    },
    "cashflow_volatility_6m": {
        "label": "Cashflow volatility (6m)",
        "description": "Normalized volatility of recent cash flow, where higher values mean less stability.",
        "minimum": 0.0,
        "maximum": 1.5,
        "step": 0.01,
        "default_value": 0.24,
        "higher_is_better": False,
        "group": "cash_flow",
    },
    "avg_daily_balance_6m": {
        "label": "Average daily balance (6m)",
        "description": "Average account balance over the last six months.",
        "minimum": -1000.0,
        "maximum": 15000.0,
        "step": 25.0,
        "default_value": 1800.0,
        "higher_is_better": True,
        "group": "cash_flow",
    },
    "nsf_events_12m": {
        "label": "NSF events (12m)",
        "description": "Count of non-sufficient funds events observed over the last 12 months.",
        "minimum": 0.0,
        "maximum": 12.0,
        "step": 1.0,
        "default_value": 0.0,
        "higher_is_better": False,
        "group": "risk_events",
    },
    "overdraft_events_12m": {
        "label": "Overdraft events (12m)",
        "description": "Count of overdraft events observed over the last 12 months.",
        "minimum": 0.0,
        "maximum": 12.0,
        "step": 1.0,
        "default_value": 0.0,
        "higher_is_better": False,
        "group": "risk_events",
    },
    "months_at_current_job": {
        "label": "Months at current job",
        "description": "Tenure at the current job, when available.",
        "minimum": 0.0,
        "maximum": 240.0,
        "step": 1.0,
        "default_value": 18.0,
        "higher_is_better": True,
        "group": "stability",
    },
    "months_at_current_address": {
        "label": "Months at current address",
        "description": "Tenure at the current address, when available.",
        "minimum": 0.0,
        "maximum": 240.0,
        "step": 1.0,
        "default_value": 24.0,
        "higher_is_better": True,
        "group": "stability",
    },
}


@dataclass(frozen=True)
class ScoredApplication:
    application_id: str
    features: dict[str, float]
    score: float
    decision: str
    reason_codes: list[str]
    contributions: dict[str, float] | None


def score_application(
    model: CreditModel, application_id: str, features: dict[str, float], decision_threshold: float
) -> ScoredApplication:
    sanitized = sanitize_features(features)
    x = to_model_vector(model.contract, sanitized)
    score_value = model.predict_proba(x)
    decision = "approve" if score_value >= decision_threshold else "deny"
    reason_codes = generate_reason_codes(sanitized)
    explanation = explain(model, x)
    contributions = explanation.contributions if explanation is not None else None
    return ScoredApplication(
        application_id=application_id,
        features=sanitized,
        score=float(score_value),
        decision=decision,
        reason_codes=reason_codes,
        contributions=contributions,
    )


def describe_contract(model: CreditModel) -> list[dict[str, Any]]:
    required = set(model.contract.required)
    definitions: list[dict[str, Any]] = []
    for name in model.contract.columns():
        metadata = FEATURE_METADATA.get(name, {})
        definitions.append(
            {
                "name": name,
                "label": metadata.get("label", name.replace("_", " ").title()),
                "description": metadata.get("description", "Model feature."),
                "required": name in required,
                "minimum": metadata.get("minimum"),
                "maximum": metadata.get("maximum"),
                "step": metadata.get("step", 1.0),
                "default_value": metadata.get("default_value", 0.0),
                "higher_is_better": metadata.get("higher_is_better", True),
                "group": metadata.get("group", "other"),
            }
        )
    return definitions


def build_fairness_report(rows: Iterable[dict[str, Any]], positive_label: int = 1) -> dict[str, Any]:
    row_list = list(rows)
    groups = [str(row["protected_group"]) for row in row_list]
    y_true = [int(row["y_true"]) for row in row_list]
    y_pred = [int(row["y_pred"]) for row in row_list]
    selection_rate = selection_rates_by_group(groups, y_pred, positive_label=positive_label)
    tpr = tpr_by_group(groups, y_true, y_pred, positive_label=positive_label)
    counts = Counter(groups)
    return {
        "groups": sorted(counts.keys()),
        "counts_by_group": dict(sorted(counts.items())),
        "demographic_parity_difference": demographic_parity_difference(selection_rate),
        "equal_opportunity_difference": equal_opportunity_difference(tpr),
        "selection_rate_by_group": selection_rate,
        "tpr_by_group": tpr,
    }


def score_band(score_value: float) -> str:
    if score_value < 0.40:
        return "subprime_watch"
    if score_value < 0.65:
        return "near_prime"
    return "prime"


def analyze_portfolio(
    model: CreditModel,
    applications: Iterable[dict[str, Any]],
    decision_threshold: float,
    group_key: str | None = None,
    top_reason_count: int = 5,
) -> dict[str, Any]:
    results: list[ScoredApplication] = []
    fairness_rows: list[dict[str, Any]] = []
    reason_counter: Counter[str] = Counter()
    decision_counter: Counter[str] = Counter()
    score_band_counter: Counter[str] = Counter()

    for row in applications:
        result = score_application(
            model=model,
            application_id=str(row["application_id"]),
            features=dict(row["features"]),
            decision_threshold=decision_threshold,
        )
        results.append(result)
        decision_counter[result.decision] += 1
        score_band_counter[score_band(result.score)] += 1
        reason_counter.update(result.reason_codes)

        sensitive = row.get("sensitive_attributes") or {}
        actual_outcome = row.get("actual_outcome")
        if group_key and group_key in sensitive and actual_outcome is not None:
            fairness_rows.append(
                {
                    "protected_group": str(sensitive[group_key]),
                    "y_true": int(actual_outcome),
                    "y_pred": 1 if result.decision == "approve" else 0,
                }
            )

    total = len(results)
    average_score = (sum(result.score for result in results) / total) if total else 0.0
    approval_rate = (decision_counter.get("approve", 0) / total) if total else 0.0

    fairness = build_fairness_report(fairness_rows) if fairness_rows else None
    top_reasons = [
        {
            "code": code,
            "count": count,
            "description": REASONS.get(code).description if code in REASONS else code,
        }
        for code, count in reason_counter.most_common(top_reason_count)
    ]

    return {
        "summary": {
            "total_applications": total,
            "average_score": average_score,
            "approval_rate": approval_rate,
            "decision_counts": dict(sorted(decision_counter.items())),
            "score_bands": dict(sorted(score_band_counter.items())),
        },
        "top_reason_codes": top_reasons,
        "applications": [
            {
                "application_id": result.application_id,
                "score": result.score,
                "decision": result.decision,
                "reason_codes": result.reason_codes,
            }
            for result in results
        ],
        "fairness": fairness,
    }
