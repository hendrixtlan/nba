# Agent Evaluation Strategy

Agent quality is evaluated at two levels.

## 1. Deterministic offline quality gate

Run:

```bash
make agent-eval
```

The test set in `evaluation/agent_cases.jsonl` verifies:

- intent routing;
- exact governed tool selection;
- policy compliance;
- evidence linkage between tool events and response evidence;
- human-approval boundaries;
- tool-call and estimated-token budgets.

Artifacts:

- `artifacts/agent_eval_metrics.json`
- `artifacts/agent_eval_results.jsonl`

Thresholds are versioned in `configs/agent_policy.yaml`.

This harness intentionally does not measure natural-language quality because it contains no LLM.

## 2. Microsoft Foundry cloud evaluation

`foundry/evaluation/run_cloud_eval.py` targets the actual deployed Foundry agent. The runner:

1. Generates an agent-specific rubric from the deployed agent configuration.
2. Uploads the curated JSONL evaluation set.
3. Uses the rubric as the primary agent-quality evaluator.
4. Adds built-in coherence and violence evaluators.
5. Executes a Foundry evaluation run against the deployed agent version.

The cloud run is the authoritative place to evaluate generative behavior, tool-use reasoning, communication quality, safety, and actual token usage.

## Recommended release gate

A production promotion should require all of the following:

```text
Offline policy/tool gate      PASS
Foundry agent rubric          PASS
Safety evaluators             PASS
Tool-call regression tests    PASS
Latency SLO                   PASS
Token/cost budget             PASS
```

Never use a single aggregate score to hide a failure in policy compliance or unsafe tool behavior. Those dimensions are hard release gates.
