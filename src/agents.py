# for the Assignment3

from src.PS_agentPrograms import *
from src.vacuumProblemSolvingAgentSMARTClass import VacuumProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
from src.navProblemSolvingAgentClass import navProblemSolvingAgent
from src.mazeProblemSolvingAgentClass import MazeProblemSolvingAgent
from src.mazeAgentPrograms import BreadthFirstSearchAgentProgram
from data.mazeData import TREASURES, START, FINISH, START_HEADING

def ProblemSolvingVacuumAgentBFS(initState,vacuumWorldGraph,goalState):
    return VacuumProblemSolvingAgentSMART(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgram())

 
def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
    return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())


# ---------------- Lab3 Task: Treasure Maze ----------------
ALL_TREASURES = tuple(sorted(TREASURES.keys()))

def MazeAgentBasic(mazeGraph, directions):
    # Basic: reach the finish
    goal = [(FINISH, ())]
    return MazeProblemSolvingAgent(START, mazeGraph, directions, goal, BreadthFirstSearchAgentProgram(), START_HEADING)

def MazeAgentAllTreasures(mazeGraph, directions):
    # Treasure collection: collect ALL treasures and reach the finish
    goal = [(FINISH, ALL_TREASURES)]
    return MazeProblemSolvingAgent(START, mazeGraph, directions, goal, BreadthFirstSearchAgentProgram(), START_HEADING)

def MazeAgentSpecificTreasure(mazeGraph, directions, treasure):
    # Specific treasure: find a particular treasure, then redefine the goal: reach the finish
    goal = [(None, (treasure,)), (FINISH, (treasure,))]
    return MazeProblemSolvingAgent(START, mazeGraph, directions, goal, BreadthFirstSearchAgentProgram(), START_HEADING)
