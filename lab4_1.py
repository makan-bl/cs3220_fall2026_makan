#Lab4 Task1: Rescue Robot in a Hazardous Laboratory Maze

import random
import math
import numpy as np

from src.thingClass import Thing
from src.agentClass import Agent
from src.environmentClass import Environment
from src.problemClass import Problem


#cell types
FREE = 0
WALL = 1
DRONE = 2
TARGET = 3
START = 4


#integer actions and their names
ACTION_NAMES = {
    0: "Left",
    1: "Up",
    2: "Right",
    3: "Down"
}


#changes to row and column
MOVEMENTS = {
    0: (0, -1),   #Left
    1: (-1, 0),   #Up
    2: (0, 1),    #Right
    3: (1, 0)     #Down
}


#action costs required in Task2
ACTION_COSTS = {
    0: 2,
    1: 4,
    2: 2,
    3: 1
}


#generate the random laboratory
def makeLaboratory():

    maze = np.zeros((7, 7), dtype=int)

    cells = []

    for row in range(7):
        for column in range(7):
            cells.append((row, column))

    random.shuffle(cells)

    #49 cells: approximately 25% walls and 10% drones
    wall_count = round(49 * 0.25)
    drone_count = round(49 * 0.10)

    #place walls
    for index in range(wall_count):
        row, column = cells[index]
        maze[row, column] = WALL

    #place drones in different cells
    for index in range(wall_count, wall_count + drone_count):
        row, column = cells[index]
        maze[row, column] = DRONE

    #select two different remaining free cells
    start = cells[wall_count + drone_count]
    goal = cells[wall_count + drone_count + 1]

    maze[start] = START
    maze[goal] = TARGET

    return maze, start, goal


#build the transition model
#format: state -> action -> next state
def makeTransitionModel(maze):

    model = {}

    size = len(maze)

    for row in range(size):

        for column in range(size):

            #walls do not become graph nodes
            if maze[row, column] == WALL:
                continue

            state = (row, column)

            #include open cells even if they have no neighbours
            model[state] = {}

            for action in range(4):

                change_row, change_column = MOVEMENTS[action]

                next_row = row + change_row
                next_column = column + change_column

                #check laboratory boundaries
                if 0 <= next_row < size and 0 <= next_column < size:

                    #the robot cannot enter a wall
                    if maze[next_row, next_column] != WALL:

                        next_state = (next_row, next_column)

                        model[state][action] = next_state

    return model


#graph of traversable laboratory cells
class LaboratoryGraph:

    def __init__(self, transition_model):

        self.origin = transition_model
        self.graph_dict = {}

        for state in transition_model:

            self.graph_dict[state] = {}

            for action in transition_model[state]:

                next_state = transition_model[state][action]

                self.graph_dict[state][next_state] = ACTION_COSTS[action]

    def nodes(self):

        return list(self.origin.keys())


#each security drone is a Thing
class SecurityDrone(Thing):

    def __init__(self, location, attack_power):

        self.location = location
        self.attack_power = attack_power


#problem used by the search algorithms
class LaboratoryProblem(Problem):

    def __init__(self, initial, goal, graph):

        super().__init__(initial, goal)

        self.graph = graph
        self.depth_limits = []

    def actions(self, state):

        return list(self.graph.origin[state].keys())

    def result(self, state, action):

        return self.graph.origin[state][action]

    def path_cost(self, cost_so_far, state, action, next_state):

        return cost_so_far + ACTION_COSTS[action]


#rescue robot
class RescueRobot(Agent):

    def __init__(self, name, start, goal, graph, search_program,
                 starting_energy=100):

        super().__init__(search_program)

        self.name = name

        self.location = start
        self.goal = goal

        self.performance = float(starting_energy)

        #execution state includes location and remaining energy
        self.state = (self.location, self.performance)

        self.known_drones = {}

        self.path_cost = 0
        self.moves = 0

        self.visited = [start]

        self.status = "Ready"

        #the graph contains movement connections, not drone locations
        self.problem = LaboratoryProblem(start, goal, graph)

        self.solution_node = self.program(self.problem)

        self.action_sequence = []
        self.action_index = 0

        if self.solution_node is None:

            self.status = "No route"

        else:

            self.action_sequence = self.solution_node.solution()

            if start == goal:
                self.status = "Rescued"

    def defensive_capability(self):

        #assumption: defense equals current energy
        return self.performance


#laboratory environment
class LaboratoryEnvironment(Environment):

    def __init__(self, maze, start, goal):

        super().__init__()

        self.maze = maze

        self.start = start
        self.goal = goal

        self.transition_model = makeTransitionModel(maze)

        self.graph = LaboratoryGraph(self.transition_model)

        self.drones = {}

        number_of_nodes = len(self.graph.nodes())

        #integer attack powers within the specified range
        minimum_power = math.ceil(number_of_nodes * 0.10)
        maximum_power = math.floor(number_of_nodes * 0.40)

        for row in range(len(maze)):

            for column in range(len(maze)):

                if maze[row, column] == DRONE:

                    location = (row, column)

                    attack_power = random.randint(
                        minimum_power,
                        maximum_power
                    )

                    self.drones[location] = SecurityDrone(
                        location,
                        attack_power
                    )

    def add_thing(self, robot, location=None):

        if robot not in self.agents:
            self.agents.append(robot)

    def percept(self, robot):

        return robot.state

    def execute_action(self, robot, action):

        available_actions = self.transition_model[robot.location]

        #check that the action is legal
        if action not in available_actions:

            print(robot.name, "cannot perform this action.")
            return

        #move the robot
        robot.location = available_actions[action]

        robot.moves += 1
        robot.path_cost += ACTION_COSTS[action]

        robot.visited.append(robot.location)

        print(
            robot.name,
            "moves",
            ACTION_NAMES[action],
            "to",
            robot.location
        )

        #the robot discovers a drone only after entering its cell
        if robot.location in self.drones:

            drone = self.drones[robot.location]

            robot.known_drones[robot.location] = drone.attack_power

            print("Drone attack power:", drone.attack_power)

            #at least twice the current defensive capability
            if drone.attack_power >= 2 * robot.defensive_capability():

                robot.alive = False
                robot.status = "Captured"

                print(robot.name, "was captured.")

            else:

                #Defense Mode consumes 10% of current energy
                robot.performance = robot.performance * 0.90

                print(
                    robot.name,
                    "activates Defense Mode.",
                    "Energy:",
                    round(robot.performance, 2)
                )

        #update the complete execution state
        robot.state = (robot.location, robot.performance)

        #a captured robot cannot complete the mission
        if robot.alive and robot.location == robot.goal:

            robot.status = "Rescued"

            print(robot.name, "reached the rescue target.")

    def step(self):

        #each active robot makes one move
        for robot in self.agents:

            if robot.alive and robot.status in ["Ready", "Moving"]:

                if robot.action_index < len(robot.action_sequence):

                    robot.status = "Moving"

                    action = robot.action_sequence[robot.action_index]

                    robot.action_index += 1

                    self.execute_action(robot, action)

                else:

                    robot.status = "No route"

    def is_done(self):

        for robot in self.agents:

            if robot.alive and robot.status in ["Ready", "Moving"]:
                return False

        return True

    def run(self, steps=None):

        step_number = 0

        while not self.is_done():

            if steps is not None and step_number >= steps:
                break

            step_number += 1

            print("\nStep", step_number)

            self.step()


#display Task1 laboratory information
def main():

    maze, start, goal = makeLaboratory()

    environment = LaboratoryEnvironment(maze, start, goal)

    print("LAB4 TASK1")
    print("0 = free, 1 = wall, 2 = drone, 3 = target, 4 = start")

    print(maze)

    print("\nStarting position:", start)
    print("Rescue target:", goal)

    print("\nTransition model:")

    for state in environment.transition_model:
        print(state, ":", environment.transition_model[state])

    print("\nNumber of graph nodes:", len(environment.graph.nodes()))

    print("\nSecurity drones:")

    for location in environment.drones:

        drone = environment.drones[location]

        print(
            "Location:",
            location,
            "Attack power:",
            drone.attack_power
        )


if __name__ == "__main__":
    main()