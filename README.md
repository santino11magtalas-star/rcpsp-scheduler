# RCPSP Scheduler

DSA 2026 final project — **Project Management Algorithms**. A scheduler for the
Resource-Constrained Project Scheduling Problem (RCPSP), built up from
polynomial critical-path analysis to heuristics and metaheuristics, benchmarked
on the PSPLIB instance library.

## Status

**Phase 0 (setup) — done:** project model, PSPLIB `.sm` parser, acyclicity check,
sample instance, tests. CPM/PERT and the schedulers land in later phases (see
`PHASE_PLAN.md`).

## Layout

```
src/rcpsp/
  model.py    Activity, Project (DAG + topological sort), Schedule
  parser.py   PSPLIB .sm loader
data/psplib/  instances (sample included; drop real J30/J60/J120 here)
tests/        unit tests
demo.py       loads an instance and prints its summary
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
PYTHONPATH=src python demo.py          # load the sample instance
PYTHONPATH=src python -m pytest -q     # run the test suite
```

## Data

A small **synthetic** instance (`data/psplib/sample_j6.sm`) is included so the
code runs out of the box. The real benchmark sets (J30 / J60 / J120) come from
PSPLIB — download the `.sm` files and their optimal/best-known bounds and drop
them into `data/psplib/`. The parser reads them with no changes.

## Schedule representation

A solution is a `Schedule`: an integer start time per activity
(`starts: dict[int, int]`). Makespan is the max finish over all activities;
resource feasibility is validated against this profile in Phase 2.
