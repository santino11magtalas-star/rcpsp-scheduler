# Serial schedule-generation scheme (SGS): builds an actual resource feasible 
# The "Schedule" is just the critical path, this is the real RCPSP scheduler. 
# The idea for this is to go through the tasks in some order (priority based order) for each task,
# That place it at the earliest time where the FF are true:
# 1. All it's predecessors are already finished
# 2. There's enough free resources 
# then also mark those resources as used and move on to the next task.
# The order matters, a smarter order gives a shorter schedule and will be choosing the ff:
# order is priority.py's job, then here we default to a topological order, which is always precedence -feasible. ref Kolish (1996), serial/parallel SGS.

def _fits(act, start, usage, caps):
    for t in range(start, start + act.duration):  # can this task run over [start, start+duration) without busting a resource?
        for r, need in act.requests.items():
            if usage[r].get(t, 0) + need > caps[r]:
                return False
    return True
 
def _place(act, start, usage):
    for t in range(start, start + act.duration):  # mark the task's resource use across the time steps it occupies
        for r, need in act.requests.items():
            usage[r][t] = usage[r].get(t, 0) + need
 
def serial_sgs(project, order=None):
    if order is None:
        order = project.topological_order()
    acts = project.activities
    caps = project.capacities
    usage = {r: {} for r in caps}   # usage[resource][time] = amount used
    starts = {}
 
    for j in order:
        act = acts[j]   # earliest we could start: right after every predecessor finishes
        preds = project.predecessors(j)
        est = max((starts[p] + acts[p].duration for p in preds), default=0)
        # push it later one step at a time until the resources actually fit
        # (NOTE: assumes each task's demand <= capacity, which holds in PSPLIB)
        t = est
        while not _fits(act, t, usage, caps):
            t += 1
        starts[j] = t
        _place(act, t, usage)
 
    return Schedule(project=project, starts=starts)
 
def is_feasible(project, schedule):
    # sanity check used by the tests: no precedence broken, no resource
    # ever over capacity.
    acts = project.activities
    starts = schedule.starts
    # precedence: every task must finish before its successors start
    for j, act in acts.items():
        for s in act.successors:
            if starts[j] + act.duration > starts[s]:
                return False
 
    # resources: rebuild the usage profile and check nothing exceeds capacity
    usage = {r: {} for r in project.capacities}
    for j, act in acts.items():
        _place(act, starts[j], usage)
    for r, cap in project.capacities.items():
        if any(used > cap for used in usage[r].values()):
            return False
    return True
 
