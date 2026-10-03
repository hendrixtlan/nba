from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from nba.services.config import ROOT


class AgentPolicyError(PermissionError):
    pass


@lru_cache
def load_agent_policy() -> dict:
    path = Path(ROOT) / "configs" / "agent_policy.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def authorize_tool(tool_name: str) -> str:
    policy = load_agent_policy()
    if tool_name in policy["read_only_tools"]:
        return "read"
    if tool_name in policy["approval_tools"]:
        return "approval"
    raise AgentPolicyError(f"Tool '{tool_name}' is not approved by agent policy")


def validate_tool_budget(tool_call_count: int) -> None:
    maximum = int(load_agent_policy()["budgets"]["max_tool_calls_per_run"])
    if tool_call_count > maximum:
        raise AgentPolicyError(f"Tool-call budget exceeded: {tool_call_count} > {maximum}")
