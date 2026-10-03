# ADR-005 — The agent is not external write authority

## Status
Accepted.

## Decision

The v0.4 commercial agent may read governed decision/semantic services and may create an approval-required action proposal. It may not directly execute CRM, campaign, pricing, inventory, order, or customer-contact actions.

## Rationale

Agentic orchestration introduces probabilistic tool selection. Keeping external writes behind an explicit approval boundary limits blast radius while evaluation evidence is accumulated. It also preserves a clean distinction between recommendation authority and transaction authority.

## Consequence

Future write tools require a separate ADR covering authorization, idempotency, approval policy, audit logging, retry semantics and compensating actions before they can be exposed to the agent.
