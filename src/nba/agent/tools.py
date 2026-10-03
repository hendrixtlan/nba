from __future__ import annotations

from nba.domain.models import CustomerContext, DecisionResponse
from nba.services.factory import build_engine


def get_next_best_action(customer: CustomerContext) -> DecisionResponse:
    """Governed tool exposed to an agent. The agent cannot override policy or ranking."""
    return build_engine().decide(customer)


def explain_decision(decision: DecisionResponse) -> dict:
    selected = next(x for x in decision.alternatives if x.action_id == decision.selected_action)
    eligible_alternatives = sorted(
        [x for x in decision.alternatives if x.eligible and x.action_id != decision.selected_action],
        key=lambda x: x.expected_utility,
        reverse=True,
    )
    runner_up = eligible_alternatives[0] if eligible_alternatives else None

    return {
        "customer_id": decision.customer_id,
        "selected_action": decision.selected_action,
        "propensity": selected.propensity,
        "expected_utility": selected.expected_utility,
        "runner_up": runner_up.model_dump() if runner_up else None,
        "policy_version": decision.policy_version,
        "model_version": decision.model_version,
        "explanation_facts": [
            "The selected action had the highest eligible expected utility.",
            "Commercial policy constraints were evaluated before ranking.",
            "The propensity score came from the registered decision model.",
        ],
    }
