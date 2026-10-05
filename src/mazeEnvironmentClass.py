import random

from src.environmentClass import Environment
from src.mazeProblemClass import maze_moves
from data.mazeData import TREASURES, START, FINISH


class MazeEnvironment(Environment):
  """The Treasure Maze environment.

  Treasure placement rules:
    * placed randomly at nodes (vertices) of the maze graph
    * not at the start, not at the finish
    * no two treasures at the same node (a node holds at most one treasure)
  """

  def __init__(self, mazeGraph, directions, treasures=None, start=START, finish=FINISH, deadly=True):
    super().__init__()
    self.deadly = deadly          # True: the Agent dies when its performance reaches 0
    self.status = mazeGraph
    self.directions = directions
    self.start = start
    self.finish = finish
    self.treasures = dict(treasures) if treasures is not None else self.place_treasures()

  def place_treasures(self):
    valid = [n for n in sorted(self.status.nodes()) if n not in (self.start, self.finish)]
    spots = random.sample(valid, len(TREASURES))     # sample = no two treasures on the same node
    return dict(zip(spots, TREASURES.keys()))

  def show_treasures(self):
    for node, t in sorted(self.treasures.items(), key=lambda x: x[1]):
      print("  {} {} at {}".format(TREASURES[t], t, node))

  def percept(self, agent):
    # fully observable: the agent's state + where the treasures are
    return agent.state, dict(self.treasures)

  def is_agent_alive(self, agent):
    return agent.alive

  def is_done(self):
    return not any(agent.alive for agent in self.agents)

  def add_thing(self, thing, location=None):
    if thing in self.agents:
      print("Can't add the same agent twice")
      return
    self.agents.append(thing)
    print("Treasures in the maze:")
    self.show_treasures()
    thing(self.percept(thing))       # the agent plans when it enters the maze
    print("The Agent in {} facing {} with performance {}".format(thing.position, thing.heading, thing.performance))

  def goal_reached(self, agent):
    goal_node, required = agent.goal[-1]          # the final goal
    return agent.position == goal_node and all(t in agent.collected for t in required)

  def execute_action(self, agent, action):
    if not self.is_agent_alive(agent) or action is None:
      return
    node, heading, collected = agent.state
    neighbour = maze_moves(self.status, self.directions, node, heading)[action]
    new_heading = self.directions[(node, neighbour)][1]
    agent.performance -= 1

    treasure = self.treasures.pop(neighbour, None)   # grab a treasure lying there
    if treasure:
      collected = tuple(sorted(collected + (treasure,)))
    agent.state = (neighbour, new_heading, collected)
    print("Agent in {} facing {} with performance = {}".format(neighbour, new_heading, agent.performance))
    if treasure:
      print("Agent grabbed {} {} at {}".format(TREASURES[treasure], treasure, neighbour))

    if self.goal_reached(agent):
      print("Agent reached the goal: the exit \U0001F3E0 {} with {} treasure(s): {}".format(
          neighbour, len(collected), ", ".join(collected) if collected else "none"))
      agent.alive = False
    elif self.deadly and agent.performance <= 0:
      agent.alive = False
      print("Agent in {} is dead (performance {}).".format(neighbour, agent.performance))

  def step(self):
    if self.is_done():
      print("There is no one here who could work...")
      return
    for agent in self.agents:
      if agent.alive:
        if not agent.seq:              # nothing left to do
          agent.alive = False
          print("The Agent has no actions left.")
          continue
        action = agent.seq.pop(0)
        print("Agent decided to do {}.".format(action))
        self.execute_action(agent, action)

  def run(self, steps=100):
    for step in range(steps):
      if self.is_done():
        return
      print("step {0}:".format(step + 1))
      self.step()
