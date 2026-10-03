from __future__ import annotations

import re
import uuid
from typing import Any

from nba.agent.contracts import AgentRequest, AgentResponse, AgentUsage, ToolAuditEvent
from nba.agent.policy import load_agent_policy
from nba.agent.registry import GovernedToolRegistry, ToolResult
from nba.agent.semantic import load_semantic_catalog
from nba.agent.telemetry import cost_profile_from_env, estimate_cost, estimate_tokens, log_agent_event
from nba.agent.tools import (
    compare_action_alternatives,
    create_action_proposal,
    explain_decision,
    get_business_definition,
    get_next_best_action,
)


class LocalGovernedAgent:
    """Deterministic reference orchestrator used for local policy and contract tests.

    Production generative behavior is provided by the Microsoft Foundry/LangGraph integration.
    This local agent intentionally contains no LLM so tool contracts and policy failures can be
    tested independently from model variance.
    """

    def __init__(self) -> None:
        self.policy = load_agent_policy()

    def _registry(self) -> GovernedToolRegistry:
        registry = GovernedToolRegistry()
        registry.register("get_next_best_action", get_next_best_action)
        registry.register("explain_decision", explain_decision)
        registry.register("compare_action_alternatives", compare_action_alternatives)
        registry.register("get_business_definition", get_business_definition)
        registry.register("create_action_proposal", create_action_proposal)
        return registry

    @staticmethod
    def _route(request: AgentRequest) -> str:
        message = request.message.lower()
        if any(x in message for x in ["ignore policy", "override policy", "force ", "bypass policy"]):
            return "policy_violation"
        if any(x in message for x in ["execute ", "send it", "apply it", "place the order"]):
            return "approval_request"
        if any(x in message for x in ["why", "explain", "rationale"]):
            return "explanation"
        if any(x in message for x in ["compare", "alternative", "runner-up", "runner up"]):
            return "comparison"
        if request.term or any(x in message for x in ["define", "what does", "what is", "meaning of"]):
            catalog_terms = load_semantic_catalog()["terms"].keys()
            if request.term or any(term.replace("_", " ") in message for term in catalog_terms):
                return "semantic_definition"
        if any(x in message for x in ["next best action", "recommend", "best action", "what should"]):
            return "decision"
        return "unsupported"

    @staticmethod
    def _event(result: ToolResult) -> ToolAuditEvent:
        return ToolAuditEvent(
            tool_name=result.tool_name,
            status="success",
            evidence_id=result.evidence_id,
            detail={"access_mode": result.access_mode},
        )

    def _decision(self, registry: GovernedToolRegistry, request: AgentRequest) -> ToolResult:
        if request.customer is None:
            raise ValueError("A governed customer context is required for customer-specific decisioning")
        return registry.execute("get_next_best_action", customer=request.customer.model_dump())

    @staticmethod
    def _term_from_message(request: AgentRequest) -> str:
        if request.term:
            return request.term
        message = request.message.lower()
        for key in load_semantic_catalog()["terms"]:
            if key.replace("_", " ") in message:
                return key
        cleaned = re.sub(r"[^a-zA-Z0-9 _-]", "", request.message)
        return cleaned.strip()

    def run(self, request: AgentRequest) -> AgentResponse:
        request_id = f"req_{uuid.uuid4().hex[:16]}"
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"
        registry = self._registry()
        intent = self._route(request)
        evidence: list[dict[str, Any]] = []
        events: list[ToolAuditEvent] = []
        requires_approval = False

        if intent == "policy_violation":
            answer = (
                "I cannot bypass the governed ranking or commercial policy. "
                "I can return the policy-compliant Next Best Action and explain the result."
            )
        elif intent == "semantic_definition":
            result = registry.execute("get_business_definition", term=self._term_from_message(request))
            evidence.append({"evidence_id": result.evidence_id, **result.payload})
            events.append(self._event(result))
            if result.payload.get("found"):
                answer = f"{result.payload['label']}: {result.payload['definition']}"
            else:
                answer = "That term is not present in the governed semantic catalog."
        elif intent in {"decision", "explanation", "comparison", "approval_request"}:
            decision = self._decision(registry, request)
            evidence.append({"evidence_id": decision.evidence_id, **decision.payload})
            events.append(self._event(decision))

            if intent == "decision":
                answer = (
                    f"The governed Next Best Action is {decision.payload['selected_action']} "
                    f"with expected utility {decision.payload['expected_utility']}."
                )
            elif intent == "explanation":
                explained = registry.execute("explain_decision", decision=decision.payload)
                evidence.append({"evidence_id": explained.evidence_id, **explained.payload})
                events.append(self._event(explained))
                runner = explained.payload.get("runner_up")
                suffix = f" The runner-up was {runner['action_id']}." if runner else ""
                answer = (
                    f"{decision.payload['selected_action']} ranked first among eligible actions after "
                    f"policy constraints and expected-utility scoring.{suffix}"
                )
            elif intent == "comparison":
                compared = registry.execute("compare_action_alternatives", decision=decision.payload)
                evidence.append({"evidence_id": compared.evidence_id, **compared.payload})
                events.append(self._event(compared))
                top = compared.payload["ranked_eligible_actions"][:2]
                answer = "Top eligible actions: " + ", ".join(
                    f"{x['action_id']} ({x['expected_utility']})" for x in top
                )
            else:
                proposal = registry.execute(
                    "create_action_proposal",
                    customer=request.customer.model_dump(),
                    reason="Requested through the commercial assistant after governed NBA evaluation.",
                )
                evidence.append({"evidence_id": proposal.evidence_id, **proposal.payload})
                events.append(self._event(proposal))
                requires_approval = True
                answer = (
                    f"I created proposal {proposal.payload['proposal_id']} for the governed action "
                    f"{proposal.payload['action_id']}. No external action was executed; human approval is required."
                )
        else:
            answer = (
                "I can calculate a governed Next Best Action, explain or compare alternatives, "
                "define governed commercial metrics, or create an approval-required action proposal."
            )

        input_tokens = estimate_tokens(request.message)
        output_tokens = estimate_tokens(answer)
        usage = AgentUsage(
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=estimate_cost(input_tokens, output_tokens, cost_profile_from_env()),
            tool_call_count=registry.call_count,
        )
        log_agent_event(
            "agent_run",
            {
                "request_id": request_id,
                "trace_id": trace_id,
                "intent": intent,
                "tool_calls": [e.tool_name for e in events],
                "estimated_tokens": usage.estimated_total_tokens,
            },
        )
        return AgentResponse(
            request_id=request_id,
            trace_id=trace_id,
            agent_version=self.policy["agent_version"],
            agent_policy_version=self.policy["policy_version"],
            intent=intent,
            answer=answer,
            evidence=evidence,
            tool_events=events,
            usage=usage,
            requires_human_approval=requires_approval,
        )
