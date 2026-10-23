#Lab5: Informed Search in PacMan World

import math
import random
import numpy as np

from pathlib import Path
from queue import PriorityQueue

from src.nodeClass import Node

from src.mazeData import (
    makeMaze,
    defineMazeAvailableActions,
    makeMazeTransformationModel,
    mazeStatesLocations
)

from src.maze2025GraphClass import mazeGraph
from src.mazeProblemClass import MazeProblem

from src.mazeProblemSolvingAgentSMARTClass import (
    MazeProblemSolvingAgentSMART
)

from src.naigationEnvironmentClass import (
    MazeNavigationEnvironment
)


#create the base class for objects in the maze
class Thing:

    def __init__(self, location):

        self.location = location


#find a route using A*
def A_StarSearchAgentProgram(f=math.dist):

    def program(problem):

        node = Node(problem.initial)

        frontier = PriorityQueue()
        frontier.put((f(node.state, problem.goal), node))

        reached = {problem.initial: node}

        problem.expanded = 0
        problem.total_cost = math.inf

        while not frontier.empty():

            node = frontier.get()[1]

            if node.path_cost > reached[node.state].path_cost:
                continue

            if problem.goal_test(node.state):

                problem.total_cost = node.path_cost
                return node

            problem.expanded += 1

            for child in node.expand(problem):

                if child.state not in reached:

                    reached[child.state] = child

                    value = (
                        child.path_cost
                        + f(child.state, problem.goal)
                    )

                    frontier.put((value, child))

                elif child.path_cost < reached[child.state].path_cost:

                    reached[child.state] = child

                    value = (
                        child.path_cost
                        + f(child.state, problem.goal)
                    )

                    frontier.put((value, child))

        return None

    return program


#find the node with the smallest f value
def lowest_f_node(nodes):

    best = nodes[0]

    for node in nodes:

        if node.f < best.f:
            best = node

    return best


#search within the current cost limit
def IDA_visit(problem, node, f, limit, visited):

    value = node.path_cost + f(node.state, problem.goal)

    if value > limit:
        return None, value

    if problem.goal_test(node.state):
        return node, value

    problem.expanded += 1

    next_limit = math.inf
    children = []

    for child in node.expand(problem):

        if child.state not in visited:

            child.f = (
                child.path_cost
                + f(child.state, problem.goal)
            )

            children.append(child)

    while len(children) > 0:

        child = lowest_f_node(children)
        children.remove(child)

        visited.append(child.state)

        solution, exceeded = IDA_visit(
            problem,
            child,
            f,
            limit,
            visited
        )

        visited.pop()

        if solution is not None:
            return solution, exceeded

        next_limit = min(next_limit, exceeded)

    return None, next_limit


#increase the cost limit until a route is found
def IDA_StarSearchAgentProgram(f=math.dist):

    def program(problem):

        node = Node(problem.initial)

        problem.expanded = 0
        problem.total_cost = math.inf

        limit = f(node.state, problem.goal)

        while limit < math.inf:

            solution, limit = IDA_visit(
                problem,
                node,
                f,
                limit,
                [node.state]
            )

            if solution is not None:

                problem.total_cost = solution.path_cost
                return solution

        return None

    return program


#follow the best branch and remember the alternatives
def RBFS_visit(problem, node, f, limit, visited):

    if problem.goal_test(node.state):
        return node, node.f

    problem.expanded += 1

    children = []

    for child in node.expand(problem):

        if child.state not in visited:

            child.f = max(
                child.path_cost + f(child.state, problem.goal),
                node.f
            )

            children.append(child)

    if len(children) == 0:
        return None, math.inf

    while True:

        best = lowest_f_node(children)

        if best.f == math.inf or best.f > limit:
            return None, best.f

        alternative = math.inf

        for child in children:

            if child is not best and child.f < alternative:
                alternative = child.f

        visited.append(best.state)

        solution, new_f = RBFS_visit(
            problem,
            best,
            f,
            min(limit, alternative),
            visited
        )

        visited.pop()

        best.f = new_f

        if solution is not None:
            return solution, best.f


#find a route using recursive best-first search
def RBFSearchAgentProgram(f=math.dist):

    def program(problem):

        node = Node(problem.initial)
        node.f = f(node.state, problem.goal)

        problem.expanded = 0
        problem.total_cost = math.inf

        solution, unused = RBFS_visit(
            problem,
            node,
            f,
            math.inf,
            [node.state]
        )

        if solution is not None:
            problem.total_cost = solution.path_cost

        return solution

    return program


#calculate Manhattan distance
def manhattan(state, goal):

    row_difference = abs(state[0] - goal[0])
    column_difference = abs(state[1] - goal[1])

    return row_difference + column_difference


def make_world(n=10, seed=3220):

    if n < 5:
        raise ValueError("Use n >= 5")

    np.random.seed(seed)
    rng = random.Random(seed)

    start = (0, 0)
    finish = (n - 1, n - 1)

    #generate a maze with reachable paths
    for attempt in range(10000):

        maze = makeMaze(n)

        maze[start] = 1
        maze[finish] = 1

        spaces = []

        for r in range(n):

            for c in range(n):

                if maze[r, c] != 0:

                    maze[r, c] = 1
                    spaces.append((r, c))

        actions = defineMazeAvailableActions(maze)
        model = makeMazeTransformationModel(actions)

        visited = {start}
        waiting = [start]

        while len(waiting) > 0:

            state = waiting.pop()

            for action in model[state]:

                destination = model[state][action]

                if destination not in visited:

                    visited.add(destination)
                    waiting.append(destination)

        if len(visited) == len(spaces):
            break

    else:
        raise RuntimeError("Could not generate a connected maze")

    #place food in 5% of open cells
    food_count = max(
        1,
        int(len(spaces) * 0.05 + 0.5)
    )

    food = set(rng.sample(spaces, food_count))

    for position in food:
        maze[position] = 2

    locations = mazeStatesLocations(list(model.keys()))

    graph = mazeGraph(model, locations)

    #set each move to cost 1
    for state in model:

        for action in model[state]:

            destination = model[state][action]
            graph.connect(state, destination, 1)

    available = []

    for position in spaces:

        if position not in food:
            if position != start and position != finish:
                available.append(position)

    ghosts = []

    for position in rng.sample(available, 5):

        power = rng.uniform(
            len(spaces) * 0.2,
            len(spaces) * 0.3
        )

        ghosts.append(Ghost(position, power))

    return maze, graph, food, ghosts, start, finish


#create a ghost with a location and power
class Ghost(Thing):

    def __init__(self, location, power):

        super().__init__(location)

        self.power = power
        self.alive = True


#plan routes and handle food and ghosts
class PacManAgent(MazeProblemSolvingAgentSMART):

    def __init__(
        self,
        start,
        graph,
        finish,
        food,
        program,
        heuristic
    ):

        super().__init__(
            start,
            graph,
            finish,
            program
        )

        self.remaining_food = set(food)
        self.performance = len(graph.nodes()) * 0.4

        self.heuristic = heuristic
        self.status = "Running"

        self.route = [start]
        self.segments = []

        self.collected = []
        self.known_ghosts = set()
        self.events = []

        self.expanded = 0
        self.total_cost = 0

    def plan(self):

        if len(self.remaining_food) > 0:
            targets = sorted(self.remaining_food)

        else:
            targets = [self.goal]

        best = None
        food_estimate = math.inf

        for target in targets:

            #find the route to each food location
            problem = self.formulate_problem(
                self.state,
                target
            )

            node = self.program(problem)

            self.expanded += problem.expanded

            estimate = self.heuristic(
                self.state,
                target
            )

            food_estimate = min(
                food_estimate,
                estimate
            )

            if node is not None:

                if best is None:
                    best = node

                elif node.path_cost < best.path_cost:
                    best = node

        if best is None:

            self.status = "No route"
            self.alive = False

            return

        self.path = best.path()
        self.seq = self.actions_path(self.path)

        self.segments.append([self.state])

        self.events.append(
            f"Next goal: {best.state}; "
            f"cost: {best.path_cost}; "
            f"nearest-goal estimate: {food_estimate:.2f}"
        )

    def __call__(self, percept, curGoal=None):

        self.state = self.update_state(
            self.state,
            percept
        )

        if self.alive and len(self.seq) == 0:
            self.plan()

    def perceive(self, percept):

        state, has_food, ghost = percept

        self.state = state

        if has_food and state in self.remaining_food:

            self.remaining_food.remove(state)
            self.collected.append(state)

            self.performance *= 2

            self.events.append(
                f"Food at {state}: "
                f"performance {self.performance:.2f}"
            )

        if ghost is not None:

            self.known_ghosts.add(state)

            if self.performance > ghost.power:

                self.performance *= 0.9
                ghost.alive = False

                self.events.append(
                    f"Won against ghost at {state}: "
                    f"performance {self.performance:.2f}"
                )

            else:

                self.status = "Killed by ghost"
                self.alive = False

                self.events.append(
                    f"Lost against ghost at {state}"
                )

        if self.alive:

            if len(self.remaining_food) == 0:
                if state == self.goal:

                    self.status = "Success"
                    self.alive = False


#move the agent through the maze
class PacManEnvironment(MazeNavigationEnvironment):

    def __init__(self, graph, food, ghosts):

        super().__init__(graph)

        self.food = set(food)
        self.ghosts = {}

        for ghost in ghosts:

            self.ghosts[ghost.location] = Ghost(
                ghost.location,
                ghost.power
            )

    def percept(self, agent):

        ghost = self.ghosts.get(agent.state)

        if ghost is not None:

            if not ghost.alive:
                ghost = None

        has_food = agent.state in self.food

        return agent.state, has_food, ghost

    def inspect_cell(self, agent):

        agent.perceive(self.percept(agent))

        if agent.state not in agent.remaining_food:
            self.food.discard(agent.state)

    def add_thing(self, thing, location=None):

        self.inspect_cell(thing)

        super().add_thing(thing, location)

    def execute_action(self, agent, action):

        if not agent.alive:
            return

        old_state = agent.state

        destination = self.status.origin[old_state][action]

        agent.state = agent.update_state(
            old_state,
            destination
        )

        agent.total_cost += self.status.get(
            old_state,
            destination
        )

        agent.performance -= 1

        agent.route.append(agent.state)
        agent.segments[-1].append(agent.state)

        if agent.performance <= 0:

            agent.status = "Exhausted"
            agent.alive = False

        else:
            self.inspect_cell(agent)

    def step(self):

        for agent in self.agents:

            if agent.alive:

                if len(agent.seq) == 0:
                    agent(agent.state)

                if agent.alive and len(agent.seq) > 0:

                    action = agent.seq.pop(0)
                    self.execute_action(agent, action)


#display each route segment in a different color
def draw_paths(
    maze,
    food,
    ghosts,
    start,
    finish,
    agents,
    names
):

    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(12, 12)
    )

    axes = axes.flatten()

    for index in range(len(agents)):

        ax = axes[index]
        agent = agents[index]

        for r in range(maze.shape[0]):

            for c in range(maze.shape[1]):

                if maze[r, c] == 0:

                    wall = plt.Rectangle(
                        (c - 0.5, r - 0.5),
                        1,
                        1,
                        color="midnightblue"
                    )

                    ax.add_patch(wall)

        number = 0

        for segment in agent.segments:

            number += 1

            x = []
            y = []

            for r, c in segment:

                x.append(c)
                y.append(r)

            ax.plot(
                x,
                y,
                linewidth=2,
                label="Leg " + str(number)
            )

        for r, c in food:

            ax.plot(
                c,
                r,
                "o",
                color="gold",
                markeredgecolor="black"
            )

        for ghost in ghosts:

            r, c = ghost.location

            ax.text(
                c,
                r,
                "G",
                color="purple",
                ha="center",
                va="center"
            )

        ax.text(
            start[1],
            start[0],
            "S",
            color="blue",
            weight="bold"
        )

        ax.text(
            finish[1],
            finish[0],
            "E",
            color="green",
            weight="bold"
        )

        ax.set_xlim(
            -0.5,
            maze.shape[1] - 0.5
        )

        ax.set_ylim(
            maze.shape[0] - 0.5,
            -0.5
        )

        ax.set_aspect("equal")

        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

        ax.set_title(
            names[index] + "\n" + agent.status
        )

        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.13),
            ncol=3
        )

    figure.suptitle(
        "Lab 5: colored route segments\n"
        "Gold = food. "
        "G = ghost, revealed only for this report."
    )

    figure.tight_layout(
        rect=(0, 0, 1, 0.94)
    )

    output = Path(__file__).with_name(
        "lab5_paths.png"
    )

    figure.savefig(output, dpi=150)
    plt.close(figure)

    print("\nPicture saved:", output)


def main():

    maze, graph, food, ghosts, start, finish = make_world()

    print("LAB 5: INFORMED SEARCH")

    print("Space cells:", len(graph.nodes()))
    print("Food locations:", sorted(food))
    print("Ghost count:", len(ghosts))
    print("Movement cost: 1 per move")

    print("\nTASKS 1-2: start-to-exit comparison")

    heuristics = [
        math.dist,
        manhattan
    ]

    names = [
        "A* Euclidean",
        "A* Manhattan",
        "IDA* Manhattan",
        "RBFS Manhattan"
    ]

    for index in range(2):

        problem = MazeProblem(
            start,
            finish,
            graph
        )

        program = A_StarSearchAgentProgram(
            heuristics[index]
        )

        node = program(problem)

        print("\n", names[index])

        print("Expanded nodes:", problem.expanded)
        print("Path cost:", problem.total_cost)

        if node is not None:
            print("Actions:", node.solution())

    programs = [
        A_StarSearchAgentProgram(math.dist),
        A_StarSearchAgentProgram(manhattan),
        IDA_StarSearchAgentProgram(manhattan),
        RBFSearchAgentProgram(manhattan)
    ]

    heuristics = [
        math.dist,
        manhattan,
        manhattan,
        manhattan
    ]

    agents = []

    for index in range(4):

        print("\nTASKS 3-8:", names[index])

        agent = PacManAgent(
            start,
            graph,
            finish,
            food,
            programs[index],
            heuristics[index]
        )

        world = PacManEnvironment(
            graph,
            food,
            ghosts
        )

        world.add_thing(agent)
        world.run(steps=1000)

        agents.append(agent)

        for event in agent.events:
            print(event)

        print("Status:", agent.status)

        print(
            "Food collected:",
            len(agent.collected),
            "of",
            len(food)
        )

        print(
            "Moves:",
            len(agent.route) - 1
        )

        print(
            "Total path cost:",
            agent.total_cost
        )

        print(
            "Planning expansions:",
            agent.expanded
        )

        print(
            "Final performance:",
            round(agent.performance, 2)
        )

    print(
        "\nPlanning counts include comparisons "
        "to all candidate food targets."
    )

    print(
        "Cheapest-next-food selection is not "
        "a globally optimal tour."
    )

    draw_paths(
        maze,
        food,
        ghosts,
        start,
        finish,
        agents,
        names
    )


if __name__ == "__main__":
    main()