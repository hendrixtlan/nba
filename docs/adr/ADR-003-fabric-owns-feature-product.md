# ADR-003 — Fabric owns the governed feature product

**Status:** Accepted

## Decision

The canonical training feature product lives in Microsoft Fabric/OneLake. Azure ML
consumes a versioned snapshot through a OneLake datastore but does not redefine the
business feature contract.

## Rationale

This preserves one governed semantic/data lineage path, reduces feature-definition drift,
and keeps data quality/ownership with the platform responsible for enterprise data.
Azure ML remains responsible for experimentation, training, registry and serving.
