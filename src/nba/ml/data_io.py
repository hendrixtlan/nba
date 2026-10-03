from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_tabular_dataset(path: str | Path) -> pd.DataFrame:
    """Load a training dataset from a CSV/Parquet file or a mounted directory.

    Azure ML mounts OneLake ``uri_folder`` inputs as directories. Fabric publishes
    the curated training snapshot as Parquet, while the local development path
    uses CSV. This loader keeps the training entry point independent from either
    storage representation.
    """

    dataset_path = Path(path)
    if dataset_path.is_file():
        return _read_file(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Training dataset does not exist: {dataset_path}")

    parquet_files = sorted(dataset_path.rglob("*.parquet"))
    if parquet_files:
        return pd.concat((pd.read_parquet(p) for p in parquet_files), ignore_index=True)

    csv_files = sorted(dataset_path.rglob("*.csv"))
    if csv_files:
        return pd.concat((pd.read_csv(p) for p in csv_files), ignore_index=True)

    raise ValueError(f"No CSV or Parquet files found under {dataset_path}")


def _read_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported training dataset format: {path.suffix}")
