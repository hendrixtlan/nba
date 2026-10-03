from __future__ import annotations

from typing import Any, TypedDict

from nba.agent.contracts import AgentRequest
from nba.agent.orchestrator import LocalGovernedAgent


class WorkflowState(TypedDict, total=False):
    request: dict[str, Any]
    response: dict[str, Any]


def build_contract_validation_graph():
    """Build a LangGraph workflow for deterministic contract/policy validation.

    This graph is intentionally LLM-free. The production Foundry prompt agent is defined under
    ``foundry/prompt_agent.py`` and uses the same governed local tools.
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:  # pragma: no cover - optional integration dependency
        raise RuntimeError("Install the agent extra: pip install -e '.[agent]'") from exc

    def run_governed_agent(state: WorkflowState) -> WorkflowState:
        request = AgentRequest.model_validate(state["request"])
        response = LocalGovernedAgent().run(request)
        return {"response": response.model_dump()}

    graph = StateGraph(WorkflowState)
    graph.add_node("governed_contract", run_governed_agent)
    graph.add_edge(START, "governed_contract")
    graph.add_edge("governed_contract", END)
    return graph.compile()
