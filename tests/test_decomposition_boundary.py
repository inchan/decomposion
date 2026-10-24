"""Checks fixed hypotheses and catches accidental metric changes."""
from experiments.decomposition_boundary import CASES, makespan, run


def test_fixed_scope():
    assert all(sum(a) == sum(b) == 120 for a, b in CASES.values())
    assert len(run()) == 12


def test_balanced_split_can_hurt():
    rows = [r for r in run() if r["case"] == "balanced"]
    assert rows[0]["winner"] == "tie"
    assert all(r["winner"] == "coarse" for r in rows[1:])


def test_skewed_split_has_a_crossover():
    rows = [r for r in run() if r["case"] == "skewed"]
    assert rows[0]["winner"] == "fine"
    assert rows[-1]["winner"] == "tie"


def test_unsplittable_bottleneck():
    rows = [r for r in run() if r["case"] == "unsplittable"]
    assert rows[0]["winner"] == "tie"
    assert rows[-1]["winner"] == "coarse"


def test_exact_assignment():
    assert makespan((80, 20, 10, 10)) == 80
    assert makespan((40, 40, 20, 10, 10)) == 60
