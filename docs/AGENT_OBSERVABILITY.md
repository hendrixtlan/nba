# Agent Observability

The v0.4 observability model treats agent, tool, model, decision, and business telemetry as separate but correlated signals.

## Correlation fields

Every local reference run returns:

- `request_id`
- `trace_id`
- `agent_version`
- `agent_policy_version`
- tool events and evidence IDs
- estimated local token usage

Authoritative production token/latency telemetry should come from Foundry traces rather than the local estimator.

## Production telemetry

Target flow:

```text
Foundry Agent / LangGraph
        |
        +--> server-side agent traces
        |
        +--> custom application spans
        |
        v
Application Insights / Azure Monitor
        |
        +--> latency / exceptions
        +--> model and tool calls
        +--> token usage / cost
        +--> retrieval/tool traces
        +--> conversation and trace IDs
```

The platform should connect Application Insights to the Foundry project and use server-side tracing first. Client-side OpenTelemetry instrumentation is added around custom application logic where additional spans are needed.

## Dashboard dimensions

Recommended dashboard views:

- request success and error rate;
- p50/p95 agent latency;
- tool-call rate by tool and outcome;
- policy-block rate;
- approval-proposal rate;
- tokens and estimated/actual cost per successful task;
- evaluation pass rate by agent version;
- NBA model version and policy version distribution;
- customer-decision endpoint latency and error rate.

Do not log secrets or unnecessary customer data into traces. Apply the organization's telemetry retention, access-control and data-classification requirements.
