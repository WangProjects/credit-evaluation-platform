from __future__ import annotations

import os

import pandas as pd

from ice.pipelines.train import train_baseline_from_dataframe


def main() -> None:
    artifacts_dir = "artifacts"
    data_path = os.path.join(artifacts_dir, "data", "synth.csv")
    model_path = os.path.join(artifacts_dir, "models", "baseline.joblib")
    registry_path = os.path.join(artifacts_dir, "registry", "model_registry.json")
    report_path = os.path.join(artifacts_dir, "reports", "latest_train_report.json")

    # Create synthetic data if missing
    if not os.path.exists(data_path):
        from scripts.generate_synth_data import make_synth

        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        make_synth(n=5000, seed=7).to_csv(data_path, index=False)

    df = pd.read_csv(data_path)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model, report = train_baseline_from_dataframe(
        df=df,
        label_col="label_good",
        artifact_path=model_path,
        registry_path=registry_path,
        report_path=report_path,
        version="0.0.1",
        decision_threshold=0.5,
    )
    print(f"Trained {model.metadata.name} v{model.metadata.version}")
    print(f"Registry: {registry_path}")
    print(f"Report:   {report_path}")


if __name__ == "__main__":
    main()


