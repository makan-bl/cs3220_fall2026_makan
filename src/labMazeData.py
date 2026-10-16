# Lab 4 - Task 1: the Hazardous Laboratory Maze
#
# Cell codes in the maze matrix (as suggested in the task):
#   0 = free cell
#   1 = wall / debris
#   2 = security drone
#   3 = rescue target
#   4 = robot starting position
import random
from collections import deque

import numpy as np

FREE, WALL, DRONE, TARGET, START = 0, 1, 2, 3, 4
CELL_NAMES = {FREE: "free", WALL: "wall/debris", DRONE: "security drone",
              TARGET: "rescue target", START: "start"}

# The robot's 4 actions, encoded as integers 0-3
LEFT, UP, RIGHT, DOWN = 0, 1, 2, 3
ACTION_NAMES = {LEFT: "left", UP: "up", RIGHT: "right", DOWN: "down"}

# How each action changes (row, column)
MOVES = {LEFT: (0, -1), UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0)}

# Cost of ONE move (one cell) for each action - used by the UCS agent
ACTION_COSTS = {LEFT: 2, UP: 4, RIGHT: 2, DOWN: 1}


# ---------------------------------------------------------------------------
# 1. Maze generator
# ---------------------------------------------------------------------------
def makeLabMaze(n=7, wall_share=0.25, drone_share=0.10, min_distance=4, seed=None):
  """Random n x n laboratory maze (NumPy matrix).

  * 25% of the cells are walls/debris (1)
  * 10% of the cells are security drones (2)
  * one free cell is the robot's start (4), one free cell is the rescue target (3)
  * everything else is free (0)

  The maze is generated again until the target can be reached from the start
  (walls block, drones do not), and start and target are at least
  `min_distance` steps apart (Manhattan distance) so the trip is not trivial.
  """
  rng = random.Random(seed)
  total = n * n
  n_walls = round(total * wall_share)    # 49 * 0.25 = 12.25 -> 12
  n_drones = round(total * drone_share)  # 49 * 0.10 = 4.9  -> 5
  cells = [(i, j) for i in range(n) for j in range(n)]

  while True:
    rng.shuffle(cells)
    maze = np.zeros((n, n), dtype=int)
    walls = cells[:n_walls]
    drones = cells[n_walls:n_walls + n_drones]
    free = cells[n_walls + n_drones:]
    start, target = free[0], free[1]
    for c in walls:
      maze[c] = WALL
    for c in drones:
      maze[c] = DRONE
    maze[start] = START
    maze[target] = TARGET

    far_enough = abs(start[0] - target[0]) + abs(start[1] - target[1]) >= min_distance
    if far_enough and pathExists(maze, start, target):
      return maze


def pathExists(maze, start, target):
  """Breadth-first flood fill over every non-wall cell."""
  seen, queue = {start}, deque([start])
  while queue:
    cell = queue.popleft()
    if cell == target:
      return True
    for nxt in neighbours(maze, cell).values():
      if nxt not in seen:
        seen.add(nxt)
        queue.append(nxt)
  return False


def findCell(maze, code):
  """(row, col) of the first cell with this code (used for start and target)."""
  r, c = np.argwhere(maze == code)[0]
  return (int(r), int(c))


def findCells(maze, code):
  return [(int(r), int(c)) for r, c in np.argwhere(maze == code)]


def robotMap(maze):
  """What the robot knows: the walls, the start and the target.
  The security drones are UNKNOWN to the robot, so their cells look free (0)."""
  known = maze.copy()
  known[known == DRONE] = FREE
  return known


def countSummary(maze):
  n = maze.shape[0] * maze.shape[1]
  lines = []
  for code, name in CELL_NAMES.items():
    k = int((maze == code).sum())
    lines.append("{} - {}: {} cells ({:.0%})".format(code, name, k, k / n))
  return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Actions and the (cell level) transition model
# ---------------------------------------------------------------------------
def neighbours(maze, cell):
  """{action: next_cell} for every move that stays inside the maze
  and does not go into a wall."""
  n_rows, n_cols = maze.shape
  result = {}
  for action, (dr, dc) in MOVES.items():
    r, c = cell[0] + dr, cell[1] + dc
    if 0 <= r < n_rows and 0 <= c < n_cols and maze[r, c] != WALL:
      result[action] = (r, c)
  return result


def defineLabAvailableActions(maze):
  """{cell: [available actions]} for every cell the robot can stand on.
  Boundaries and walls remove actions."""
  acts = {}
  for r in range(maze.shape[0]):
    for c in range(maze.shape[1]):
      if maze[r, c] != WALL:
        acts[(r, c)] = sorted(neighbours(maze, (r, c)).keys())
  return acts


def makeLabTransitionModel(labActs):
  """Transition model RESULT(s, a) for single cells:
  {cell: {action: next_cell}}"""
  tm = {}
  for cell, actions in labActs.items():
    tm[cell] = {}
    for a in actions:
      dr, dc = MOVES[a]
      tm[cell][a] = (cell[0] + dr, cell[1] + dc)
  return tm


# ---------------------------------------------------------------------------
# 3. The state-space graph: only the cells where a decision is made
# ---------------------------------------------------------------------------
def decisionPoints(cellTM, start, target):
  """Graph nodes = the start, the target, and every junction
  (a cell with 3 or 4 open directions = a real choice between paths)."""
  return [cell for cell in cellTM
          if cell == start or cell == target or len(cellTM[cell]) >= 3]


def makeLabGraphData(cellTM, start, target):
  """Walk every corridor that leaves a decision point until the next decision point.

  Returns
    graphData: {node: {action: next_node}}   <- transition model of the graph
    edgeData:  {(node, action): {'to', 'actions', 'cells', 'cost'}}
               'actions' / 'cells' are the single moves walked along the corridor,
               'cost' is the sum of their action costs.
  Corridors that end in a dead end are dropped (nothing useful down there).
  """
  nodes = set(decisionPoints(cellTM, start, target))
  graphData, edgeData = {}, {}
  for node in sorted(nodes):
    graphData[node] = {}
    for action, nxt in sorted(cellTM[node].items()):
      moves, cells = [action], [nxt]
      prev, cur = node, nxt
      while cur not in nodes:
        onward = [(a, c) for a, c in sorted(cellTM[cur].items()) if c != prev]
        if not onward:          # dead end
          break
        a, c = onward[0]        # corridor cell: exactly one way forward
        moves.append(a)
        cells.append(c)
        prev, cur = cur, c
      if cur in nodes and cur != node:
        graphData[node][action] = cur
        edgeData[(node, action)] = {
            "to": cur,
            "actions": moves,
            "cells": cells,
            "cost": sum(ACTION_COSTS[a] for a in moves),
        }
  return graphData, edgeData


def labStatesLocations(keyList, scale=60):
  """Screen position of each node = where it is in the maze."""
  return {k: (k[1] * scale, k[0] * scale) for k in keyList}


def tupleToStr(t):
  return "-".join(str(item) for item in t)
