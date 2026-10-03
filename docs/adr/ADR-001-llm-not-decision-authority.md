# ADR-001 — LLM is not the commercial decision authority

## Status
Accepted.

## Context
The system includes an agentic interface but also makes economically consequential recommendations. Free-form LLM generation is not an appropriate source of authoritative propensity, eligibility or expected-utility values.

## Decision
The deterministic NBA service owns candidate eligibility, propensity retrieval, utility calculation, ranking and policy application. The agent may retrieve context, call approved tools, explain a returned decision and coordinate approved downstream workflow steps.

## Consequences
- model and policy versions are auditable;
- explanations can be grounded in decision artifacts;
- agent prompts cannot silently change commercial policy;
- tool authorization becomes a separate security boundary;
- conversational flexibility is retained without delegating numeric decision authority to an LLM.
