from __future__ import annotations
from fastapi.testclient import TestClient

from scripts.generate_synth_data import make_synth
from ice.pipelines.train import train_baseline_from_dataframe


def test_train_and_score(tmp_path, monkeypatch):
    artifacts = tmp_path / "artifacts"
    model_path = artifacts / "models" / "baseline.joblib"
    registry_path = artifacts / "registry" / "model_registry.json"
    report_path = artifacts / "reports" / "latest_train_report.json"
    audit_log_path = artifacts / "audit" / "decisions.jsonl"

    df = make_synth(n=2000, seed=3)
    train_baseline_from_dataframe(
        df=df,
        label_col="label_good",
        artifact_path=str(model_path),
        registry_path=str(registry_path),
        report_path=str(report_path),
        version="0.0.1",
        decision_threshold=0.5,
    )

    monkeypatch.setenv("ICE_REGISTRY_PATH", str(registry_path))
    monkeypatch.setenv("ICE_CURRENT_MODEL_PATH", str(model_path))
    monkeypatch.setenv("ICE_AUDIT_LOG_PATH", str(audit_log_path))
    monkeypatch.setenv("ICE_ENABLE_SQLITE_AUDIT_STORE", "false")

    from services.api.app import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200

    payload = {
        "application_id": "app_test",
        "features": {
            "rent_on_time_rate_12m": 0.96,
            "utility_on_time_rate_12m": 0.93,
            "avg_monthly_income_6m": 4500,
            "cashflow_volatility_6m": 0.12,
            "avg_daily_balance_6m": 1800,
            "nsf_events_12m": 0,
            "overdraft_events_12m": 0,
        },
        "sensitive_attributes": {"age_band": "25-34"},
    }
    r2 = client.post("/v1/score", json=payload)
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["application_id"] == "app_test"
    assert 0.0 <= body["score"] <= 1.0
    assert body["decision"] in ("approve", "deny")
    assert isinstance(body["reason_codes"], list)


