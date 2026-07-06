# tests for the priority rule orderings.
# To run: PYTHONPATH=src python -m pytest -q

from pathlib import Path
from rcpsp import is_feasible, parse_sm, priority_order, serial_sgs
SAMPLE = Path(__file__).resolve().parents[1] / "data" / "psplib" / "sample_j6.sm"
RULES = ["lft", "mslk", "grpw"]

def test_order_has_every_task_once():
    # the order must include every task exactly once, nothing missing or doubled
    p = parse_sm(SAMPLE)
    for rule in RULES:
        order = priority_order(p, rule)
        assert sorted(order) == sorted(p.activities)

def test_order_respects_precedence():
    # a task must never come before one of its predecessors
    p = parse_sm(SAMPLE)
    for rule in RULES:
        order = priority_order(p, rule)
        pos = {j: i for i, j in enumerate(order)}
        for j, act in p.activities.items():
            for s in act.successors:
                assert pos[j] < pos[s]

def test_each_rule_gives_a_feasible_schedule():
    # every rule should produce an order the scheduler can turn into a
    # valid (feasible) schedule
    p = parse_sm(SAMPLE)
    for rule in RULES:
        order = priority_order(p, rule)
        s = serial_sgs(p, order=order)
        assert is_feasible(p, s)

def test_bad_rule_raises():
    # asking for a rule that doesn't exist should raise a clear error
    p = parse_sm(SAMPLE)
    try:
        priority_order(p, "not-a-rule")
        assert False, "should have raised"
    except ValueError:
        pass
