# Tests for the exact branch & bound solver.
# Run: PYTHONPATH=src python3 -m pytest -q
from pathlib import Path
from rcpsp import (Activity, Project, branch_and_bound, critical_path_method, is_feasible, parse_sm, serial_sgs)
SAMPLE = Path(__file__).resolve().parents[1]/"data"/"psplib"/"sample_j6.sm"

def test_result_is_feasible():
    p = parse_sm(SAMPLE)
    s = branch_and_bound(p)
    assert is_feasible(p, s)
  
def test_optimal_on_sample():
    p = parse_sm(SAMPLE)
    assert branch_and_bound(p).makespan == 8
    # sample_j6 has enough capacity that the optimum equals the critical-path
    # length (8) is the exact solver must find exactly that.
 
def test_exact_beats_or_ties_heuristic():   # the exact optimum can never be worse than any heuristic schedule
    p = parse_sm(SAMPLE)
    heur = serial_sgs(p).makespan
    assert branch_and_bound(p).makespan <= heur
 
def test_resource_conflict_optimum():
    acts = {
        1: Activity(id=1, duration=0, successors=[2, 3]),
        2: Activity(id=2, duration=3, successors=[4], requests={"R1": 1}),
        3: Activity(id=3, duration=3, successors=[4], requests={"R1": 1}),
        4: Activity(id=4, duration=0, successors=[]),
    }
    p = Project(activities=acts, capacities={"R1": 1})
    s = branch_and_bound(p)
    assert is_feasible(p, s)
    assert s.makespan == 6
    # two tasks each needing the whole resource must run back-to-back:
    # the true optimum is 6, and the exact solver should prove it.
