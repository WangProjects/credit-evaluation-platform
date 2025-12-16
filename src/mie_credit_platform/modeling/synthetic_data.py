from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticDataConfig:
    n: int = 5000
    seed: int = 7


def make_synthetic_alt_data(cfg: SyntheticDataConfig) -> pd.DataFrame:
    """
    Generate a synthetic dataset representing alternative-data signals.

    This is **only** for demo/testing. Replace with governed datasets and feature engineering.
    """

    rng = np.random.default_rng(cfg.seed)

    rent = np.clip(rng.normal(0.9, 0.08, cfg.n), 0, 1)
    util = np.clip(rng.normal(0.92, 0.07, cfg.n), 0, 1)
    cash_vol = np.clip(rng.lognormal(mean=-1.0, sigma=0.6, size=cfg.n), 0, 5)
    inc_stab = np.clip(rng.beta(6, 2, cfg.n), 0, 1)
    inflow = np.clip(rng.normal(3200, 1400, cfg.n), -10000, 100000)
    balance = np.clip(rng.normal(900, 1200, cfg.n), -5000, 100000)
    overdraft = np.clip(rng.poisson(0.6, cfg.n), 0, 50)
    months_addr = np.clip(rng.integers(1, 72, cfg.n), 1, 240)

    # Hidden "true" risk model to create labels.
    # Higher rent/util/inc_stab/balance reduce default; overdraft/cash_vol increase.
    z = (
        2.2 * rent
        + 2.0 * util
        + 1.6 * inc_stab
        + 0.00035 * inflow
        + 0.00045 * balance
        - 0.65 * cash_vol
        - 0.35 * overdraft
        + 0.02 * np.log1p(months_addr)
        - 2.0
    )
    # Convert to probability of "good outcome"
    p_good = 1 / (1 + np.exp(-z))
    y = (rng.uniform(size=cfg.n) < p_good).astype(int)

    df = pd.DataFrame(
        {
            "rent_on_time_ratio_12m": rent,
            "utilities_on_time_ratio_12m": util,
            "cashflow_volatility_90d": cash_vol,
            "income_stability_6m": inc_stab,
            "avg_monthly_net_inflow_6m": inflow,
            "avg_daily_balance_90d": balance,
            "overdraft_count_12m": overdraft,
            "months_at_address": months_addr,
            "y": y,
        }
    )
    # small noise to avoid perfect separability
    df["avg_daily_balance_90d"] = df["avg_daily_balance_90d"] + rng.normal(0, 50, cfg.n)
    df["avg_monthly_net_inflow_6m"] = df["avg_monthly_net_inflow_6m"] + rng.normal(0, 80, cfg.n)

    # Optional: synthetic protected group for fairness testing (NOT a feature)
    # This intentionally correlates slightly with income/balance to demonstrate auditing.
    g = np.where((inflow + balance) > np.median(inflow + balance), "group_A", "group_B")
    # Add mild label shift
    shift = np.where(g == "group_B", -0.04, 0.0)
    y2 = (rng.uniform(size=cfg.n) < np.clip(p_good + shift, 0, 1)).astype(int)
    df["y"] = y2
    df["protected_group"] = g

    # sanity
    df["months_at_address"] = df["months_at_address"].astype(int)
    df["overdraft_count_12m"] = df["overdraft_count_12m"].astype(int)
    return df


