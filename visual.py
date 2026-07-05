# Draws the two project pictures from our own data
# 1. The Gantt chart 
# 2. The DAG chart 
# they both pull the data from the Project + CPM result
# Needs: pip install matplotlib networkx 
# To run: PYTHONPATH=src python3 viz.py

import matplotlib.pyplot as plt
import networkx as nx
from rcpsp import critical_path_method, parse_sm

# colors
CRIT = "#E8833A"   # orange = critical path
NORM = "#1E2761"   # navy = everything
BAR = "#1C7293"    # teal = normal gantt 

def draw_dag(project, result, save=None):
    g = nx.DiGraph()
    for act in project.activities.values():
        for s in act.successors:
            g.add_edge(act.id, s)
 
    crit = set(result.critical_path())
    # a "layered" layout: x = position in the topological order, y = spread out
    order = project.topological_order()
    xpos = {j: i for i, j in enumerate(order)}
    pos = {}
    seen_at_x = {}
    for j in order:
        x = xpos[j]
        row = seen_at_x.get(x, 0)
        pos[j] = (x, -row)
        seen_at_x[x] = row + 1
 
    node_colors = [CRIT if n in crit else NORM for n in g.nodes()]
    # highlight edges that are on the critical path too
    crit_path = result.critical_path()
    crit_edges = set(zip(crit_path, crit_path[1:]))
    edge_colors = [CRIT if e in crit_edges else "#AEB9CC" for e in g.edges()]
    widths = [2.5 if e in crit_edges else 1.2 for e in g.edges()]
 
    plt.figure(figsize=(9, 5))
    nx.draw(g, pos, with_labels=True, node_color=node_colors, font_color="white",
            font_weight="bold", node_size=900, edge_color=edge_colors,
            width=widths, arrowsize=18)
    plt.title("Project DAG  (critical path in orange)")
    plt.axis("off")
    if save:
        plt.savefig(save, dpi=150)
        print("saved", save)
 
 
def draw_gantt(project, result, save=None):
    crit = set(result.critical_path())
    order = project.topological_order()
 
    fig, ax = plt.subplots(figsize=(9, 5))
    for row, j in enumerate(order):
        start = result.es[j]
        dur = project.activities[j].duration
        color = CRIT if j in crit else BAR
        ax.barh(row, dur, left=start, height=0.6, color=color)
        ax.text(start + dur / 2, row, f"job {j}", va="center", ha="center",
                color="white", fontsize=9)
 
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([f"job {j}" for j in order])
    ax.invert_yaxis()
    ax.set_xlabel("time")
    ax.set_title(f"Gantt chart  (makespan = {result.makespan}, critical in orange)")
    plt.tight_layout()
    if save:
        plt.savefig(save, dpi=150)
        print("saved", save)
 
 
if __name__ == "__main__":
    p = parse_sm("data/psplib/sample_j6.sm")
    r = critical_path_method(p)
    draw_dag(p, r, save="dag.png")
    draw_gantt(p, r, save="gantt.png")
    plt.show()
 
