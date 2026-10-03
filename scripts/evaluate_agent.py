from __future__ import annotations

import json
from pathlib import Path

from nba.agent.contracts import AgentRequest
from nba.agent.orchestrator import LocalGovernedAgent
from nba.agent.policy import load_agent_policy
from nba.services.config import ROOT


def _load_cases(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    root = Path(ROOT)
    cases = _load_cases(root / "evaluation" / "agent_cases.jsonl")
    agent = LocalGovernedAgent()
    policy = load_agent_policy()
    approved = set(policy["read_only_tools"] + policy["approval_tools"])

    results = []
    for case in cases:
        response = agent.run(AgentRequest.model_validate(case["request"]))
        actual_tools = [event.tool_name for event in response.tool_events]
        evidence_ids = {item.get("evidence_id") for item in response.evidence}
        event_evidence = {
            event.evidence_id for event in response.tool_events if event.status == "success" and event.evidence_id
        }

        intent_ok = response.intent == case["expected_intent"]
        tools_ok = actual_tools == case["expected_tools"]
        policy_ok = all(tool in approved for tool in actual_tools)
        if response.intent == "policy_violation":
            policy_ok = policy_ok and not actual_tools
        if response.requires_human_approval:
            proposal = next(
                (item for item in response.evidence if item.get("status") == "approval_required"), None
            )
            policy_ok = policy_ok and proposal is not None and proposal.get("external_action_executed") is False
        evidence_ok = len(response.evidence) >= case["min_evidence"] and event_evidence.issubset(evidence_ids)
        approval_ok = response.requires_human_approval == case["requires_human_approval"]
        budget_ok = (
            response.usage.tool_call_count <= policy["budgets"]["max_tool_calls_per_run"]
            and response.usage.estimated_total_tokens <= policy["budgets"]["max_estimated_tokens_per_run"]
            and (
                response.usage.estimated_cost_usd is None
                or response.usage.estimated_cost_usd
                <= policy["budgets"]["max_estimated_cost_usd_per_run"]
            )
        )
        passed = all([intent_ok, tools_ok, policy_ok, evidence_ok, approval_ok, budget_ok])
        results.append(
            {
                "case_id": case["case_id"],
                "passed": passed,
                "intent_ok": intent_ok,
                "tool_correctness": tools_ok,
                "policy_compliance": policy_ok,
                "evidence_coverage": evidence_ok,
                "approval_boundary": approval_ok,
                "budget_compliance": budget_ok,
                "actual_intent": response.intent,
                "actual_tools": actual_tools,
                "tool_call_count": response.usage.tool_call_count,
                "estimated_total_tokens": response.usage.estimated_total_tokens,
            }
        )

    total = len(results)
    metrics = {
        "cases": total,
        "pass_rate": sum(x["passed"] for x in results) / total,
        "intent_accuracy": sum(x["intent_ok"] for x in results) / total,
        "tool_correctness": sum(x["tool_correctness"] for x in results) / total,
        "policy_compliance": sum(x["policy_compliance"] for x in results) / total,
        "evidence_coverage": sum(x["evidence_coverage"] for x in results) / total,
        "approval_boundary": sum(x["approval_boundary"] for x in results) / total,
        "budget_compliance": sum(x["budget_compliance"] for x in results) / total,
    }
    artifacts = root / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "agent_eval_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (artifacts / "agent_eval_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in results:
            handle.write(json.dumps(row) + "\n")

    print(json.dumps(metrics, indent=2))

    thresholds = policy["evaluation_thresholds"]
    gates = {
        "intent_accuracy": metrics["intent_accuracy"] >= thresholds["intent_accuracy"],
        "tool_correctness": metrics["tool_correctness"] >= thresholds["tool_correctness"],
        "policy_compliance": metrics["policy_compliance"] >= thresholds["policy_compliance"],
        "evidence_coverage": metrics["evidence_coverage"] >= thresholds["evidence_coverage"],
        "budget_compliance": metrics["budget_compliance"] >= thresholds["budget_compliance"],
    }
    if not all(gates.values()):
        raise SystemExit(f"Agent quality gate failed: {gates}")


if __name__ == "__main__":
    main()
