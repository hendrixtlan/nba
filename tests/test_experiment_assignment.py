from nba.experimentation.assignment import assign_variant


def test_assignment_is_sticky():
    first = assign_variant("discount-2026q4", "C00001")
    second = assign_variant("discount-2026q4", "C00001")
    assert first == second


def test_assignment_changes_by_experiment():
    a = assign_variant("exp-a", "C00001")
    b = assign_variant("exp-b", "C00001")
    assert (a.bucket, a.experiment_id) != (b.bucket, b.experiment_id)
