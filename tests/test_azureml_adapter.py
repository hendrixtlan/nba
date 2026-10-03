from __future__ import annotations

import json

import pytest

from nba.adapters import azureml_model
from nba.adapters.azureml_model import AzureMLPropensityModel
from nba.domain.models import CandidateAction, CustomerContext


class _Token:
    token = "fake-token"


class _Credential:
    def get_token(self, scope):
        assert scope == "https://ml.azure.com/.default"
        return _Token()


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"probabilities": [0.71], "model_version": "test-v1"}).encode()


def test_azureml_adapter_requires_https():
    with pytest.raises(ValueError):
        AzureMLPropensityModel("http://example.test/score")


def test_azureml_adapter_uses_entra_token_and_feature_contract(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["authorization"] = req.get_header("Authorization")
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode())
        return _Response()

    monkeypatch.setattr(azureml_model.request, "urlopen", fake_urlopen)
    model = AzureMLPropensityModel(
        "https://example.inference.ml.azure.com/score",
        credential=_Credential(),
        timeout_seconds=3.0,
    )
    customer = CustomerContext(
        customer_id="C1", channel="traditional_trade", region="MX-CENTRAL",
        avg_ticket=350, purchase_frequency_30d=6, days_since_last_purchase=4,
        category_affinity=.82, historical_discount_response=.55,
        price_sensitivity=.42, contact_count_7d=1,
    )
    action = CandidateAction(
        action_id="a1", action_type="product", expected_margin=12, discount_cost=1,
        contact_cost=.5, price=320, inventory_units=100, risk_penalty=.05,
    )
    assert model.predict(customer, action) == pytest.approx(.71)
    assert captured["authorization"] == "Bearer fake-token"
    assert captured["timeout"] == 3.0
    assert captured["body"]["input_data"][0]["action_id"] == "a1"
