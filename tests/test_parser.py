# tests for the parser + graph model.  run: PYTHONPATH=src python -m pytest -q
from pathlib import Path

import pytest

from rcpsp import CycleError, Project, parse_sm
from rcpsp.model import Activity

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "psplib" / "sample_j6.sm"


def test_job_count():
    p = parse_sm(SAMPLE)
    assert len(p) == 6
    assert p.source == 1 and p.sink == 6


def test_durations_and_requests():
    p = parse_sm(SAMPLE)
    assert p.activities[2].duration == 4
    assert p.activities[2].requests == {"R1": 3}
    assert p.activities[5].duration == 5
    # source + sink are dummies
    assert p.activities[1].duration == 0
    assert p.activities[6].duration == 0


def test_precedence():
    p = parse_sm(SAMPLE)
    assert p.activities[1].successors == [2, 3]
    assert p.activities[3].successors == [4, 5]
    assert p.activities[6].successors == []
    assert p.predecessors(4) == [2, 3]


def test_capacity():
    p = parse_sm(SAMPLE)
    assert p.capacities == {"R1": 5}


def test_topo_order_respects_precedence():
    p = parse_sm(SAMPLE)
    order = p.topological_order()
    pos = {j: i for i, j in enumerate(order)}
    for a in p.activities.values():
        for s in a.successors:
            assert pos[a.id] < pos[s]


def test_cycle_raises():
    # tiny 2-node loop -> should blow up
    a = Activity(id=1, duration=1, successors=[2])
    b = Activity(id=2, duration=1, successors=[1])
    p = Project(activities={1: a, 2: b}, capacities={"R1": 1})
    with pytest.raises(CycleError):
        p.validate_acyclic()
