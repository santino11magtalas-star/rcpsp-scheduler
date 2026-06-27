# tests for the critical path method.
# the numbers below are worked out by hand on the sample_j6 network so we know exactly what cpm.py should produce. 

from pathlib import Path
from rcpsp import Activity, Project, critical_path_method, parse_sm
SAMPLE = Path(__file__).resolve().parents[1] / "data" / "psplib" / "sample_j6.sm"

# sample_j6 network (durations): 1=0, 2=4, 3=3, 4=2, 5=5, 6=0
# precedence: 1->2,3 ; 2->4 ; 3->4,5 ; 4->6 ; 5->6
# by hand:
#   ES/EF = 1:0/0  2:0/4  3:0/3  4:4/6  5:3/8  6:8/8  
#   slack = 1:0  2:2  3:0  4:2  5:0  6:0
#   critical path = 1 - 3 - 5 - 6

def test_makespan():
    p = parse_sm(SAMPLE)
    r = critical_path_method(p)
    assert r.makespan == 8

def test_earliest_times():
    r = critical_path_method(parse_sm(SAMPLE))
    assert r.es == {1: 0, 2: 0, 3: 0, 4: 4, 5: 3, 6: 8}
    assert r.ef == {1: 0, 2: 4, 3: 3, 4: 6, 5: 8, 6: 8}

def test_slack():
    r = critical_path_method(parse_sm(SAMPLE))
    assert r.slack == {1: 0, 2: 2, 3: 0, 4: 2, 5: 0, 6: 0}

def test_critical_path():   # everything on the path has zero slack
    r = critical_path_method(parse_sm(SAMPLE))
    assert r.critical_path() == [1, 3, 5, 6]
    assert all(r.is_critical(j) for j in r.critical_path())

def test_slack_never_negative():  # sanity: on a valid project no task can have negative slack
  r = critical_path_method(parse_sm(SAMPLE))
  assert all(s >= 0 for s in r.slack.values())

def test_simple_chain(): 
  acts = { 
    1: Activity(id=1, duration=0, successors=[2]),
    2: Activity(id=2, duration=5, successors=[3]),
    3: Activity(id=3, duration=3, successors=[]),
  }
  p = Project(activities=acts, capacities={"R1" : 1})
  r = critical_path_method(p)
  assert r.makespan == 8 
  assert r.critical_path() == [1,2,3]
  assert all(s == 0 for s in r.slack.values())

