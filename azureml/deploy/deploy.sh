#!/usr/bin/env bash
set -euo pipefail

: "${MODEL_VERSION:?Set MODEL_VERSION to the registered model version}"

az ml online-endpoint create -f azureml/endpoints/endpoint.yml
az ml online-deployment create \
  -f azureml/endpoints/deployment.yml \
  --set model="azureml:latam-nba-propensity:${MODEL_VERSION}" \
  --all-traffic

az ml online-endpoint show -n latam-nba-propensity --query scoring_uri -o tsv
