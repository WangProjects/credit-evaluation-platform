from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from ice.features.contract import DEFAULT_CONTRACT


def make_synth(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    rent = rng.beta(20, 2, size=n)  # high on-time rates
    util = rng.beta(18, 3, size=n)
    income = rng.lognormal(mean=8.1, sigma=0.35, size=n)  # ~ 3300-6000 typical
    vol = rng.beta(2, 8, size=n)  # lower volatility better
    bal = rng.lognormal(mean=7.4, sigma=0.55, size=n)  # average daily balance
    nsf = rng.poisson(lam=0.15, size=n)
    od = rng.poisson(lam=0.10, size=n)

    # Optional fields
    job = rng.integers(0, 120, size=n)
    addr = rng.integers(0, 180, size=n)

    df = pd.DataFrame(
        {
            "rent_on_time_rate_12m": rent,
            "utility_on_time_rate_12m": util,
            "avg_monthly_income_6m": income,
            "cashflow_volatility_6m": vol,
            "avg_daily_balance_6m": bal,
            "nsf_events_12m": nsf,
            "overdraft_events_12m": od,
            "months_at_current_job": job,
            "months_at_current_address": addr,
        }
    )

    # Synthetic label: higher risk if low rent/util, higher vol, more nsf/od, low income/bal
    risk = (
        (0.92 - df["rent_on_time_rate_12m"]).clip(lower=0) * 2.5
        + (0.92 - df["utility_on_time_rate_12m"]).clip(lower=0) * 2.0
        + (df["cashflow_volatility_6m"] - 0.25).clip(lower=0) * 2.0
        + (3000 - df["avg_monthly_income_6m"]).clip(lower=0) / 2500
        + (500 - df["avg_daily_balance_6m"]).clip(lower=0) / 2000
        + df["nsf_events_12m"] * 0.6
        + df["overdraft_events_12m"] * 0.5
    )
    p_default = 1 / (1 + np.exp(-(risk - 0.5)))
    y = rng.binomial(n=1, p=p_default).astype(int)  # 1 = default (bad)

    # We train on "good outcome" label, so invert: 1=good repayment
    df["label_good"] = 1 - y

    # Ensure contract columns exist
    for col in DEFAULT_CONTRACT.columns():
        if col not in df.columns:
            df[col] = 0.0

    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=str, default="artifacts/data/synth.csv")
    args = ap.parse_args()

    df = make_synth(args.n, args.seed)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()


