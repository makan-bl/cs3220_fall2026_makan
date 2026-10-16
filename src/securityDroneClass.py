import random

from src.thingClass import Thing


class SecurityDrone(Thing):
  """An enemy drone sitting in one cell of the laboratory.

  attack_power is random, between 10% and 40% of the number of nodes
  in the state-space graph."""

  def __init__(self, location, n_graph_nodes, rng=random):
    self.location = location
    low = 0.10 * n_graph_nodes
    high = 0.40 * n_graph_nodes
    self.attack_power = round(rng.uniform(low, high), 1)

  def __repr__(self):
    return "<SecurityDrone at {} attack={}>".format(self.location, self.attack_power)
