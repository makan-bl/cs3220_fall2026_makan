from src.maze2026GraphClass import mazeGraph


class labGraph(mazeGraph):
  """State-space graph of the Hazardous Laboratory.

  Nodes  = start, rescue target, and every junction (a cell where the robot can choose
           between several paths).
  Edges  = the corridors between those nodes.

  Same idea as the tutorial's mazeGraph:
    self.origin     = {node: {action: next_node}}    -> the transition model (actions 0-3)
    self.graph_dict = {node: {next_node: cost}}      -> used for drawing / get()
  Extra:
    self.edges      = {(node, action): {'to', 'actions', 'cells', 'cost'}}
                      the single moves walked along each corridor and their total cost
  """

  def __init__(self, graph_dict=None, edges=None, locations=None):
    self.edges = edges or {}
    super().__init__(graph_dict, locations)

  def make_graph(self, graph_dict):
    for a in graph_dict.keys():
      self.graph_dict.setdefault(a, {})          # keep nodes even if they have no exits
      for (act, b) in graph_dict[a].items():
        cost = self.edges[(a, act)]["cost"]
        old = self.graph_dict[a].get(b)
        if old is None or cost < old:           # two corridors A->B: keep the cheaper one
          self.connect(a, b, cost)

  def edge(self, node, action):
    return self.edges.get((node, action))
