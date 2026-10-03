from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from nba.domain.models import CustomerContext

AgentIntent = Literal[
    "decision",
    "explanation",
    "comparison",
    "semantic_definition",
    "approval_request",
    "policy_violation",
    "unsupported",
]


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    customer: CustomerContext | None = None
    term: str | None = None


class ToolAuditEvent(BaseModel):
    tool_name: str
    status: Literal["success", "blocked", "error"]
    evidence_id: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)


class AgentUsage(BaseModel):
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_total_tokens: int = 0
    estimated_cost_usd: float | None = None
    tool_call_count: int = 0


class AgentResponse(BaseModel):
    request_id: str
    trace_id: str
    agent_version: str
    agent_policy_version: str
    intent: AgentIntent
    answer: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    tool_events: list[ToolAuditEvent] = Field(default_factory=list)
    usage: AgentUsage = Field(default_factory=AgentUsage)
    requires_human_approval: bool = False
