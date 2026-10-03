from __future__ import annotations

import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from langchain_azure_ai.agents import AgentServiceFactory

from nba.agent import tools as governed_tools

ROOT = Path(__file__).resolve().parents[1]


def build_foundry_agent():
    """Create a Foundry-managed prompt agent exposed as a LangGraph-compatible graph."""
    instructions = (ROOT / "foundry" / "system_prompt.md").read_text(encoding="utf-8")
    factory = AgentServiceFactory(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME") or os.environ[
        "AZURE_AI_MODEL_DEPLOYMENT_NAME"
    ]

    def get_next_best_action(customer: dict) -> dict:
        """Return the policy-compliant commercial Next Best Action for a customer context."""
        return governed_tools.get_next_best_action(customer)

    def explain_decision(decision: dict) -> dict:
        """Return evidence-backed facts explaining an authoritative NBA decision."""
        return governed_tools.explain_decision(decision)

    def compare_action_alternatives(decision: dict) -> dict:
        """Compare eligible and excluded actions from an authoritative NBA decision."""
        return governed_tools.compare_action_alternatives(decision)

    def get_business_definition(term: str) -> dict:
        """Return a governed business definition from the semantic catalog."""
        return governed_tools.get_business_definition(term)

    def create_action_proposal(customer: dict, reason: str) -> dict:
        """Create a human-approval proposal for the governed NBA; execute nothing externally."""
        return governed_tools.create_action_proposal(customer, reason)

    agent = factory.create_prompt_agent(
        name=os.getenv("NBA_FOUNDRY_AGENT_NAME", "latam-nba-commercial-agent"),
        model=model_deployment,
        instructions=instructions,
        tools=[
            get_next_best_action,
            explain_decision,
            compare_action_alternatives,
            get_business_definition,
            create_action_proposal,
        ],
    )
    return agent


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    agent = build_foundry_agent()
    response = agent.invoke(
        {"messages": [HumanMessage(content="Define expected utility using the governed catalog.")]}
    )
    print(response)
