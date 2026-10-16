#How do we decide which node from the frontier to expand next?
from src.nodeClass import Node
from queue import PriorityQueue

nodeColors={
    "start":"red",
    "goal": "green",
    "frontier": "orange",
    "expanded":"pink"
}

def BestFirstSearchAgentProgram(f=None):
  #with BFS we choose a node, n, with minimum value of some evaluation function, f (n).
    
    def program(problem):

      node = Node(problem.initial)
      #node.color=nodeColors["start"]
      #print(node.state)
      frontier = PriorityQueue()
      frontier.put((1,node))
      #node.color=nodeColors["frontier"]
      reached = {problem.initial:node}

      while frontier:
        node = frontier.get()[1]
        #node.color=nodeColors["expanded"]
        print(node)

        if problem.goal_test(node.state):
          node.color=nodeColors["goal"]
          return node

        #reached.add(node.state)
        for child in node.expand(problem):
            if child.state not in reached or child.path_cost<reached[child.state].path_cost:
                frontier.put((1,child))
                #child.color=nodeColors["frontier"]
                reached.update({child.state:child})
            
        #node.color=nodeColors["expanded"]
      return None

    return program
  
 











def BestFirstSearchAgentProgramForShow(f=None):
  #with BFS we choose a node, n, with minimum value of some evaluation function, f (n).
    
    def program(problem):
      #print(111)
      steps = 0
      allNodeColors = []
      nodeColors = {k : 'white' for k in problem.graph.nodes()}

      node = Node(problem.initial)
      nodeColors[node.state] = "yellow"
      steps += 1
      allNodeColors.append(dict(nodeColors))

      #print(node.state)
      frontier = PriorityQueue()
      frontier.put((1,node))

      nodeColors[node.state] = "orange"
      steps += 1
      allNodeColors.append(dict(nodeColors))



      reached = {problem.initial:node}

      while frontier:
        node = frontier.get()[1]
        nodeColors[node.state] = "red"
        steps += 1
        allNodeColors.append(dict(nodeColors))
        #print(node)

        if problem.goal_test(node.state):
          nodeColors[node.state] = "green"
          steps += 1
          allNodeColors.append(dict(nodeColors))
          return (node,steps,allNodeColors)
          

        #reached.add(node.state)
        for child in node.expand(problem):
            if child.state not in reached or child.path_cost<reached[child.state].path_cost:
                frontier.put((1,child))
                nodeColors[child.state] = "orange"
                steps += 1
                allNodeColors.append(dict(nodeColors))

                reached.update({child.state:child})

        # modify the color of explored nodes to blue
        nodeColors[node.state] = "blue"
        steps += 1
        allNodeColors.append(dict(nodeColors))
            
      return None

    return program


# =====================================================================
# Lab 4 - Task 2: search programs for the Rescue Robot agents
# =====================================================================
import heapq
import itertools

CUTOFF = "cutoff"   # DLS hit the depth limit somewhere (maybe a deeper solution exists)


def make_child(problem, node, action):
  """Child node (same as Node.child_node, but without the debug print)."""
  next_state = problem.result(node.state, action)
  return Node(next_state, node, action,
              problem.path_cost(node.path_cost, node.state, action, next_state))


def UniformCostSearchAgentProgram():
  """Uniform-Cost Search = Best-First Search with f(n) = g(n) = path cost.

  The frontier is a priority queue ordered by path cost, so the
  cheapest node is always expanded next."""

  def f(node):
    return node.path_cost          # g(n)

  def program(problem):
    counter = itertools.count()    # tie-breaker: equal costs -> first in, first out
    node = Node(problem.initial)
    frontier = [(f(node), next(counter), node)]
    reached = {problem.initial: node}
    expanded = 0

    while frontier:
      _, _, node = heapq.heappop(frontier)
      if problem.goal_test(node.state):          # goal test when the node is EXPANDED
        print("UCS: expanded {} nodes, path cost {}".format(expanded, node.path_cost))
        program.expanded = expanded
        return node
      expanded += 1
      for action in problem.actions(node.state):
        child = make_child(problem, node, action)
        s = child.state
        if s not in reached or child.path_cost < reached[s].path_cost:
          reached[s] = child
          heapq.heappush(frontier, (f(child), next(counter), child))

    print("UCS: expanded {} nodes, no solution".format(expanded))
    program.expanded = expanded
    return None

  program.expanded = 0
  return program


def is_cycle(node):
  """True if node's state already appears earlier on its own path."""
  state, p = node.state, node.parent
  while p is not None:
    if p.state == state:
      return True
    p = p.parent
  return False


def DepthLimitedSearch(problem, limit, counter=None):
  """DEPTH-LIMITED-SEARCH(problem, limit): returns a goal node, CUTOFF, or None (failure).
  States already on the current path are skipped (no going round in circles)."""
  counter = counter if counter is not None else {"expanded": 0}

  def recursive_dls(node):
    if problem.goal_test(node.state):
      return node
    if node.depth == limit:
      return CUTOFF
    counter["expanded"] += 1
    cutoff_occurred = False
    for action in problem.actions(node.state):
      child = make_child(problem, node, action)
      if is_cycle(child):
        continue
      result = recursive_dls(child)
      if isinstance(result, str) and result == CUTOFF:
        cutoff_occurred = True
      elif result is not None:
        return result
    return CUTOFF if cutoff_occurred else None

  return recursive_dls(Node(problem.initial))


def IDSearchAgentProgram():
  """ITERATIVE-DEEPENING-SEARCH(problem):
  for depth = 0, 1, 2, ... run DLS from the SAME initial state;
  stop when DLS returns a solution or a failure (not a cutoff)."""

  def program(problem):
    counter = {"expanded": 0}
    for depth in itertools.count():
      result = DepthLimitedSearch(problem, depth, counter)
      if isinstance(result, str) and result == CUTOFF:
        print("IDS: depth limit {} -> cutoff, try deeper".format(depth))
        continue
      program.expanded = counter["expanded"]
      program.depth = depth
      if result is None:
        print("IDS: depth limit {} -> failure: no solution exists".format(depth))
      else:
        print("IDS: depth limit {} -> SOLUTION found (expanded {} nodes in total)".format(
            depth, counter["expanded"]))
      return result

  program.expanded = 0
  program.depth = None
  return program
