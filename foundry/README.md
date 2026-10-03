# Microsoft Foundry + LangGraph integration

This directory contains the production generative orchestration surface. The authoritative commercial decision still lives in `nba.services.decision_engine` and its registered ML model/policy.

## Primary pattern

`prompt_agent.py` uses `langchain-azure-ai` `AgentServiceFactory.create_prompt_agent` to create a Foundry-managed agent that is also a LangGraph-compatible compiled graph. The agent receives only governed local tools.

Required environment variables:

```bash
export AZURE_AI_PROJECT_ENDPOINT='https://...'
export MODEL_DEPLOYMENT_NAME='...'
export NBA_FOUNDRY_AGENT_NAME='latam-nba-commercial-agent'
```

Install optional dependencies:

```bash
pip install -e '.[agent]'
python foundry/prompt_agent.py
```

## Evaluation

`evaluation/run_cloud_eval.py` creates an agent-specific rubric from the deployed agent, uploads the JSONL test set, adds built-in coherence and violence evaluators, and starts a Foundry evaluation run. It requires a real Foundry project and appropriate RBAC.

The repository also contains a deterministic offline quality gate (`make agent-eval`) that validates tool selection, policy compliance, grounding/evidence contracts, approval boundaries, and local budgets without an LLM.
