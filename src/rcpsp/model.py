# core data model for the scheduler.
# a Project is a DAG of activities + resource capacities. job 1 is the
# supersource and job n is the sink (both duration 0) -- PSPLIB convention.
# refs: Skiena ch 9-10 (graphs/traversal), 11-12 (weighted graphs).

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class CycleError(ValueError):
    """raised if the precedence graph isn't actually a DAG."""


@dataclass
class Activity:
    id: int
    duration: int
    successors: list[int] = field(default_factory=list)
    requests: dict[str, int] = field(default_factory=dict)  # resource -> amount


@dataclass
class Project:
    activities: dict[int, Activity]
    capacities: dict[str, int]
    horizon: int = 0

    def __len__(self):
        return len(self.activities)

    @property
    def resource_names(self):
        return list(self.capacities.keys())

    @property
    def source(self):
        return min(self.activities)

    @property
    def sink(self):
        return max(self.activities)

    def predecessors(self, job):
        # no reverse index yet, just scan. fine for J30/J60.
        # TODO: build a preds map if J120 feels slow
        return [a.id for a in self.activities.values() if job in a.successors]

    def topological_order(self):
        # Kahn's algorithm. we sort the ready set so the output is
        # deterministic -- makes the tests way easier to write.
        indeg = {jid: 0 for jid in self.activities}
        for act in self.activities.values():
            for s in act.successors:
                indeg[s] += 1

        ready = deque(sorted(j for j, d in indeg.items() if d == 0))
        order = []
        while ready:
            j = ready.popleft()
            order.append(j)
            for s in self.activities[j].successors:
                indeg[s] -= 1
                if indeg[s] == 0:
                    ready.append(s)

        if len(order) != len(self.activities):
            raise CycleError("cycle in precedence graph (not a DAG)")
        return order

    def validate_acyclic(self):
        self.topological_order()  # raises CycleError if there's a cycle


@dataclass
class Schedule:
    # a solution = start time per job. resource feasibility gets checked
    # later (phase 2), here we just hold the structure + makespan.
    project: Project
    starts: dict[int, int]

    def finish(self, job):
        return self.starts[job] + self.project.activities[job].duration

    @property
    def makespan(self):
        return max(self.finish(j) for j in self.starts)
