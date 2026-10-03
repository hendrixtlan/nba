from __future__ import annotations

import pandas as pd

from nba.ml.data_io import load_tabular_dataset


def test_load_tabular_dataset_from_csv_directory(tmp_path):
    pd.DataFrame({"x": [1, 2]}).to_csv(tmp_path / "a.csv", index=False)
    pd.DataFrame({"x": [3]}).to_csv(tmp_path / "b.csv", index=False)
    result = load_tabular_dataset(tmp_path)
    assert result["x"].tolist() == [1, 2, 3]
