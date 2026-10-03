import pandas as pd

from nba.ml.drift import drift_status, population_stability_index


def test_psi_detects_large_shift():
    reference = pd.Series(range(1, 101))
    current = pd.Series(range(201, 301))
    psi = population_stability_index(reference, current)
    assert psi >= 0.25
    assert drift_status(psi) == "investigate"
