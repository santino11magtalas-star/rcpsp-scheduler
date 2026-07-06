# run_psplib.py and the benchmark runner and this is where our RESULTS come from.
# for every project in the PSPLIB sets (j30 / j60 / j120) it:
#   1. reads the project
#   2. computes the critical-path lower bound (shortest possible length, if we
#      had unlimited resources)
#   3. schedules it with each method (the priority rules + simulated annealing)
#   4. measures how far ABOVE that lower bound each method landed
# then it averages that gap per method per set and writes results.csv.
# usage:
#   PYTHONPATH=src python3 run_psplib.py           # quick: first 20 per set
#   PYTHONPATH=src python3 run_psplib.py --full     # every project (slower)

import csv
import sys
from pathlib import Path
from rcpsp import (critical_path_method, parse_sm, priority_order, serial_sgs, simulated_annealing)

SETS = ["j30", "j60", "j120"]
METHODS = ["priority-lft", "priority-mslk", "priority-grpw", "annealing"]
DATA = Path(__file__).parent / "data" / "psplib"

def _deviation(makespan, lower_bound):
    if lower_bound == 0:
        return 0.0
    return (makespan - lower_bound) / lower_bound * 100

def _run_one(project):
    lb = critical_path_method(project).makespan
    out = {}
    for rule in ["lft", "mslk", "grpw"]:
        ms = serial_sgs(project, order=priority_order(project, rule)).makespan
        out[f"priority-{rule}"] = _deviation(ms, lb)
    ms = simulated_annealing(project, iterations=500, seed=1).makespan
    out["annealing"] = _deviation(ms, lb)
    return out

def _run_set(folder, limit):
    files = sorted(folder.glob("*.sm"))
    if limit:
        files = files[:limit]
    totals, count = {m: 0.0 for m in METHODS}, 0
    for f in files:
        try:
            project = parse_sm(f)
        except Exception as e:      # noqa: BLE001 = just skip a bad file
            print(f"  skipped {f.name}: {e}")
            continue
        for method, dev in _run_one(project).items():
            totals[method] += dev
        count += 1
    if count == 0:
        return None, 0
    return {m: totals[m] / count for m in METHODS}, count

def main():
    full = "--full" in sys.argv
    limit = None if full else 20
    print(f"\nrunning {'ALL' if full else 'first 20'} projects per set "
          "(this can take a bit)...\n")
    per_set = {}
    for s in SETS:
        folder = DATA / s
        if not folder.exists():
            print(f"(missing folder, skipping: {folder})")
            continue
        avg, n = _run_set(folder, limit)
        if avg is None:
            print(f"(no .sm files in {folder})")
            continue
        per_set[s] = avg
        print(f"  {s}: {n} projects done")
    # print the results table (avg % above lower bound) 
    print("\nRESULTS -- average % above the critical-path lower bound "
          "(lower = better)\n")
    header = f"{'method':<16}" + "".join(f"{s:>9}" for s in SETS)
    print(header)
    print("-" * len(header))
    print(f"{'lower bound':<16}" + "".join(f"{'0.0%':>9}" for _ in SETS))
    for m in METHODS:
        line = f"{m:<16}"
        for s in SETS:
            v = per_set.get(s, {}).get(m)
            line += f"{v:>8.1f}%" if v is not None else f"{'-':>9}"
        print(line)
    # write results.csv
    out = Path(__file__).parent / "results.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["method"] + SETS)
        w.writerow(["lower_bound"] + [0.0 for _ in SETS])
        for m in METHODS:
            w.writerow([m] + [per_set.get(s, {}).get(m) for s in SETS])
    print(f"\nsaved {out}")
if __name__ == "__main__":
    main()
