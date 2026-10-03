from __future__ import annotations

from fastapi import FastAPI

from nba.agent.tools import explain_decision
from nba.domain.models import CustomerContext, DecisionResponse, ExplainRequest
from nba.services.factory import build_engine

app = FastAPI(
    title="LATAM Next Best Action API",
    version="0.1.0",
    description="Governed decision service for commercial Next Best Action use cases.",
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
