# DSA Final Project — Phase Plan

**Topic:** Project Management Algorithms (CPM/PERT → RCPSP) · Team of 6
**Owners:** Core A · Core B · Test · Report A · Report B · Viz

---

## Phase 0 — Setup  *(this week)*
- [ ] Claim the topic with the prof (first-come-first-served) **(All)**
- [ ] Create repo, `requirements.txt`, README scaffold, branch protection **(Test)**
- [ ] Download PSPLIB J30/J60/J120 + optimal/best-known bounds into `data/` **(Test)**
- [ ] Define `Activity` / `Project` / DAG in `model.py` **(Core A)**
- [ ] Write `parser.py` for `.sm` format + acyclicity check via topo sort **(Core A)**
- [ ] Agree on the schedule data structure (start times + resource profile) **(Core A+B)**

## Phase 1 — Prototype  *(→ Midterm session)*
- [ ] `cpm.py`: forward/backward pass, ES/EF/LS/LF, slack, critical path **(Core B)**
- [ ] PERT: three-point estimates → mean/variance, completion probability **(Core B)**
- [ ] Unit tests for CPM/slack on 2–3 hand-computed networks **(Test)**
- [ ] First Gantt + network-diagram render from a CPM result **(Viz)**
- [ ] Report skeleton: sections, RCPSP definition, NP-hardness outline **(Report A+B)**
- [ ] **Midterm deliverable:** finalized proposal + prototype running end-to-end

## Phase 2 — Depth & Polish  *(Midterm → Finals)*
- [ ] `sgs.py`: serial + parallel schedule-generation schemes **(Core A)**
- [ ] `priority.py`: min-slack, LFT, GRPW, most-successors; compare **(Core A)**
- [ ] `genetic.py`: activity-list GA, precedence-preserving crossover/mutation **(Core B)**
- [ ] `annealing.py`: SA variant for comparison **(Core B)**
- [ ] `exact.py`: small branch & bound on J30 (stretch) **(Core B)**
- [ ] `evaluate.py` + `run_psplib.py`: batch benchmark → `results.csv` **(Test)**
- [ ] Integration tests (reproduce known optima) + stress tests (J120, timeouts) **(Test)**
- [ ] CI on every push; PEP8/format pass; docstrings **(Test)**
- [ ] Convergence + gap-to-optimal plots **(Viz)**
- [ ] Finish report: proof, results, discussion **(Report A+B)**
- [ ] Build + rehearse 10-min deck (< 10:00) **(Viz + All)**
- [ ] **Finals:** report PDF + tagged repo release + presentation
