from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
from rich.console import Console
from sklearn.metrics import roc_auc_score

from flg.data.synthetic import make_synthetic_training_data
from flg.fairness.metrics import group_fairness_report
from flg.ml.model import CreditModelBundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved model bundle on synthetic data.")
    parser.add_argument("--model", type=str, default="artifacts/model.joblib")
    parser.add_argument("--n", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    console = Console()

    bundle: CreditModelBundle = joblib.load(Path(args.model))
    X, y, group = make_synthetic_training_data(n=args.n, seed=args.seed)

    y_score = bundle.model.predict_proba(X)[:, 1]
    auc = roc_auc_score(y, y_score)

    report = group_fairness_report(
        y_true=np.asarray(y), y_score=np.asarray(y_score), group=np.asarray(group)
    )

    console.print({"model_version": bundle.model_version, "auc": float(auc), "fairness": report})


if __name__ == "__main__":
    main()
