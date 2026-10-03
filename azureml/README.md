# Azure Machine Learning production surface

This folder turns the local propensity pipeline into a managed Azure ML workflow while
keeping the authoritative commercial decision logic in `src/nba/services`.

## Integration pattern

```text
Fabric Gold Delta table
        |
        v
OneLake Files immutable training snapshot
        |
        v
Azure ML OneLake datastore (identity based)
        |
        v
Command training job
        |
        v
Named custom-model output
        |
        v
Registered model asset
        |
        v
Managed online endpoint (aad_token)
        |
        v
NBA FastAPI adapter
```

## Bootstrap order

1. Create/configure the Azure ML workspace and compute.
2. Create compute: `az ml compute create -f azureml/compute/cpu-cluster.yml`.
3. Register OneLake as a datastore:
   `python azureml/setup/register_onelake_datastore.py ...`
4. Create the training environment:
   `az ml environment create -f azureml/environments/training.yml`
5. Submit the command job:
   `az ml job create -f azureml/jobs/train.yml --stream`
6. Register the named job output:
   `python azureml/deploy/register_model.py --job-name <job>`
7. Create the `aad_token` managed online endpoint and deployment.
8. Grant the NBA API managed identity endpoint `score/action` permission.
9. Set `NBA_AZUREML_SCORING_URI` in the API runtime.

No account key or endpoint key is required in the production path.
