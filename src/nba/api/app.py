from __future__ import annotations

from fastapi import FastAPI

from nba.agent.contracts import AgentRequest, AgentResponse
from nba.agent.orchestrator import LocalGovernedAgent
from nba.agent.tools import explain_decision
from nba.domain.models import CustomerContext, DecisionResponse, ExplainRequest
from nba.services.factory import build_engine

app = FastAPI(
    title="LATAM Next Best Action API",
    version="0.4.0",
    description="Governed decision service and local agent-contract harness for commercial NBA use cases.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/next-best-action", response_model=DecisionResponse)
def next_best_action(customer: CustomerContext) -> DecisionResponse:
    return build_engine().decide(customer)


@app.post("/v1/explain")
def explain(request: ExplainRequest) -> dict:
    facts = explain_decision(request.decision)
    return {"style": request.style, "facts": facts}


@app.post("/v1/agent/run", response_model=AgentResponse)
def run_local_agent(request: AgentRequest) -> AgentResponse:
    """Deterministic local contract harness; production LLM orchestration lives in Foundry."""
    return LocalGovernedAgent().run(request)
