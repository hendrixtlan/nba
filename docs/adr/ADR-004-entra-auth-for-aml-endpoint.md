# ADR-004 — Microsoft Entra authentication for managed ML inference

**Status:** Accepted

## Decision

Production inference uses an Azure ML managed online endpoint configured with
`auth_mode: aad_token`. The NBA API calls it with its managed identity and is granted
only the endpoint scoring permission required by the workload.

## Rationale

Static endpoint keys create long-lived secret-management and rotation obligations.
Identity-based invocation provides RBAC-scoped authorization and clearer auditability.
