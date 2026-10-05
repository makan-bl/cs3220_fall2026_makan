from src.problemClass import Problem

# relative turns for an agent facing a direction
LEFT_OF = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
RIGHT_OF = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
ACTION_ORDER = ['advance', 'left', 'right']


def relative_turn(heading, direction):
    """Which way the agent has to go (relative to its heading) to leave in `direction`."""
    if direction == heading:
        return 'advance'
    if direction == LEFT_OF[heading]:
        return 'left'
    if direction == RIGHT_OF[heading]:
        return 'right'
    return 'back'


def maze_moves(graph, directions, node, heading):
    """{action: neighbour} available at `node` for an agent facing `heading`.
    Actions are only advance / left / right. Going back is only possible at a dead end
    (a node with one corridor): there the agent turns around and then advances."""
    moves = {}
    dead_end = len(graph.get(node)) == 1
    for neighbour in graph.get(node):
        rel = relative_turn(heading, directions[(node, neighbour)][0])
        if rel == 'back':
            if not dead_end:
                continue
            rel = 'advance'
        moves[rel] = neighbour
    return {a: moves[a] for a in ACTION_ORDER if a in moves}


class MazeProblem(Problem):
    """The Treasure Maze problem.

    state = (node, heading, collected)
        node      - where the agent is ('S', 'A', ..., 'F')
        heading   - which way it is facing ('N', 'S', 'E', 'W')
        collected - tuple (sorted) of the treasure names collected so far

    goal = (goalNode, requiredTreasures)
        goalNode          - node to reach, or None (= anywhere)
        requiredTreasures - tuple of treasure names that must be collected
    """

    def __init__(self, initial, goal, graph, directions, treasures=None):
        super().__init__(initial, goal)
        self.graph = graph              # the state space (a Graph object built from mazeData)
        self.directions = directions    # mazeDirections
        self.treasures = treasures or {}  # {node: treasure name} the agent cares about

    def actions(self, state):
        node, heading, collected = state
        return list(maze_moves(self.graph, self.directions, node, heading).keys())

    def result(self, state, action):
        node, heading, collected = state
        neighbour = maze_moves(self.graph, self.directions, node, heading)[action]
        new_heading = self.directions[(node, neighbour)][1]
        treasure = self.treasures.get(neighbour)
        if treasure and treasure not in collected:
            collected = tuple(sorted(collected + (treasure,)))
        return (neighbour, new_heading, collected)

    def goal_test(self, state):
        node, heading, collected = state
        goal_node, required = self.goal
        at_goal_node = goal_node is None or node == goal_node
        return at_goal_node and all(t in collected for t in required)

    def path_cost(self, c, state1, action, state2):
        return c + 1   # every executed action costs 1
