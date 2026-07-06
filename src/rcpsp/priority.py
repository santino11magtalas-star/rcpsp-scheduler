# simulated annealing: the optimizer takes a schedule and keeps trying small tweaks to make it shorter.
# how it works:
# 1. a "solution" is an order to hand the scheduler.
# 2. a "tweak is a swap in two neighbouring tasks in the list. Ex: we never put a task before something it depends on.
# 3. we decode each order with the serial SGS and look at the makespan.
# 4. If a "tweak" makes it shorter, keep it but if it makes it longer we still keep it but depends on the situation. 
# 5. reference: Kirkpatrick et al. (1983); Bouleimen & Lecocq (2003).

from __future__ import annotations
import random
import math
from .priority import priority_order
from .sgs import serial_sgs

def makespan(project, order):
  return serial_sgs(project, order=order).makespan

def _neighbor(project, order, rng):
    # swap two adjacent tasks, but only if it stays legal.
    # swapping a,b is legal as long as a isn't a direct predecessor of b.
    order = list(order)
    n = len(order)
    for _ in range(10):   # a few tries to find a legal swap
        i = rng.randrange(n - 1)
        a, b = order[i], order[i + 1]
        if b not in project.activities[a].successors:
            order[i], order[i + 1] = b, a
            return order
    return order   # couldn't find one, leave it unchanged
 
 
def simulated_annealing(project, iterations=2000, t_start=2.0,
                        cooling=0.995, rule="lft", seed=None):
    rng = random.Random(seed)
    current = priority_order(project, rule)   # start from a good order
    current_ms = _makespan(project, current)
    best, best_ms = current, current_ms
    temp = t_start
    for _ in range(iterations):
        cand = _neighbor(project, current, rng)
        cand_ms = _makespan(project, cand)
        delta = cand_ms - current_ms
        # accept if better, or sometimes if worse (less often as temp drops)
        if delta <= 0 or rng.random() < math.exp(-delta / temp):
            current, current_ms = cand, cand_ms
            if current_ms < best_ms:
                best, best_ms = current, current_ms
        temp *= cooling
 
    return serial_sgs(project, order=best)
 
