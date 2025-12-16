from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mie_credit_platform.modeling.model_io import ModelPackage, save_model_package
from mie_credit_platform.modeling.synthetic_data import SyntheticDataConfig, make_synthetic_alt_data


@dataclass(frozen=True)
class TrainConfig:
    version: str
    registry_dir: str
    seed: int = 7
    test_size: float = 0.2
    n_synth: int = 8000


def train_baseline_logreg(cfg: TrainConfig) -> dict[str, Any]:
    df = make_synthetic_alt_data(SyntheticDataConfig(n=cfg.n_synth, seed=cfg.seed))
    feature_names = [
        "rent_on_time_ratio_12m",
        "utilities_on_time_ratio_12m",
        "cashflow_volatility_90d",
        "income_stability_6m",
        "avg_monthly_net_inflow_6m",
        "avg_daily_balance_90d",
        "overdraft_count_12m",
        "months_at_address",
    ]
    X = df[feature_names].copy()
    y = df["y"].astype(int).to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg.test_size, random_state=cfg.seed, stratify=y
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, n_jobs=1)),
        ]
    )
    model.fit(X_train, y_train)

    p = model.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, p))

    metadata = {
        "created_at_unix": time.time(),
        "model_type": "logistic_regression",
        "framework": "scikit-learn",
        "features": feature_names,
        "training": {
            "seed": cfg.seed,
            "n_rows": int(len(df)),
            "test_size": float(cfg.test_size),
        },
        "metrics": {"roc_auc": auc},
        "data": {"source": "synthetic_alt_data_demo_only"},
        "notes": "Demo baseline. Replace with governed training data and full compliance review.",
    }

    pkg = ModelPackage(version=cfg.version, model=model, feature_names=feature_names, metadata=metadata)
    out_dir = save_model_package(pkg, cfg.registry_dir)
    (out_dir / "model_card.md").write_text(_default_model_card(metadata), encoding="utf-8")

    return {"version": cfg.version, "registry_dir": cfg.registry_dir, "roc_auc": auc, "out_dir": str(out_dir)}


def _default_model_card(metadata: dict[str, Any]) -> str:
    return (
        "## Model Card (Template)\n\n"
        "### Summary\n"
        f"- **Model type**: {metadata.get('model_type')}\n"
        f"- **Created**: {metadata.get('created_at_unix')}\n"
        f"- **Primary metric (demo)**: ROC-AUC={metadata.get('metrics', {}).get('roc_auc')}\n\n"
        "### Intended use\n"
        "- Provide a baseline example of an explainable, auditable credit-score component using alternative-data "
        "features.\n\n"
        "### Out-of-scope uses\n"
        "- Do not use as a production credit model.\n"
        "- Do not use protected-class attributes as features.\n\n"
        "### Data\n"
        "- This package was trained on **synthetic data** for demo purposes.\n\n"
        "### Fairness & compliance\n"
        "- Run fairness evaluation with held-out real data under governance controls.\n"
        "- Document adverse action reason codes and model limitations.\n\n"
        "### Approval\n"
        "- This model is **not approved** by default. Use `mie approve-model` after review.\n"
    )


