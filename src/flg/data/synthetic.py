from __future__ import annotations

import numpy as np
import pandas as pd

from flg.features.schema import FEATURE_ORDER


def make_synthetic_training_data(n: int = 5000, seed: int = 7) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Generate a synthetic dataset for demo/testing.

    Returns:
      X: engineered features
      y: binary label (1=good outcome, 0=bad outcome)
      group: synthetic protected group label for fairness reporting

    NOTE: This is NOT representative of any real population.
    """

    rng = np.random.default_rng(seed)

    group = rng.choice(["A", "B"], size=n, p=[0.6, 0.4])

    rent = rng.beta(12, 2, size=n)  # mostly on-time
    utils = rng.beta(10, 3, size=n)
    income = rng.lognormal(mean=8.2, sigma=0.45, size=n)  # ~ 3k-7k
    vol = rng.gamma(shape=2.0, scale=0.15, size=n)  # 0.0-1.0-ish
    bal = rng.normal(loc=1200, scale=800, size=n)
    overdrafts = rng.poisson(lam=0.4, size=n)
    months_job = rng.integers(0, 120, size=n)
    months_addr = rng.integers(0, 180, size=n)

    # Inject group shift for demonstration (not a statement about reality)
    income = income * np.where(group == "B", 0.92, 1.0)
    overdrafts = overdrafts + np.where(group == "B", rng.poisson(0.15, size=n), 0)

    X = pd.DataFrame(
        {
            "rent_on_time_rate_12m": rent,
            "utilities_on_time_rate_12m": utils,
            "cashflow_income_monthly": income,
            "cashflow_volatility_3m": vol,
            "avg_daily_balance_30d": bal,
            "overdraft_events_90d": overdrafts,
            "months_at_job": months_job,
            "months_at_address": months_addr,
        }
    )

    # Logistic-ish outcome with noise.
    z = (
        2.2 * (rent - 0.8)
        + 1.6 * (utils - 0.75)
        + 0.00025 * (income - 4500)
        - 1.2 * vol
        + 0.00035 * (bal - 800)
        - 0.45 * overdrafts
        + 0.006 * months_job
        + 0.003 * months_addr
        + rng.normal(0, 0.6, size=n)
    )
    p = 1 / (1 + np.exp(-z))
    y = (p > 0.5).astype(int)

    X = X[FEATURE_ORDER]
    return X, pd.Series(y, name="y"), pd.Series(group, name="group")
