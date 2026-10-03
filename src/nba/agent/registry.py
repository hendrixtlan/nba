from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from nba.agent.policy import authorize_tool, validate_tool_budget
from nba.agent.telemetry import stable_id


@dataclass
class ToolResult:
    tool_name: str
    evidence_id: str
    payload: dict[str, Any]
    access_mode: str


class GovernedToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., dict[str, Any]]] = {}
        self.call_count = 0

    def register(self, name: str, fn: Callable[..., dict[str, Any]]) -> None:
        self._tools[name] = fn

    def execute(self, name: str, **kwargs: Any) -> ToolResult:
        access_mode = authorize_tool(name)
        self.call_count += 1
        validate_tool_budget(self.call_count)
        if name not in self._tools:
            raise KeyError(f"Approved tool '{name}' has no runtime implementation")
        payload = self._tools[name](**kwargs)
        evidence_seed = f"{name}:{self.call_count}:{payload}"
        return ToolResult(
            tool_name=name,
            evidence_id=stable_id("ev", evidence_seed),
            payload=payload,
            access_mode=access_mode,
        )
