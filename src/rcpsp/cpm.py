# Crititcal path method, which is done as DP over the topological order
# this is the longest-path-in-a DAG recurrence 
# References for this part: Skiena ch 19-24 (dynamic programming). 

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CPMResult:
    es: dict[int, int]
    ef: dict[int, int]
    ls: dict[int, int]
    lf: dict[int, int]
    slack: dict[int, int]
    makespan: int
    project: "object" = None

    def is_critical(self, job):
        return self.slack[job] == 0

    def critical_path(self):
        p = self.project
        node = p.source
        path = [node]
        while node != p.sink:
            nxt = None
            for s in p.activities[node].successors:
                if self.slack[s] == 0 and self.ef[node] == self.es[s]:
                    nxt = s
                    break
            if nxt is None:
                break
            path.append(nxt)
            node = nxt
        return path

def critical_path_method(project):
    order = project.topological_order()
    acts = project.activities
    es, ef = {}, {}
    for j in order:
        preds = project.predecessors(j)
        es[j] = max((ef[p] for p in preds), default=0)
        ef[j] = es[j] + acts[j].duration

    makespan = max(ef.values())
  
    ls, lf = {}, {}
    for j in reversed(order):
        succ = acts[j].successors
        lf[j] = min((ls[s] for s in succ), default=makespan)
        ls[j] = lf[j] - acts[j].duration
    slack = {j: ls[j] - es[j] for j in order}
    return CPMResult(es=es, ef=ef, ls=ls, lf=lf, slack=slack, makespan=makespan, project=project)
  
