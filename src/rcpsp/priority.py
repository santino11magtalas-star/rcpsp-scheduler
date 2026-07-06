# Priority rules: decide what order to hand tasks to the scheduler.
# The serial SGS schedules tasks one at a time, a smarter order usally gives a smarter schedule.
# So here we build a priority list so that at each step we look at eh tasks whose predecessors are already placed ("eligible"), and pick
# the most urgent one by whatever rule we chose.

from __future__ import annotations
from .cpm import critical_path_method


def _key_func(project, cpm, rule):
    acts = project.activities
    if rule == "lft":
        return lambda j: (cpm.lf[j], j)
    if rule == "mslk":
        return lambda j: (cpm.slack[j], j)
    if rule == "grpw":
        def grpw(j):
            weight = acts[j].duration + sum(acts[s].duration
                                            for s in acts[j].successors)
            return (-weight, j)
        return grpw
    raise ValueError(f"unknown rule: {rule!r}")

def priority_order(project, rule="lft"):
    cpm = critical_path_method(project)
    key = _key_func(project, cpm, rule)
    chosen, chosen_set = [], set()
    remaining = set(project.activities)
    while remaining:
        eligible = [j for j in remaining
                    if all(p in chosen_set for p in project.predecessors(j))]
        nxt = min(eligible, key=key)
        chosen.append(nxt)
        chosen_set.add(nxt)
        remaining.remove(nxt)
    return chosen
