from __future__ import annotations

from nba.domain.models import CandidateAction, CustomerContext, DecisionResponse, ScoredAction
from nba.ml.model import PropensityModel


class DecisionEngine:
    def __init__(self, model: PropensityModel, actions: list[CandidateAction], policy: dict) -> None:
        self.model = model
        self.actions = actions
        self.policy = policy

    def _eligibility(self, customer: CustomerContext, action: CandidateAction) -> list[str]:
        if action.action_type == "no_action":
            return []

        reasons: list[str] = []
        if action.inventory_units < self.policy["min_inventory_units"]:
            reasons.append("insufficient_inventory")

        if customer.contact_count_7d >= self.policy["max_contacts_7d"] and action.contact_cost > 0:
            reasons.append("contact_frequency_cap")

        if (
            action.price > 0
            and customer.avg_ticket > 0
            and action.price
            > customer.avg_ticket * self.policy["max_price_tolerance_multiplier"]
        ):
            reasons.append("price_tolerance_exceeded")

        if action.risk_penalty >= self.policy["risk_penalty_threshold"]:
            reasons.append("risk_threshold_exceeded")

        return reasons

    def _score(self, customer: CustomerContext, action: CandidateAction) -> ScoredAction:
        reasons = self._eligibility(customer, action)
        if action.action_type == "no_action":
            propensity = None
            gross_value = 0.0
            utility = 0.0
        else:
            propensity = self.model.predict(customer, action)
            gross_value = propensity * action.expected_margin
            utility = gross_value - action.discount_cost - action.contact_cost - action.risk_penalty

        return ScoredAction(
            action_id=action.action_id,
            action_type=action.action_type,
            propensity=round(propensity, 6) if propensity is not None else None,
            gross_expected_value=round(gross_value, 4),
            expected_utility=round(utility, 4),
            eligible=not reasons,
            exclusion_reasons=reasons,
        )

    def decide(self, customer: CustomerContext) -> DecisionResponse:
        scores = [self._score(customer, action) for action in self.actions]
        eligible = [x for x in scores if x.eligible]
        eligible.sort(key=lambda x: x.expected_utility, reverse=True)

        if not eligible:
            raise RuntimeError("No eligible actions; policy must permit a safe fallback")

        selected = eligible[0]
        if selected.expected_utility < self.policy["minimum_utility"]:
            fallback = next((x for x in eligible if x.action_type == "no_action"), selected)
            selected = fallback

        rationale_codes = [
            "highest_eligible_expected_utility",
            "policy_constraints_applied",
            "model_propensity_used",
        ]
        if selected.action_type == "no_action":
            rationale_codes.append("minimum_utility_not_met")

        return DecisionResponse(
            customer_id=customer.customer_id,
            selected_action=selected.action_id,
            expected_utility=selected.expected_utility,
            propensity=selected.propensity,
            policy_version=self.policy["policy_version"],
            model_version=self.model.version,
            rationale_codes=rationale_codes,
            alternatives=scores,
        )
