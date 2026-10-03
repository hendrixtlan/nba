import pandas as pd
from sklearn.linear_model import LogisticRegression

from nba.ml.uplift import TLearnerUpliftModel


def test_tlearner_returns_one_uplift_per_row():
    x = pd.DataFrame({"x": [0, 1, 2, 3, 4, 5, 6, 7]})
    treatment = pd.Series([0, 0, 0, 0, 1, 1, 1, 1])
    y = pd.Series([0, 0, 1, 1, 0, 1, 1, 1])
    model = TLearnerUpliftModel(LogisticRegression()).fit(x, treatment, y)
    uplift = model.predict_uplift(x)
    assert len(uplift) == len(x)
