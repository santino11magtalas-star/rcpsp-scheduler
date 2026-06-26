# quick sanity check -- load an instance and print what we parsed.
# run: PYTHONPATH=src python demo.py
from pathlib import Path

from rcpsp import parse_sm

SAMPLE = Path(__file__).parent / "data" / "psplib" / "sample_j6.sm"

p = parse_sm(SAMPLE)
print(f"loaded {SAMPLE.name}: {len(p)} jobs, resources={p.capacities}")
print("topo order:", p.topological_order())
print()
for j in p.topological_order():
    a = p.activities[j]
    print(f"  job {a.id}: dur={a.duration} req={a.requests} -> {a.successors}")
