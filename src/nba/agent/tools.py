from __future__ import annotations

import hashlib

from nba.agent.semantic import get_definition
from nba.domain.models import CustomerContext, DecisionResponse
from nba.services.factory import build_engine


def _customer(value: CustomerContext | dict) -> CustomerContext:
    return value if isinstance(value, CustomerContext) else CustomerContext.model_validate(value)


def _decision(value: DecisionResponse | dict) -> DecisionResponse:
    return value if isinstance(value, DecisionResponse) else DecisionResponse.model_validate(value)


def get_next_best_action(customer: CustomerContext | dict) -> dict:
    """Return the governed Next Best Action. The caller cannot override policy or ranking."""
    decision = build_engine().decide(_customer(customer))
    return decision.model_dump()


def explain_decision(decision: DecisionResponse | dict) -> dict:
    """Return grounded facts that can be used to explain a governed NBA decision."""
    decision = _decision(decision)
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
        "rationale_codes": decision.rationale_codes,
        "explanation_facts": [
            "The selected action had the highest eligible expected utility.",
            "Commercial policy constraints were evaluated before ranking.",
            *(
                ["The propensity score came from the registered decision model."]
                if selected.propensity is not None
                else ["No-action is a deterministic fallback and has no response propensity score."]
            ),
        ],
    }


def compare_action_alternatives(decision: DecisionResponse | dict) -> dict:
    """Rank eligible alternatives and preserve exclusions for auditability."""
    decision = _decision(decision)
    ranked = sorted(
        [item for item in decision.alternatives if item.eligible],
        key=lambda item: item.expected_utility,
        reverse=True,
    )
    excluded = [item for item in decision.alternatives if not item.eligible]
    return {
        "customer_id": decision.customer_id,
        "selected_action": decision.selected_action,
        "ranked_eligible_actions": [item.model_dump() for item in ranked],
        "excluded_actions": [item.model_dump() for item in excluded],
        "policy_version": decision.policy_version,
        "model_version": decision.model_version,
    }


def get_business_definition(term: str) -> dict:
    """Resolve a term through the governed semantic catalog rather than free-form generation."""
    return get_definition(term)


def create_action_proposal(customer: CustomerContext | dict, reason: str) -> dict:
    """Create an approval request for the governed NBA only; never execute externally."""
    decision = get_next_best_action(customer)
    customer_id = decision["customer_id"]
    action_id = decision["selected_action"]
    seed = f"{customer_id}|{action_id}|{decision['policy_version']}|{reason}".encode("utf-8")
    proposal_id = "apr_" + hashlib.sha256(seed).hexdigest()[:16]
    return {
        "proposal_id": proposal_id,
        "customer_id": customer_id,
        "action_id": action_id,
        "status": "approval_required",
        "reason": reason,
        "model_version": decision["model_version"],
        "policy_version": decision["policy_version"],
        "external_action_executed": False,
    }
