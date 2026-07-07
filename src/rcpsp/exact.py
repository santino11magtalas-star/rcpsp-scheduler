# exact.py is the "honesty check" and a slow but CORRECT solver for SMALL projects.
# So we can see how close our fact methods get to the true best.
# How does it work?
# 1. Build an activity list one task at a time, only choosking tasks whose predecessors are already placed.
# 2. After each choice, schedule what we have so far, where in the partial length is a lower bound on the finish schedule.
# 3. The critical path length is a hard lower bound: if we ever match it, we can stop completely.
# Reference: Demeulemeester & Herrolen (1992), Branch and Bound for the RCPSP.
# NOTE: This explores oderings, so it's only practical on small instances, this is the BASELINE and not the MAIN solver.

from __future__ import annotations 
from .cpm import critical_path_method
from .sgs import serial_sgs

def branch_and_bound(project):
    lower_bound = critical_path_method(project).makespan
    acts = project.activities
    n = len(acts)
    best = {"ms": float("inf"), "order": None}
 
    def recurse(chosen, chosen_set):
        if best["ms"] == lower_bound:
            return   # can't possibly do better than the lower bound, stop
        if len(chosen) == n:
            ms = serial_sgs(project, order=chosen).makespan
            if ms < best["ms"]:
                best["ms"] = ms
                best["order"] = list(chosen)
            return
        eligible = sorted(     # tasks we're allowed to place next (all predecessors already placed)
            j for j in acts
            if j not in chosen_set
            and all(p in chosen_set for p in project.predecessors(j))
        )
        for j in eligible:
            chosen.append(j)
            chosen_set.add(j)
            # partial schedule length is a lower bound on the full one --
            # only keep going if it could still beat our best
            partial = serial_sgs(project, order=chosen).makespan
            if partial < best["ms"]:
                recurse(chosen, chosen_set)
            chosen.pop()
            chosen_set.discard(j)
    recurse([], set())
    return serial_sgs(project, order=best["order"]) 
