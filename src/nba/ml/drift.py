from __future__ import annotations

import numpy as np
import pandas as pd


def population_stability_index(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy()
    cur = pd.to_numeric(current, errors="coerce").dropna().to_numpy()
    if len(ref) == 0 or len(cur) == 0:
        return 0.0
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    ref_hist, _ = np.histogram(ref, bins=edges)
    cur_hist, _ = np.histogram(cur, bins=edges)
    ref_pct = np.clip(ref_hist / ref_hist.sum(), 1e-6, None)
    cur_pct = np.clip(cur_hist / cur_hist.sum(), 1e-6, None)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def categorical_psi(reference: pd.Series, current: pd.Series) -> float:
    categories = sorted(set(reference.astype(str)) | set(current.astype(str)))
    ref = reference.astype(str).value_counts(normalize=True).reindex(categories, fill_value=0.0)
    cur = current.astype(str).value_counts(normalize=True).reindex(categories, fill_value=0.0)
    ref_v = np.clip(ref.to_numpy(), 1e-6, None)
    cur_v = np.clip(cur.to_numpy(), 1e-6, None)
    return float(np.sum((cur_v - ref_v) * np.log(cur_v / ref_v)))


def drift_status(psi: float) -> str:
    if psi < 0.10:
        return "stable"
    if psi < 0.25:
        return "watch"
    return "investigate"
