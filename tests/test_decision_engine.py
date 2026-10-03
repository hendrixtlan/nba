from nba.domain.models import CandidateAction, CustomerContext
from nba.ml.model import HeuristicPropensityModel
from nba.services.decision_engine import DecisionEngine


def customer(**overrides):
    base = dict(
        customer_id="C1",
        channel="traditional_trade",
        region="MX-CENTRAL",
        avg_ticket=350,
        purchase_frequency_30d=6,
        days_since_last_purchase=3,
        category_affinity=0.8,
        historical_discount_response=0.5,
        price_sensitivity=0.4,
        contact_count_7d=0,
    )
    base.update(overrides)
    return CustomerContext(**base)


def actions():
    return [
        CandidateAction(
            action_id="high_value",
            action_type="bundle",
            expected_margin=14,
            discount_cost=1,
            contact_cost=0.2,
            price=360,
            inventory_units=100,
            risk_penalty=0,
        ),
        CandidateAction(
            action_id="no_action",
            action_type="no_action",
            expected_margin=0,
            discount_cost=0,
            contact_cost=0,
            price=0,
            inventory_units=9999,
            risk_penalty=0,
        ),
    ]


def policy():
    return {
        "policy_version": "test-v1",
        "max_contacts_7d": 2,
        "min_inventory_units": 10,
        "max_price_tolerance_multiplier": 1.15,
        "risk_penalty_threshold": 0.8,
        "minimum_utility": 0.25,
    }


def test_engine_returns_versioned_decision():
    result = DecisionEngine(HeuristicPropensityModel(), actions(), policy()).decide(customer())
    assert result.policy_version == "test-v1"
    assert result.model_version == "heuristic-v1"
    assert result.selected_action in {"high_value", "no_action"}


def test_contact_cap_excludes_contact_action():
    result = DecisionEngine(HeuristicPropensityModel(), actions(), policy()).decide(
        customer(contact_count_7d=2)
    )
    high = next(x for x in result.alternatives if x.action_id == "high_value")
    assert not high.eligible
    assert "contact_frequency_cap" in high.exclusion_reasons
