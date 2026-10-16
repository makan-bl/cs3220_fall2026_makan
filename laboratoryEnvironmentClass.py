import random

from src.environmentClass import Environment
from src.securityDroneClass import SecurityDrone
from src.labMazeData import DRONE, ACTION_NAMES, findCells

# Battery used for every single cell the robot moves (the tutorial's
# navigation environment also takes -1 performance for each move).
ENERGY_PER_MOVE = 1
DEFENSE_MODE_COST = 0.10   # Defense Mode uses 10% of the CURRENT energy


class LaboratoryEnvironment(Environment):
  """The Hazardous Laboratory.

  * holds the TRUE maze (with the drones) - the robots only get the map without drones
  * places one SecurityDrone (a Thing) on every drone cell
  * moves the robots, cell by cell, along the corridor chosen by each action
  * handles drone encounters: capture, or Defense Mode (-10% energy)
  """

  def __init__(self, labMaze, labGraph, seed=None):
    super().__init__()
    self.maze = labMaze          # true matrix (0-4)
    self.status = labGraph       # state-space graph (same one the robots use)
    self.things = []             # the security drones
    rng = random.Random(seed)
    n_nodes = len(labGraph.nodes())
    for cell in findCells(labMaze, DRONE):
      self.add_thing(SecurityDrone(cell, n_nodes, rng))

  # --- things ---------------------------------------------------------------
  def add_thing(self, thing, location=None):
    if isinstance(thing, SecurityDrone):
      self.things.append(thing)
      return
    if thing in self.agents:
      print("Can't add the same agent twice")
      return
    # A new robot plans its route as soon as it enters the laboratory
    print("=== {} enters the laboratory at {} with energy {} ===".format(
        thing.name, thing.location, thing.energy))
    thing(self.percept(thing))
    self.agents.append(thing)

  def drone_at(self, cell):
    for d in self.things:
      if d.location == cell:
        return d
    return None

  def percept(self, agent):
    # The robot only senses where it is and how much energy it has.
    return agent.state

  def is_agent_alive(self, agent):
    return agent.alive

  # --- drone encounter ------------------------------------------------------
  def encounter(self, agent, drone):
    agent.known_drones[drone.location] = drone.attack_power   # drone becomes known
    print("   !! {} met a security drone at {} (attack power {}), robot energy {}".format(
        agent.name, drone.location, drone.attack_power, agent.energy))
    # Defensive capability = the robot's current energy
    if drone.attack_power >= 2 * agent.energy:
      agent.captured = True
      agent.alive = False
      print("   XX The drone is at least twice as strong - {} is CAPTURED.".format(agent.name))
    else:
      new_energy = agent.energy - DEFENSE_MODE_COST * agent.energy
      agent.set_state(agent.location, new_energy)
      print("   ++ Defense Mode ON: -10% energy -> {}".format(agent.energy))

  # --- moving ---------------------------------------------------------------
  def execute_action(self, agent, action):
    if not self.is_agent_alive(agent):
      return
    edge = self.status.edge(agent.location, action)
    if edge is None:                          # not possible in this state: wall/boundary
      print("{} cannot go {} from {}".format(agent.name, ACTION_NAMES[action], agent.location))
      return
    print("{} does action {} ({}) from {}".format(
        agent.name, action, ACTION_NAMES[action], agent.location))
    for move, cell in zip(edge["actions"], edge["cells"]):
      agent.set_state(cell, agent.energy - ENERGY_PER_MOVE)
      agent.moves += 1
      agent.trail.append(cell)
      print("   {} -> {}  energy {}".format(ACTION_NAMES[move], cell, agent.energy))
      drone = self.drone_at(cell)
      if drone is not None:
        self.encounter(agent, drone)
      if self.update_agent_alive(agent):
        break

  def update_agent_alive(self, agent):
    """Returns True when the robot has stopped (dead or mission done)."""
    if not agent.alive:
      return True
    if agent.energy <= 0:
      agent.alive = False
      print("   XX {} ran out of energy at {}.".format(agent.name, agent.location))
      return True
    if agent.location == agent.goal:
      agent.reached_target = True
      agent.alive = False
      print("   ** {} reached the RESCUE TARGET {} with energy {}".format(
          agent.name, agent.goal, agent.energy))
      return True
    return False

  def step(self):
    if self.is_done():
      print("There is no one here who could work...")
      return
    for agent in self.agents:
      if not agent.alive:
        continue
      if not agent.seq:
        agent.alive = False
        print("{} has no actions left.".format(agent.name))
        continue
      self.execute_action(agent, agent.seq.pop(0))

  def run(self, steps=100):
    for step in range(steps):
      if self.is_done():
        return
      print("step {}:".format(step + 1))
      self.step()

  # --- results --------------------------------------------------------------
  def report(self):
    rows = []
    for a in self.agents:
      status = ("reached target" if a.reached_target
                else "captured" if a.captured
                else "out of energy" if a.energy <= 0
                else "did not reach target")
      rows.append({"agent": a.name, "result": status, "final energy": a.energy,
                   "cells moved": a.moves, "planned path cost": a.plan_cost,
                   "drones met": len(a.known_drones)})
    return rows

  def winner(self):
    """The agent that reached the target with the highest performance (energy)."""
    finishers = [a for a in self.agents if a.reached_target]
    if not finishers:
      return None, "No winner: no robot reached the rescue target."
    best = max(a.energy for a in finishers)
    top = [a for a in finishers if a.energy == best]
    if len(top) > 1:
      return top, "Draw: {} reached the target with the same energy {}.".format(
          " and ".join(a.name for a in top), best)
    return top[0], "Winner: {} (reached the target with energy {}).".format(top[0].name, best)
