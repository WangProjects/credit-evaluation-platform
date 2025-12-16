from __future__ import annotations

from fastapi.testclient import TestClient

from flg.api.main import app
from flg.ml.train import train_demo_model


def test_train_and_score_smoke(tmp_path):
    # Train in-memory
    bundle = train_demo_model(n=500, seed=3)
    assert bundle.model_version

    # Patch app settings model path by saving artifact
    import joblib

    model_path = tmp_path / "model.joblib"
    joblib.dump(bundle, model_path)

    # Monkeypatch settings
    from flg.config import settings

    settings.model_path = model_path

    client = TestClient(app)
    resp = client.post(
        "/v1/score",
        json={
            "applicant_id": "t1",
            "features": {
                "rent_on_time_rate_12m": 0.95,
                "utilities_on_time_rate_12m": 0.9,
                "cashflow_income_monthly": 4500,
                "cashflow_volatility_3m": 0.25,
                "avg_daily_balance_30d": 1200,
                "overdraft_events_90d": 0,
                "months_at_job": 18,
                "months_at_address": 24,
            },
            "protected_attributes": {"group": "A"},
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert 0.0 <= body["score"] <= 1.0
    assert body["decision"] in {"approve", "review", "deny"}
    assert body["audit_id"]
