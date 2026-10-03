from fastapi.testclient import TestClient

from nba.api.app import app

client = TestClient(app)


def test_agent_endpoint_returns_governed_decision():
    payload = {
        "message": "What is the next best action?",
        "customer": {
            "customer_id": "C901",
            "channel": "traditional_trade",
            "region": "MX-CENTRAL",
            "avg_ticket": 350,
            "purchase_frequency_30d": 6,
            "days_since_last_purchase": 4,
            "category_affinity": 0.82,
            "historical_discount_response": 0.55,
            "price_sensitivity": 0.42,
            "contact_count_7d": 1,
        },
    }
    response = client.post("/v1/agent/run", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "decision"
    assert body["tool_events"][0]["tool_name"] == "get_next_best_action"
    assert body["evidence"]
