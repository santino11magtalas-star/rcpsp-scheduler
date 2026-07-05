# tests for the serial schedule-generation scheme (the resource scheduler).
# run: PYTHONPATH=src python -m pytest -q

from pathlib import Path
from rcpsp import (Activity, Project, critical_path_method, is_feasible,
                   parse_sm, serial_sgs)
SAMPLE = Path(__file__).resolve().parents[1] / "data" / "psplib" / "sample_j6.sm"

def test_schedule_is_feasible():
    p = parse_sm(SAMPLE)
    s = serial_sgs(p)
    assert is_feasible(p, s)
  
def test_makespan_on_sample():
    p = parse_sm(SAMPLE)
    s = serial_sgs(p)
    assert s.makespan == 8
    # capacity (R1=5) is enough that resources don't force a delay here,
    # so the resource schedule matches the critical-path length: 8.

def test_never_shorter_than_critical_path():
    p = parse_sm(SAMPLE)
    cpm = critical_path_method(p)
    s = serial_sgs(p)
    assert s.makespan >= cpm.makespan
 # resources can only push things later, never earlier, so the SGS
    # makespan must be >= the critical-path makespan.


def test_resource_conflict_forces_delay():
    acts = {
        1: Activity(id=1, duration=0, successors=[2, 3]),
        2: Activity(id=2, duration=3, successors=[4], requests={"R1": 1}),
        3: Activity(id=3, duration=3, successors=[4], requests={"R1": 1}),
        4: Activity(id=4, duration=0, successors=[]),
    }
    p = Project(activities=acts, capacities={"R1": 1})
    s = serial_sgs(p)
    assert is_feasible(p, s)
    assert s.makespan == 6
    # two tasks that each need the ENTIRE resource can't run at the same time,
    # so they're forced to run back-to-back.  without the resource limit they'd
    # overlap and finish at 3; with it, they finish at 6.
