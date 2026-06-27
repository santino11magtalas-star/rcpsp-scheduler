# Crititcal path method, which is done as DP over the topological order
# this is the longest-path-in-a DAG recurrence 
# References for this part: Skiena ch 19-24 (dynamic programming). 
# What to compute here:
# 1. ES = Earliest start, EF = Earliest finish 
# 2. LS = lastest start, LF = Lastest finish
# 3. Slack = LS - ES means on how much can a task slip
# * a task is "critical" if slack ==0. Which means the critical path is the chain of critical tasks from source to sink


from __future__ import annotations 
from dataclasses import dataclass

#dataclass
class CPMResult: 
  es: dict[int, int]
  ef: dict[int, int]
  ls: dict[int, int]
  lf: dict[int, int]
  slack: dict[int, int]
  makespan: int
  project: "object" = None # for path rebuilding

def is_critical(self, job):
  return self.slack[job] ==0

def critical_path(self):
  p = self.project
  node = p.source
  path = [node]
  while node != p.sink:
    nxt = None
    for s in p.activities[node]. successors:
      if self.slack[s] ==0 and self.ef[node] == self.es[s]:
        nxt = s
        break 
if nxt is None:
  break # means that it shouldn't happen on a valide DAG, but don't loop it forever
path.append(nxt)
node = nxt
return path 

def critical_path_method(project):
  order = project.topological_order()
  acts = project.activities 

#Forward pass: Earliest times 
# ES is the latest finish among predecessors, the process is in topological order so
# every predecessor is already done by the time we reach a task
es, ef = [], {}
for j in order:
  preds = project.predecessors(j)
  es[j] = max((ef[p] for p in preds), default=0)
  ef[j] = es[j] + acts [j].duration
makespan = max(ef.values())

#backward pass: lastest times
# this is inverse from the forward pass, which means a task with no successors can finish as late as the 
# project end. Otherwise LF =  earliest LS among its  successors.
ls, lf = {}, {}
for j in reversed(order):
  succ = acts[j].successors
  lf[j] = min((ls[s] for s in succ), default=makespan)
  ls[j] = lf[j] - acts[j].duration
slack = {j: ls[j] - es[j] for j in order}
return CPMResults(es=es, ef=ef, ls=ls, lf=lf, slack=slack, makespan=makespan, project=project)
