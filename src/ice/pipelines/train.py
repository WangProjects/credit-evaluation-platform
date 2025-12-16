from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from ice.features.contract import DEFAULT_CONTRACT
from ice.models.sklearn_logreg import SklearnLogRegCreditModel, new_untrained_bundle, save_bundle
from ice.models.registry import add_model


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def train_baseline_from_dataframe(
    df: pd.DataFrame,
    label_col: str,
    artifact_path: str,
    registry_path: str,
    report_path: str,
    version: str = "0.0.1",
    decision_threshold: float = 0.5,
) -> Tuple[SklearnLogRegCreditModel, Dict[str, object]]:
    contract = DEFAULT_CONTRACT
    cols = list(contract.columns())
    missing_cols = [c for c in cols + [label_col] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    X = df[cols].astype(float).values
    y = df[label_col].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7)

    bundle = new_untrained_bundle(version=version, decision_threshold=decision_threshold)
    bundle.model.fit(X_train, y_train)
    save_bundle(artifact_path, bundle)

    model = SklearnLogRegCreditModel(bundle)
    y_score = bundle.model.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, y_score)) if len(set(y_test.tolist())) > 1 else 0.0

    report = {
        "model_name": model.metadata.name,
        "model_version": model.metadata.version,
        "feature_schema_hash": model.metadata.feature_schema_hash,
        "metrics": {"roc_auc": auc},
        "notes": "Synthetic/demo baseline training run.",
    }

    _ensure_dir(os.path.dirname(report_path))
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    add_model(
        registry_path=registry_path,
        metadata=model.metadata,
        artifact_path=artifact_path,
        metrics=report["metrics"],
        fairness={},
        notes=report["notes"],
        set_current=True,
    )
    return model, report


