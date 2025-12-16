from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import joblib
from rich.console import Console
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from flg.data.synthetic import make_synthetic_training_data
from flg.ml.model import CreditModelBundle


def _model_version_from_data(seed: int, n: int) -> str:
    h = hashlib.sha256(f"synthetic:{seed}:{n}".encode("utf-8")).hexdigest()[:12]
    return f"demo-{h}"


def train_demo_model(n: int = 5000, seed: int = 7) -> CreditModelBundle:
    X, y, _group = make_synthetic_training_data(n=n, seed=seed)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )

    pipe = Pipeline(
        steps=[
            ("scaler", StandardScaler(with_mean=True, with_std=True)),
            ("clf", LogisticRegression(max_iter=2000, n_jobs=1)),
        ]
    )
    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)

    version = _model_version_from_data(seed, n)
    bundle = CreditModelBundle.build(
        pipe,
        model_version=version,
        thresholds={"approve": 0.72, "review": 0.58},
    )
    bundle.extra["demo_accuracy"] = float(score)
    bundle.extra["seed"] = seed
    bundle.extra["n"] = n
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a demo alternative-data credit model.")
    parser.add_argument("--out", type=str, default="artifacts/model.joblib", help="Output path")
    parser.add_argument("--n", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    console = Console()
    console.print(f"Training demo model (n={args.n}, seed={args.seed})...")
    bundle = train_demo_model(n=args.n, seed=args.seed)
    joblib.dump(bundle, out)
    console.print(f"Saved: {out} (model_version={bundle.model_version})")


if __name__ == "__main__":
    main()
