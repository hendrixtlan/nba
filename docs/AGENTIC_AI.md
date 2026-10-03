# Agentic AI Architecture — v0.4

## Purpose

The agent is a governed interaction and orchestration layer over the existing Next Best Action capability. It is deliberately **not** the commercial decision authority.

```text
Commercial User
      |
      v
Microsoft Foundry Agent Service
      |
LangGraph-compatible prompt agent
      |
      +-------------------------------+
      | governed local tools          |
      v                               v
NBA Decision API / Engine       Semantic Catalog
      |                               |
      v                               v
Azure ML registered model       Governed definitions
      |
      v
Fabric / OneLake feature product
```

## Tool boundary

Read-only tools:

- `get_next_best_action`
- `explain_decision`
- `compare_action_alternatives`
- `get_business_definition`

Approval-only tool:

- `create_action_proposal`

The approval tool does not call CRM, campaign, pricing, inventory, or order APIs. It only returns an approval-required proposal with `external_action_executed=false`.

## Why two orchestrators exist

`LocalGovernedAgent` is deterministic and contains no LLM. It is used in CI to prove policy/tool contracts independently of model variability.

`foundry/prompt_agent.py` is the production generative layer. It uses Microsoft Foundry Agent Service via `langchain-azure-ai`. `AgentServiceFactory.create_prompt_agent` supplies a LangGraph-compatible graph and attaches the same local governed tools.

This separation answers two different questions:

1. **Are our business rules, tool schemas and approval boundaries correct?** — deterministic CI.
2. **Does the LLM reliably choose tools, follow policy and communicate well?** — Foundry evaluation.

## Request lifecycle

```text
User message
   |
   v
Intent / reasoning in Foundry
   |
   +-- customer decision ------> get_next_best_action
   +-- explanation ------------> explain_decision
   +-- alternatives -----------> compare_action_alternatives
   +-- metric meaning ---------> get_business_definition
   +-- action request ---------> create_action_proposal -> HUMAN APPROVAL
   |
   v
Grounded response
```

## Security principles

- No customer-specific decision is generated from model memory alone.
- No tool exists that can override expected utility or eligibility.
- Policy/model versions are returned from the authoritative decision service.
- Prompt-injection requests to bypass policy are not valid authority.
- Write-side enterprise integrations are intentionally absent in v0.4.
- Static API keys are not required by the intended Foundry/Entra deployment pattern.
