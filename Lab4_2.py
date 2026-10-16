# Lab4 Task2: UCS Robot vs Iterative Deepening Robot

from src.nodeClass import Node

from lab4_1 import (
    makeLaboratory,
    LaboratoryEnvironment,
    RescueRobot,
    ACTION_NAMES
)


# UCS always chooses the node with the lowest total cost.
def UCSAgentProgram(problem):
    frontier = [Node(problem.initial)]
    visited = []

    while frontier:
        # Put the cheapest node first.
        frontier.sort(key=lambda node: node.path_cost)
        node = frontier.pop(0)

        if node.state in visited:
            continue

        if problem.goal_test(node.state):
            return node

        visited.append(node.state)

        for child in node.expand(problem):
            if child.state not in visited:
                frontier.append(child)

    return None


# Search only as far as the given depth limit.
def depthLimitedSearch(problem, node, limit, path):
    if problem.goal_test(node.state):
        return node

    if limit == 0:
        return None

    for child in node.expand(problem):
        # Do not revisit a cell already on this route.
        if child.state not in path:
            result = depthLimitedSearch(
                problem,
                child,
                limit - 1,
                path + [child.state]
            )

            if result is not None:
                return result

    return None


# Try depth limits 0, 1, 2, and so on.
def IDSearchAgentProgram(problem):
    problem.depth_limits = []

    # A route without repeated cells uses at most N - 1 moves.
    number_of_cells = len(problem.graph.nodes())

    for limit in range(number_of_cells):
        problem.depth_limits.append(limit)

        result = depthLimitedSearch(
            problem,
            Node(problem.initial),
            limit,
            [problem.initial]
        )

        if result is not None:
            return result

    return None


def displayPlan(robot):
    print("\nAgent:", robot.name)

    if robot.name == "IDDFS":
        print("Depth limits:", robot.problem.depth_limits)

    if robot.solution_node is None:
        print("No route exists.")
        return

    print("Planned actions:")

    for action in robot.action_sequence:
        print(action, "-", ACTION_NAMES[action])

    print("Number of moves:", len(robot.action_sequence))
    print("Total planned cost:", robot.solution_node.path_cost)


def displayResult(robot):
    print("\nAgent:", robot.name)
    print("Status:", robot.status)
    print("Final location:", robot.location)
    print("Moves made:", robot.moves)
    print("Total movement cost:", robot.path_cost)
    print("Remaining energy:", round(robot.performance, 2))
    print("Final state:", robot.state)
    print("Discovered drones:", robot.known_drones)
    print("Visited cells:", robot.visited)


def determineWinner(ucs_robot, ids_robot):
    print("\nWINNER")

    ucs_success = ucs_robot.status == "Rescued"
    ids_success = ids_robot.status == "Rescued"

    if ucs_success and ids_success:
        if ucs_robot.performance > ids_robot.performance:
            print("UCS wins: it has more energy remaining.")
        elif ids_robot.performance > ucs_robot.performance:
            print("IDDFS wins: it has more energy remaining.")
        else:
            print("Tie: both have the same energy remaining.")

    elif ucs_success:
        print("UCS wins: only UCS reached the target.")

    elif ids_success:
        print("IDDFS wins: only IDDFS reached the target.")

    else:
        print("No winner: neither robot reached the target.")


def main():
    # Both robots use the same laboratory.
    maze, start, goal = makeLaboratory()
    environment = LaboratoryEnvironment(maze, start, goal)

    print("LAB4 TASK2")
    print("0 = free, 1 = wall, 2 = drone, 3 = target, 4 = start")
    print(maze)
    print("\nStarting position:", start)
    print("Rescue target:", goal)

    starting_energy = 100

    ucs_robot = RescueRobot(
        "UCS",
        start,
        goal,
        environment.graph,
        UCSAgentProgram,
        starting_energy
    )

    ids_robot = RescueRobot(
        "IDDFS",
        start,
        goal,
        environment.graph,
        IDSearchAgentProgram,
        starting_energy
    )

    environment.add_thing(ucs_robot)
    environment.add_thing(ids_robot)

    displayPlan(ucs_robot)
    displayPlan(ids_robot)

    print("\nEXECUTING THE PLANNED ROUTES")
    environment.run()

    print("\nFINAL RESULTS")
    displayResult(ucs_robot)
    displayResult(ids_robot)

    determineWinner(ucs_robot, ids_robot)


if __name__ == "__main__":
    main()