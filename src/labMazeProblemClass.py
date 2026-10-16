from src.problemClass import Problem


class LabMazeProblem(Problem):
  """Search problem for the Rescue Robot.

  state   = a node of the laboratory graph (row, col)
  actions = 0 left, 1 up, 2 right, 3 down (only the ones that lead to another node)
  result  = the node reached by following the corridor in that direction
  path cost = sum of the action costs of every single move along the corridor
              (left 2, up 4, right 2, down 1)
  """

  def __init__(self, initial, goal, graph):
    super().__init__(initial, goal)
    self.graph = graph            # instance of labGraph

  def actions(self, state):
    return list(self.graph.origin[state].keys())

  def result(self, state, action):
    # Transition model RESULT(s, a)
    return self.graph.origin[state][action]

  def path_cost(self, cost_so_far, A, action, B):
    # Action cost function
    return cost_so_far + self.graph.edges[(A, action)]["cost"]
