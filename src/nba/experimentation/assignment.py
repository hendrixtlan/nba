from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentAssignment:
    experiment_id: str
    subject_id: str
    variant: str
    bucket: int


def assign_variant(
    experiment_id: str,
    subject_id: str,
    treatment_share: float = 0.5,
    salt: str = "nba-experiment-v1",
) -> ExperimentAssignment:
    """Deterministic assignment suitable for sticky randomized experiments."""
    if not 0 < treatment_share < 1:
        raise ValueError("treatment_share must be between 0 and 1")
    key = f"{salt}:{experiment_id}:{subject_id}".encode()
    bucket = int(hashlib.sha256(key).hexdigest()[:8], 16) % 10_000
    threshold = int(treatment_share * 10_000)
    variant = "treatment" if bucket < threshold else "control"
    return ExperimentAssignment(experiment_id, subject_id, variant, bucket)
