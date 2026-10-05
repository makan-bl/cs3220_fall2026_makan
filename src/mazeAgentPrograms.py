# Uninformed search for the Treasure Maze
from collections import deque
from src.nodeClass import Node


def BreadthFirstSearchAgentProgram():
    """Breadth-first (uninformed) graph search: expands the shallowest node first,
    so the solution found uses the fewest actions (every action costs 1)."""

    def program(problem):
        node = Node(problem.initial)
        if problem.goal_test(node.state):
            return node
        frontier = deque([node])          # FIFO queue
        reached = {problem.initial}
        expanded = 0
        while frontier:
            node = frontier.popleft()
            expanded += 1
            for child in node.expand(problem):
                if child.state not in reached:
                    if problem.goal_test(child.state):
                        print("BFS expanded {} nodes, solution depth {}".format(expanded, child.depth))
                        return child
                    reached.add(child.state)
                    frontier.append(child)
        print("BFS expanded {} nodes, no solution".format(expanded))
        return None

    return program
