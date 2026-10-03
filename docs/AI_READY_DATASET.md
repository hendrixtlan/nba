# AI-ready dataset contract

The Gold feature product is treated as a governed interface, not an ad-hoc table.

## Readiness gates

A snapshot is publishable to Azure ML only when all gates pass:

1. **Ownership** — named business and technical owners exist outside this sample repo.
2. **Contract** — required fields, types and valid ranges match `training_features.schema.json`.
3. **Temporal correctness** — features are available at or before `event_time`; no future leakage.
4. **Quality** — key completeness, label validity, range checks and duplicate checks pass.
5. **Lineage** — snapshot ID can be traced to Gold, Silver, Bronze and source ingestion runs.
6. **Classification** — sensitivity/PII classification is recorded before production onboarding.
7. **Access** — least-privilege identities are used; no shared storage secrets are embedded.
8. **Reproducibility** — immutable training snapshot ID is carried into the training run/model record.
9. **Monitoring** — training/serving schema skew and feature drift are observable.
10. **Retention** — snapshot retention is explicitly defined by governance policy.

## T1/T2/T3 note

The vacancy references an internal LATAM AI Office T1/T2/T3 rubric. This public portfolio
project does **not** invent that proprietary scoring model. `T1/T2/T3` mapping is therefore
an integration point to be completed using the organization's official rubric.
