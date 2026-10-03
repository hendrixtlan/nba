from __future__ import annotations

import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a trained NBA model output")
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--workspace-name", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--model-name", default="latam-nba-propensity")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = MLClient(
        DefaultAzureCredential(),
        args.subscription_id,
        args.resource_group,
        args.workspace_name,
    )
    model = Model(
        name=args.model_name,
        path=f"azureml://jobs/{args.job_name}/outputs/model_output",
        type=AssetTypes.CUSTOM_MODEL,
        description="Calibrated propensity model plus manifest and evaluation artifacts",
        tags={"capability": "next-best-action", "decision_authority": "propensity_only"},
    )
    registered = client.models.create_or_update(model)
    print(f"registered_model={registered.name}:{registered.version}")


if __name__ == "__main__":
    main()
