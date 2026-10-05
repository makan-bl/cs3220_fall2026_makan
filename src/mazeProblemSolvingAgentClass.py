import collections.abc

from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.mazeProblemClass import MazeProblem
from data.mazeData import TREASURES


def describe_goal(goal):
    node, required = goal
    parts = []
    if required:
        parts.append("collect " + ", ".join(f"{TREASURES[t]} {t}" for t in required))
    if node is not None:
        parts.append("reach {}".format("the exit \U0001F3E0 F" if node == 'F' else node))
    return " and ".join(parts)


class MazeProblemSolvingAgent(SimpleProblemSolvingAgentProgram):
  """Problem-solving agent for the Treasure Maze.

  goal is a LIST of goals solved one after another, each goal = (node, requiredTreasures):
    Basic               [('F', ())]
    Treasure collection [('F', ('Diamond', 'Extra Points', 'Gold', 'Pizza'))]
    Specific treasure   [(None, ('Diamond',)), ('F', ('Diamond',))]   <- grab it, then redefine the goal: the exit
  """

  def __init__(self, initial_state=None, mazeGraph=None, directions=None, goal=None, program=None, heading='E'):
    super().__init__((initial_state, heading, ()))
    self.dataGraph = mazeGraph
    self.directions = directions
    self.goal = goal
    self.treasureMap = {}            # {node: treasure}, perceived from the environment
    self.planned_states = []         # the states the plan goes through (for drawing)

    # Initially the Agent's performance is 50% of the number of nodes
    self.performance = len(mazeGraph.nodes()) // 2

    if program is None or not isinstance(program, collections.abc.Callable):
      print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))

      def program(percept):
        return eval(input('Percept={}; action? '.format(percept)))

    self.program = program

  # convenient views of the state
  @property
  def position(self):
    return self.state[0]

  @property
  def heading(self):
    return self.state[1]

  @property
  def collected(self):
    return self.state[2]

  def update_state(self, state, percept):
    # percept = (agent state, {node: treasure} still lying in the maze)
    agent_state, treasure_map = percept
    self.treasureMap = dict(treasure_map)
    return agent_state

  def formulate_goal(self, state):
    if self.goal is not None:
      return self.goal
    print("No goal! can't work!")
    return None

  def formulate_problem(self, state, goal):
    # the agent only cares about the treasures its goal needs
    wanted = {node: t for node, t in self.treasureMap.items() if t in goal[1]}
    return MazeProblem(state, goal, self.dataGraph, self.directions, wanted)

  def search(self, problem):
    node = self.program(problem)
    if node is None:
      print("No solution!")
      return [], problem.initial
    path = node.path()
    self.planned_states.extend(n.state for n in path[1:])
    solution = [n.action for n in path[1:]]
    print("Solution (a sequence of actions) from the initial state to a goal: {}".format(solution))
    print("Path: {}".format(" -> ".join(n.state[0] for n in path)))
    return solution, node.state

  def __call__(self, percept):
    self.state = self.update_state(self.state, percept)
    if self.seq:
      print("I have already done my work. Find someone else")
      return None

    goals = self.formulate_goal(self.state)          # PHASE 1: goal formulation
    if not goals:
      return None
    state = self.state
    self.planned_states = [state]
    for i, goal in enumerate(goals):
      if i > 0:
        print("Goal reached -> the Agent redefines its goal")
      print("Goal {}: {}".format(i + 1, describe_goal(goal)))
      problem = self.formulate_problem(state, goal)   # PHASE 2: problem formulation
      solution, state = self.search(problem)         # PHASE 3: search
      if not solution and not problem.goal_test(state):
        self.seq = []
        return None
      self.seq.extend(solution)
    print("Plan: {} actions, the Agent has performance {}".format(len(self.seq), self.performance))
    return None
