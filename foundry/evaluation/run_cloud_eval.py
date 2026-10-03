from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEvaluatorGenerationJobSource,
    EvaluatorGenerationInputs,
    EvaluatorGenerationJob,
    TestingCriterionAzureAIEvaluator,
)
from azure.identity import DefaultAzureCredential
from openai.types.eval_create_params import DataSourceConfigCustom

ROOT = Path(__file__).resolve().parents[2]
AGENT_NAME = os.getenv("NBA_FOUNDRY_AGENT_NAME", "latam-nba-commercial-agent")
AGENT_VERSION = os.getenv("NBA_FOUNDRY_AGENT_VERSION", "1")


def main() -> None:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    client = project_client.get_openai_client()

    generation_job = EvaluatorGenerationJob(
        inputs=EvaluatorGenerationInputs(
            model=model_deployment,
            evaluator_name=f"nba-agent-quality-{uuid.uuid4().hex[:8]}",
            evaluator_display_name="NBA Agent Quality",
            sources=[AgentEvaluatorGenerationJobSource(agent_name=AGENT_NAME)],
        )
    )
    rubric = project_client.beta.evaluators.begin_create_generation_job(job=generation_job).result()

    dataset = project_client.datasets.upload_file(
        name="nba-agent-test-queries",
        version=os.getenv("NBA_EVAL_DATASET_VERSION", "1"),
        file_path=str(ROOT / "foundry" / "evaluation" / "test_queries.jsonl"),
    )

    criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="Agent Quality",
            evaluator_name=rubric.name,
            initialization_parameters={"deployment_name": model_deployment},
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_items}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="Coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_deployment},
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="Violence",
            evaluator_name="builtin.violence",
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        ),
    ]

    evaluation = client.evals.create(
        name="LATAM NBA Agent Evaluation",
        data_source_config=DataSourceConfigCustom(
            type="custom",
            item_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            include_sample_schema=True,
        ),
        testing_criteria=criteria,
    )
    run = client.evals.runs.create(
        eval_id=evaluation.id,
        name=f"nba-agent-eval-{uuid.uuid4().hex[:8]}",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {"type": "file_id", "id": dataset.id},
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {"type": "input_text", "text": "{{item.query}}"},
                    }
                ],
            },
            "target": {"type": "azure_ai_agent", "name": AGENT_NAME, "version": AGENT_VERSION},
        },
    )

    while True:
        current = client.evals.runs.retrieve(run_id=run.id, eval_id=evaluation.id)
        if current.status in {"completed", "failed"}:
            print(f"status={current.status}")
            print(f"report_url={getattr(current, 'report_url', None)}")
            break
        time.sleep(5)


if __name__ == "__main__":
    main()
