import collections

from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.labMazeProblemClass import LabMazeProblem


class RescueRobotAgent(SimpleProblemSolvingAgentProgram):
  """Problem-solving Rescue Robot.

  The robot's state is (location, energy):
    * location = the cell the robot is in
    * energy   = battery level = the robot's performance

  Starting energy = number of nodes in the state-space graph
  (the same rule the tutorial's MazeProblemSolvingAgentSMART uses for performance).

  The robot knows the walls (its map) but NOT where the security drones are.
  A drone becomes known only when the robot walks into its cell (known_drones).
  """

  def __init__(self, name, initial_location, dataGraph, goal, program=None):
    super().__init__(initial_location)
    self.name = name
    self.dataGraph = dataGraph
    self.goal = goal
    self.performance = len(dataGraph.nodes())
    self.state = (initial_location, self.performance)   # energy is part of the state

    if program is None or not isinstance(program, collections.abc.Callable):
      raise ValueError("RescueRobotAgent needs a search program")
    self.program = program

    self.known_drones = {}      # {cell: attack power} - filled in while moving
    self.trail = [initial_location]   # every cell the robot has visited
    self.plan_nodes = []        # graph nodes on the planned route
    self.plan_cost = None       # path cost of the plan (action costs)
    self.reached_target = False
    self.captured = False
    self.moves = 0              # single cell moves made

  def __repr__(self):
    return "<{}>".format(self.name)

  # --- the robot's state -----------------------------------------------------
  @property
  def location(self):
    return self.state[0]

  @property
  def energy(self):
    return self.state[1]

  def set_state(self, location, energy):
    """Location and energy change together, so both stay in the state."""
    self.state = (location, round(energy, 2))
    self.performance = self.state[1]

  # --- the 4 phases of the problem-solving agent ----------------------------
  def update_state(self, state, percept):
    # percept = (location, energy) given by the environment
    return percept

  def formulate_goal(self, state):
    if self.goal is not None:
      return self.goal
    print("No goal! can't work!")
    return None

  def formulate_problem(self, state, goal):
    location = state[0]           # search only needs the location
    return LabMazeProblem(location, goal, self.dataGraph)

  def search(self, problem):
    node = self.program(problem)
    if node is None:
      print("{}: no route to the rescue target exists.".format(self.name))
      return []
    self.plan_nodes = [n.state for n in node.path()]
    self.plan_cost = node.path_cost
    solution = node.solution()          # list of actions 0-3
    print("{}: solution (actions) = {}".format(self.name, solution))
    print("{}: route through graph nodes = {}".format(self.name, self.plan_nodes))
    print("{}: path cost = {}".format(self.name, self.plan_cost))
    return solution
