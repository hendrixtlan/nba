from __future__ import annotations

import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.entities import OneLakeArtifact, OneLakeDatastore
from azure.identity import DefaultAzureCredential


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a Fabric OneLake datastore in Azure ML")
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--workspace-name", required=True)
    parser.add_argument("--fabric-workspace-id", required=True)
    parser.add_argument("--lakehouse-item-id", required=True)
    parser.add_argument("--name", default="nba_onelake")
    parser.add_argument("--endpoint", default="onelake.dfs.fabric.microsoft.com")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = MLClient(
        DefaultAzureCredential(),
        args.subscription_id,
        args.resource_group,
        args.workspace_name,
    )
    datastore = OneLakeDatastore(
        name=args.name,
        description="Governed Fabric Lakehouse Files surface for LATAM NBA ML",
        one_lake_workspace_name=args.fabric_workspace_id,
        endpoint=args.endpoint,
        artifact=OneLakeArtifact(
            name=f"{args.lakehouse_item_id}/Files",
            type="lake_house",
        ),
    )
    result = client.datastores.create_or_update(datastore)
    print(f"registered_datastore={result.name}")


if __name__ == "__main__":
    main()
