# experiments.py:
#   1. GROUND TRUTH  : how close do our methods get to the TRUE optimum?
#                      (our answer to "Christofides is within 1.5x optimal")
#   2. CONVERGENCE   : does annealing approach the optimum as we give it more
#                      time (iterations)?
#   3. COMPLEXITY    : does measured runtime match the theoretical growth?
# parts 1 and 2 use small instances where branch & bound gives the true
# optimum, so they are fully self-contained and reproducible.
# part 3 uses the real PSPLIB sets for the runtime-vs-size story.
# run:  PYTHONPATH=src python3 experiments.py

import csv
import glob
import math
import random
import time
from rcpsp import (Activity, Project, branch_and_bound, critical_path_method, parse_sm, priority_order, serial_sgs, simulated_annealing)

def make_small(seed, n_real=7, cap=4):
    """A small instance the exact solver can solve to optimality."""
    rng = random.Random(seed)
    n = n_real + 2
    succ = {j: [] for j in range(1, n + 1)}
    for j in range(2, n):
        t = sorted(rng.sample(range(j + 1, n + 1), min(rng.randint(1, 2), n - j)))
        succ[j] = t or [n]
    succ[1] = sorted(rng.sample(range(2, n), min(2, n - 2)))
    acts = {}
    for j in range(1, n + 1):
        if j == 1 or j == n:
            d, r = 0, {"R1": 0}
        else:
            d, r = rng.randint(1, 6), {"R1": rng.randint(1, cap)}
        acts[j] = Activity(id=j, duration=d, successors=succ[j], requests=r)
    return Project(activities=acts, capacities={"R1": cap})

def _random_order(p, rng):
    chosen, cs, rem = [], set(), set(p.activities)
    while rem:
        elig = [j for j in rem if all(q in cs for q in p.predecessors(j))]
        nxt = rng.choice(elig)
        chosen.append(nxt); cs.add(nxt); rem.discard(nxt)
    return chosen

def _swap(p, order, rng):
    order = list(order); n = len(order)
    for _ in range(10):
        i = rng.randrange(n - 1); a, b = order[i], order[i + 1]
        if b not in p.activities[a].successors:
            order[i], order[i + 1] = b, a
            return order
    return order

def _anneal_from_random(p, iterations, seed):
    """Annealing started from a RANDOM order, so we can watch it converge."""
    rng = random.Random(seed)
    cur = _random_order(p, rng); cur_ms = serial_sgs(p, order=cur).makespan
    best = cur_ms; temp = 2.0
    for _ in range(iterations):
        cand = _swap(p, cur, rng); cms = serial_sgs(p, order=cand).makespan
        d = cms - cur_ms
        if d <= 0 or rng.random() < math.exp(-d / temp):
            cur, cur_ms = cand, cms
            best = min(best, cur_ms)
        temp *= 0.99
    return best
  
def gap(ms, base):
    return (ms - base) / base * 100 if base else 0.0

# 1. GROUND TRUTH
def experiment_optimal(n=40):
    print("\n=== 1. GROUND TRUTH: gap above the TRUE optimum ===")
    print("(small instances solved exactly by branch & bound)\n")
    tot = {"lft": 0.0, "ann": 0.0}; hit = {"lft": 0, "ann": 0}; rows = []
    for i in range(n):
        p = make_small(i)
        opt = branch_and_bound(p).makespan
        lft = serial_sgs(p, order=priority_order(p, "lft")).makespan
        ann = simulated_annealing(p, iterations=1000, seed=1).makespan
        tot["lft"] += gap(lft, opt); tot["ann"] += gap(ann, opt)
        hit["lft"] += (lft == opt); hit["ann"] += (ann == opt)
        rows.append([i, opt, lft, ann])
    print(f"instances: {n}")
    print(f"  priority-LFT : {tot['lft']/n:4.1f}% above optimum | "
          f"matches optimum {100*hit['lft']//n}% of the time  "
          f"(within {1+tot['lft']/n/100:.2f}x)")
    print(f"  annealing    : {tot['ann']/n:4.1f}% above optimum | "
          f"matches optimum {100*hit['ann']//n}% of the time  "
          f"(within {1+tot['ann']/n/100:.2f}x)")
    with open("exp_optimal.csv", "w", newline="") as f:
        csv.writer(f).writerows([["instance", "optimum", "lft", "annealing"]] + rows)

# 2. CONVERGENCE
def experiment_convergence(n=40):
    print("\n=== 2. CONVERGENCE: approaching the optimum with more time ===")
    print("(annealing from a random start; avg gap above the true optimum)\n")
    insts = [make_small(i) for i in range(n)]
    opts = [branch_and_bound(p).makespan for p in insts]
    budgets = [1, 5, 10, 25, 50, 100, 250, 500]
    rows = []
    print(f"{'iterations':>12}{'avg % above optimum':>22}")
    print("-" * 34)
    for it in budgets:
        tot = sum(gap(_anneal_from_random(p, it, 1), opt)
                  for p, opt in zip(insts, opts))
        avg = tot / n
        print(f"{it:>12}{avg:>21.1f}%")
        rows.append([it, round(avg, 2)])
    with open("exp_convergence.csv", "w", newline="") as f:
        csv.writer(f).writerows([["iterations", "avg_gap_above_optimum"]] + rows)

# 3. COMPLEXITY
def experiment_complexity(sample=20):
    print("\n=== 3. COMPLEXITY: measured runtime vs instance size ===")
    print("(SGS theory ~ O(n * horizon); does runtime scale with size?)\n")
    rows = []
    print(f"{'set':>6}{'tasks':>8}{'SGS (ms)':>12}{'annealing (ms)':>17}")
    print("-" * 43)
    for s in ["j30", "j60", "j120"]:
        files = sorted(glob.glob(f"data/psplib/{s}/*.sm"))[:sample]
        if not files:
            print(f"  ({s}: no files found)")
            continue
        nt = 0; sgs_t = 0.0; ann_t = 0.0; cnt = 0
        for fp in files:
            try:
                p = parse_sm(fp)
            except Exception:
                continue
            nt = len(p); order = priority_order(p, "lft")
            t0 = time.perf_counter(); serial_sgs(p, order=order)
            sgs_t += (time.perf_counter() - t0) * 1000
            t0 = time.perf_counter(); simulated_annealing(p, iterations=500, seed=1)
            ann_t += (time.perf_counter() - t0) * 1000
            cnt += 1
        print(f"{s:>6}{nt:>8}{sgs_t/cnt:>12.3f}{ann_t/cnt:>17.1f}")
        rows.append([s, nt, round(sgs_t/cnt, 3), round(ann_t/cnt, 1)])
    with open("exp_complexity.csv", "w", newline="") as f:
        csv.writer(f).writerows(
            [["set", "tasks", "avg_sgs_ms", "avg_annealing_ms"]] + rows)
      
if __name__ == "__main__":
    experiment_optimal()
    experiment_convergence()
    experiment_complexity()
    print("\nsaved: exp_optimal.csv, exp_convergence.csv, exp_complexity.csv")
