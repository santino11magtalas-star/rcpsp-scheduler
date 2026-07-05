# automatically generates the project pictures from our own data:
#   1. the DAG            
#   2. the Gantt chart    
#   3. the three views side by side: of DAG and Gantt charts in topological order
# all of data came from the Project + CPM result
# needs: pip install matplotlib networkx
# to run:   PYTHONPATH=src python3 visual.py

import matplotlib.pyplot as plt
import networkx as nx
from rcpsp import critical_path_method, parse_sm

# colors 
CRIT = "#E8833A"   # orange = critical path 
NORM = "#1E2761"   # navy = everything else
BAR = "#1C7293"    # teal = normal gantt bar


def _layered_pos(project):
    # position nodes left-to-right by their spot in the topological order
    order = project.topological_order()
    xpos = {j: i for i, j in enumerate(order)}
    pos, seen = {}, {}
    for j in order:
        x = xpos[j]
        row = seen.get(x, 0)
        pos[j] = (x, -row)
        seen[x] = row + 1
    return pos

def draw_dag(project, result, ax=None):
    g = nx.DiGraph()
    for act in project.activities.values():
        for s in act.successors:
            g.add_edge(act.id, s)
    crit = set(result.critical_path())
    crit_path = result.critical_path()
    crit_edges = set(zip(crit_path, crit_path[1:]))
    pos = _layered_pos(project)
    node_colors = [CRIT if n in crit else NORM for n in g.nodes()]
    edge_colors = [CRIT if e in crit_edges else "#AEB9CC" for e in g.edges()]
    widths = [2.5 if e in crit_edges else 1.2 for e in g.edges()]

    if ax is None:
        plt.figure(figsize=(9, 5))
        ax = plt.gca()
    nx.draw(g, pos, ax=ax, with_labels=True, node_color=node_colors,
            font_color="white", font_weight="bold", node_size=800,
            edge_color=edge_colors, width=widths, arrowsize=16)
    ax.set_title("DAG (critical path in orange)")

def draw_topo_order(project, result, ax=None):
    # the tasks flattened into one valid order, left to right
    order = project.topological_order()
    crit = set(result.critical_path())
    if ax is None:
        plt.figure(figsize=(9, 2.5))
        ax = plt.gca()
    for i, j in enumerate(order):
        color = CRIT if j in crit else NORM
        ax.scatter(i, 0, s=900, color=color, zorder=2)
        ax.text(i, 0, str(j), color="white", ha="center", va="center",
                fontweight="bold", zorder=3)
        if i < len(order) - 1:
            ax.annotate("", xy=(i + 0.8, 0), xytext=(i + 0.2, 0),
                        arrowprops=dict(arrowstyle="->", color="#AEB9CC"))
    ax.set_xlim(-0.5, len(order) - 0.5)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    ax.set_title("Topological order")

def draw_gantt(project, result, ax=None):
    crit = set(result.critical_path())
    order = project.topological_order()
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    for row, j in enumerate(order):
        start = result.es[j]
        dur = project.activities[j].duration
        color = CRIT if j in crit else BAR
        ax.barh(row, dur, left=start, height=0.6, color=color)
        ax.text(start + dur / 2, row, f"job {j}", va="center", ha="center",
                color="white", fontsize=8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([f"job {j}" for j in order])
    ax.invert_yaxis()
    ax.set_xlabel("time")
    ax.set_title(f"Gantt (makespan = {result.makespan})")

def draw_all_three(project, result, save=None):
    # DAG | topological order | Gantt, all in one figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    draw_dag(project, result, ax=axes[0])
    draw_topo_order(project, result, ax=axes[1])
    draw_gantt(project, result, ax=axes[2])
    fig.suptitle("Same project, three ways", fontsize=15, fontweight="bold")
    plt.tight_layout()
    if save:
        plt.savefig(save, dpi=150, bbox_inches="tight")
        print("saved", save)

if __name__ == "__main__":
    p = parse_sm("data/psplib/sample_j6.sm")
    r = critical_path_method(p)

    # the three-views comparison (the one the prof suggested)
    draw_all_three(p, r, save="three_views.png")

    # or each on its own:
    draw_dag(p, r)
    plt.savefig("dag.png", dpi=150, bbox_inches="tight")
    draw_gantt(p, r)
    plt.savefig("gantt.png", dpi=150, bbox_inches="tight")
    print("saved dag.png, gantt.png")
    plt.show()
