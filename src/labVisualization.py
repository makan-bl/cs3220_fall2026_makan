# Drawing helpers for Lab 4 (matplotlib picture of the maze + pyvis graphs)
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from pyvis.network import Network

from src.labMazeData import (FREE, WALL, DRONE, TARGET, START, ACTION_NAMES,
                             tupleToStr)

CELL_COLORS = {FREE: "#eef3fb", WALL: "#555555", DRONE: "#f4a6a6",
               TARGET: "#9be39b", START: "#ffd966"}
CELL_TEXT = {FREE: "", WALL: "#", DRONE: "D", TARGET: "T", START: "S"}
TRAIL_COLORS = ["#1f6fd1", "#d1491f", "#7a3fb8", "#2a9d5c"]


def drawLabMaze(maze, title="7 x 7 Laboratory Maze", trails=None, ax=None, show_codes=True):
  """Coloured picture of the maze matrix.
  trails = {agent name: [cells visited]} -> drawn as lines on top."""
  n_rows, n_cols = maze.shape
  if ax is None:
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
  cmap = ListedColormap([CELL_COLORS[k] for k in range(5)])
  ax.imshow(maze, cmap=cmap, vmin=-0.5, vmax=4.5)
  for r in range(n_rows):
    for c in range(n_cols):
      code = int(maze[r, c])
      label = CELL_TEXT[code]
      if show_codes:
        label = "{}\n{}".format(label, code) if label else str(code)
      ax.text(c, r, label, ha="center", va="center", fontsize=11,
              color="white" if code == WALL else "black", fontweight="bold")
  ax.set_xticks(range(n_cols))
  ax.set_yticks(range(n_rows))
  ax.set_xticks([x - 0.5 for x in range(1, n_cols)], minor=True)
  ax.set_yticks([y - 0.5 for y in range(1, n_rows)], minor=True)
  ax.grid(which="minor", color="black", linewidth=1)
  ax.tick_params(which="minor", length=0)
  ax.xaxis.tick_top()
  ax.set_title(title, pad=24, fontsize=14, fontweight="bold")

  handles = [Patch(color=CELL_COLORS[k], label="{} - {}".format(k, name))
             for k, name in [(FREE, "free"), (WALL, "wall/debris"), (DRONE, "security drone"),
                             (TARGET, "rescue target"), (START, "start")]]
  if trails:
    for i, (name, cells) in enumerate(trails.items()):
      off = (i - (len(trails) - 1) / 2) * 0.15      # shift lines so they don't overlap
      xs = [c + off for (_, c) in cells]
      ys = [r + off for (r, _) in cells]
      color = TRAIL_COLORS[i % len(TRAIL_COLORS)]
      ax.plot(xs, ys, "-o", color=color, linewidth=3, markersize=5, alpha=0.85)
      handles.append(plt.Line2D([0], [0], color=color, linewidth=3, label=name))
  ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=10)
  return ax


def _new_network(heading):
  net = Network(heading=heading, bgcolor="#242020", font_color="white",
                height="750px", width="100%", directed=True)   # directed: keep BOTH directions
  net.toggle_physics(False)
  net.set_edge_smooth("curvedCW")      # A->B and B->A are drawn as two separate arcs
  return net


def _node_color(maze, cell, start, target):
  if cell == start:
    return "gold"
  if cell == target:
    return "green"
  if maze[cell] == DRONE:
    return "red"
  return "white"


def cellNetwork(maze, cellTM, start, target, heading="Lab4. All available actions (cell level)"):
  """Every non-wall cell is a node, every AVAILABLE action is its own arrow.
  Walls are drawn as small grey squares so the layout looks like the maze."""
  net = _new_network(heading)
  n_rows, n_cols = maze.shape
  for r in range(n_rows):
    for c in range(n_cols):
      cell = (r, c)
      if maze[cell] == WALL:
        net.add_node(tupleToStr(cell), label=" ", title="{} wall".format(tupleToStr(cell)),
                     x=c * 120, y=r * 120, color="#555555", shape="square", size=12)
      else:
        net.add_node(tupleToStr(cell), label=tupleToStr(cell), title=tupleToStr(cell),
                     x=c * 120, y=r * 120, color=_node_color(maze, cell, start, target),
                     shape="dot", size=12, font={"color": "white"})
  for cell, moves in cellTM.items():
    for action, nxt in moves.items():
      net.add_edge(tupleToStr(cell), tupleToStr(nxt), label=str(action),
                   title="{} {}".format(action, ACTION_NAMES[action]), color="#97c2fc",
                   font={"color": "white", "strokeWidth": 0, "size": 10})
  return net


def graphNetwork(G, maze, start, target, paths=None,
                 heading="Lab4. State-space graph of the Laboratory"):
  """The decision-point graph. Edge label = 'action (cost)'.
  paths = {agent name: [graph nodes on the route]} -> those edges are coloured."""
  net = _new_network(heading)
  for node in sorted(G.nodes()):
    x, y = G.getLocation(node)
    net.add_node(tupleToStr(node), label=tupleToStr(node), title=tupleToStr(node),
                 x=x * 2, y=y * 2, color=_node_color(maze, node, start, target),
                 shape="dot", size=14, font={"color": "white"})
  on_path = {}
  for i, (name, nodes) in enumerate((paths or {}).items()):
    for a, b in zip(nodes, nodes[1:]):
      on_path.setdefault((a, b), []).append((name, TRAIL_COLORS[i % len(TRAIL_COLORS)]))
  for (node, action), e in sorted(G.edges.items()):
    users = on_path.get((node, e["to"]), [])
    color = users[0][1] if users else "#97c2fc"
    width = 5 if users else 1
    title = "{} -> {}: actions {} through {} cost {}".format(
        tupleToStr(node), tupleToStr(e["to"]), e["actions"],
        [tupleToStr(c) for c in e["cells"]], e["cost"])
    if users:
      title += " | used by " + ", ".join(n for n, _ in users)
    net.add_edge(tupleToStr(node), tupleToStr(e["to"]),
                 label="{} ({})".format(action, e["cost"]), title=title,
                 color=color, width=width, font={"color": "white", "strokeWidth": 0, "size": 11})
  return net
