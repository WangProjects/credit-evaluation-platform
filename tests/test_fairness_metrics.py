from __future__ import annotations

from ice.fairness.metrics import (
    demographic_parity_difference,
    equal_opportunity_difference,
    selection_rates_by_group,
    tpr_by_group,
)


def test_selection_rates_by_group():
    groups = ["a", "a", "b", "b", "b"]
    y_pred = [1, 0, 1, 1, 0]
    rates = selection_rates_by_group(groups, y_pred)
    assert rates == {"a": 0.5, "b": 2 / 3}


def test_tpr_and_fairness_differences():
    groups = ["a", "a", "b", "b", "b", "c"]
    y_true = [1, 1, 1, 0, 1, 1]
    y_pred = [1, 0, 1, 0, 1, 0]

    tpr = tpr_by_group(groups, y_true, y_pred)
    assert tpr == {"a": 0.5, "b": 1.0, "c": 0.0}

    selection = selection_rates_by_group(groups, y_pred)
    assert round(demographic_parity_difference(selection), 4) == round((2 / 3) - 0.5, 4)
    assert equal_opportunity_difference(tpr) == 1.0
