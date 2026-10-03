import pandas as pd

from nba.ml.evaluation import temporal_split


def test_temporal_split_has_no_time_overlap():
    df = pd.DataFrame({"event_timestamp": pd.date_range("2026-01-01", periods=100, freq="D"), "x": range(100)})
    split = temporal_split(df)
    assert pd.to_datetime(split.train.event_timestamp).max() < pd.to_datetime(split.validation.event_timestamp).min()
    assert pd.to_datetime(split.validation.event_timestamp).max() < pd.to_datetime(split.test.event_timestamp).min()
    assert len(split.train) + len(split.validation) + len(split.test) == 100
