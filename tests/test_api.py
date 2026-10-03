from fastapi.testclient import TestClient

from nba.api.app import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_next_best_action_contract():
    payload = {
        "customer_id": "C0001",
        "channel": "traditional_trade",
        "region": "MX-CENTRAL",
        "avg_ticket": 350.0,
        "purchase_frequency_30d": 6,
        "days_since_last_purchase": 4,
        "category_affinity": 0.82,
        "historical_discount_response": 0.55,
        "price_sensitivity": 0.42,
        "contact_count_7d": 1,
    }
    response = client.post("/v1/next-best-action", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == "C0001"
    assert "selected_action" in body
    assert "policy_version" in body
    assert "model_version" in body
