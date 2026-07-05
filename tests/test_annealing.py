# run tests for the simulated annealing optimizer
# to run: PYTHONPATH=src python -m pytest -q

from pathlib import Path 
from rcpsp import (critical_path_method, is_feasible, parse_sm, priority_order, serial_sgs, simulated_annealing)
sample = Path(__file__).resolve().parents[1]/"data"/"psplib"/"sample_j6.sm"

def test_result_is_feasible():
    p = parse_sm(SAMPLE)
    s = simulated_annealing(p, iterations=200, seed=1)
    assert is_feasible(p, s)
 
def test_never_worse_than_starting_order():
    # annealing starts from the priority-rule order and only keeps the best it
    # finds, so it can never come out worse than where it started.
    p = parse_sm(SAMPLE)
    start_ms = serial_sgs(p, order=priority_order(p, "lft")).makespan
    s = simulated_annealing(p, iterations=200, seed=1, rule="lft")
    assert s.makespan <= start_ms
  
def test_not_below_critical_path():
    # the critical path is a hard lower bound but nothing can beat it.
    p = parse_sm(SAMPLE)
    cpm = critical_path_method(p)
    s = simulated_annealing(p, iterations=200, seed=1)
    assert s.makespan >= cpm.makespan
  
def test_reproducible_with_seed():
    # same seed equals same answer (important for tests + fair benchmarks)
    p = parse_sm(SAMPLE)
    a = simulated_annealing(p, iterations=200, seed=42)
    b = simulated_annealing(p, iterations=200, seed=42)
    assert a.makespan == b.makespan
 
