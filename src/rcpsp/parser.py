# parser for PSPLIB single-mode (.sm) files.
# the format is section-based (headers like "PRECEDENCE RELATIONS:"), so we
# find each section and read the rows under it instead of hardcoding column
# positions -- that way the whitespace differences between files don't break us.
# ref: Kolisch & Sprecher 1997 (PSPLIB).
# NOTE: only single-mode + renewable resources for now. multi-mode (.mm) and
#       nonrenewable resources are out of scope.

from __future__ import annotations

from pathlib import Path

from .model import Activity, Project


def _section(lines, header):
    for i, line in enumerate(lines):
        if header in line:
            return i
    raise ValueError(f"section not found: {header!r}")


def _scalar(lines, key):
    # grab the int after "key : value"
    for line in lines:
        if key in line and ":" in line:
            return int(line.split(":")[1].split()[0])
    raise ValueError(f"key not found: {key!r}")


def parse_sm(path):
    lines = Path(path).read_text().splitlines()

    n_jobs = _scalar(lines, "jobs (incl. supersource/sink )")
    horizon = _scalar(lines, "horizon")
    n_renew = _scalar(lines, "- renewable")
    resource_names = [f"R{i + 1}" for i in range(n_renew)]

    activities = {j: Activity(id=j, duration=0) for j in range(1, n_jobs + 1)}

    # precedence rows look like: jobnr  #modes  #succ  succ1 succ2 ...
    start = _section(lines, "PRECEDENCE RELATIONS:") + 2
    for line in lines[start:]:
        parts = line.split()
        if not parts or not parts[0].isdigit():
            break
        job = int(parts[0])
        n_succ = int(parts[2])
        activities[job].successors = [int(x) for x in parts[3:3 + n_succ]]

    # durations + per-resource demand
    start = _section(lines, "REQUESTS/DURATIONS:") + 1
    for line in lines[start:]:
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        job = int(parts[0])
        activities[job].duration = int(parts[2])
        demands = [int(x) for x in parts[3:3 + n_renew]]
        activities[job].requests = dict(zip(resource_names, demands))

    # capacities: the "R 1  R 2 ..." label row has letters so we skip it,
    # the real values are the numbers-only row right after. (got bit by this.)
    start = _section(lines, "RESOURCEAVAILABILITIES:") + 1
    capacities = {}
    for line in lines[start:]:
        if any(c.isalpha() for c in line):
            continue
        nums = [int(x) for x in line.split() if x.lstrip("-").isdigit()]
        if nums:
            capacities = dict(zip(resource_names, nums))
            break

    proj = Project(activities=activities, capacities=capacities, horizon=horizon)
    proj.validate_acyclic()
    return proj
