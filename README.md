# RCPSP Scheduler

**DSA 2026 Final Project — Project Management Algorithms**
Learning Team 5 (LT5)

A scheduler for the **Resource-Constrained Project Scheduling Problem (RCPSP)**,
built from polynomial critical-path analysis up to priority-rule heuristics and a
simulated-annealing metaheuristic, with an exact branch-and-bound solver for
ground truth. Everything is benchmarked on the standard PSPLIB instance library
(1,559 projects across J30, J60, and J120).

This repository is the *code* half of the project. The accompanying theory paper
proves that RCPSP is NP-hard (via a reduction from PARTITION) and explains the
methods below.

---

## What this project does

Given a project of tasks with durations, precedence (task A must finish before
task B), and limited renewable resources, we find a schedule that finishes as
early as possible (minimizes the *makespan*). Adding the resource limit makes the
problem NP-hard, so we solve it with heuristics and measure how close they get to
the true optimum.

---

## Layout

```
src/rcpsp/
  model.py      Activity, Project (DAG + topological sort), Schedule
  parser.py     PSPLIB .sm loader
  cpm.py        critical path method (forward/backward pass, slack)
  sgs.py        serial schedule generation scheme + feasibility check
  priority.py   priority rules (LFT, min-slack, GRPW)
  annealing.py  simulated annealing metaheuristic
  exact.py      exact branch-and-bound solver (small instances)

run_psplib.py   benchmark runner -> results.csv
experiments.py  the three studies: ground truth, convergence, complexity
demo.py         loads a sample instance and prints its structure
visual.py       draws the DAG / Gantt figures

data/psplib/    PSPLIB instances (J30, J60, J120) + a small sample
tests/          28 unit tests
```

---

## Setup

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

---

## Quick start

Run everything with `PYTHONPATH=src` so Python finds the package.

```bash
# 1. sanity check: load a sample project and print it
PYTHONPATH=src python3 demo.py

# 2. run the full test suite (28 tests)
PYTHONPATH=src python3 -m pytest -q

# 3. run the benchmark (quick: first 20 projects per set)
PYTHONPATH=src python3 run_psplib.py

# 3b. run the FULL benchmark (all 1,559 projects, slower)
PYTHONPATH=src python3 run_psplib.py --full

# 4. run the three experiment studies
PYTHONPATH=src python3 experiments.py
```

---

## The methods

| Method | File | What it does |
| :--- | :--- | :--- |
| Critical path (CPM) | `cpm.py` | Computes the lower bound in O(V+E) via a forward/backward DP pass. |
| Serial scheduler (SGS) | `sgs.py` | Turns any task order into a feasible schedule, placing each task at its earliest legal, resource-free slot. |
| Priority rules | `priority.py` | Three cheap ways to order tasks: LFT (latest finish time), min-slack, GRPW. |
| Simulated annealing | `annealing.py` | Searches task orders, accepting occasional worse moves to escape local optima. Our best method. |
| Exact branch & bound | `exact.py` | Finds the true optimum on small instances; used to measure how good the heuristics are. |

Every schedule is independently re-checked for precedence and resource
feasibility before it is reported.

---

## Results

On the complete PSPLIB benchmark (1,559 projects, 4 resources each), average
percentage above the critical-path lower bound (lower is better):

| Method | J30 | J60 | J120 |
| :--- | :--- | :--- | :--- |
| Priority – LFT | 131.2% | 188.5% | 310.9% |
| Priority – min-slack | 133.9% | 191.4% | 317.1% |
| Priority – GRPW | 134.5% | 192.6% | 320.7% |
| **Simulated annealing** | **128.0%** | **186.2%** | **308.0%** |

Simulated annealing wins on every set. On small instances where the true optimum
is known, annealing matches it on every one (within 1.00x optimal).

Reproduce these numbers with `PYTHONPATH=src python3 run_psplib.py --full`.

---

## Reproducibility

- Simulated annealing uses a fixed random seed, so runs are deterministic.
- `run_psplib.py` writes `results.csv`; `experiments.py` writes
  `exp_optimal.csv`, `exp_convergence.csv`, and `exp_complexity.csv`.

---

## Data

The PSPLIB benchmark sets (J30, J60, J120) are included under `data/psplib/`,
along with a small sample instance (`sample_j6.sm`) so the code runs out of the
box. PSPLIB is the standard public benchmark for this problem (Kolisch and
Sprecher, 1997).

---

## Testing

```bash
PYTHONPATH=src python3 -m pytest -q
```

The 28 tests cover the parser (including malformed files), CPM, the serial
scheduler, priority rules, annealing (reproducibility), and the exact solver
(matching the known optimum on small cases). They also check the core
invariants: no schedule ever violates precedence, exceeds a resource capacity,
or beats the lower bound.

---

## Team

Learning Team 5: Enrico Sarmiento, Santino Magtalas, Lorenzo Bello, Lia Imperial,
Nicolai Dominic, Patricia Bucad, Niccolo Dojoles.
