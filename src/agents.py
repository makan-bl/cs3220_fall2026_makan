# for the Assignment3

from src.PS_agentPrograms import *
from src.mazeProblemSolvingAgentSMARTClass import MazeProblemSolvingAgentSMART



from src.vacuumProblemSolvingAgentSMARTClass import VacuumProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
from src.navProblemSolvingAgentClass import navProblemSolvingAgent


def ProblemSolvingMazeAgentBFS(initState,mazeWorldGraph,goalState):
    return MazeProblemSolvingAgentSMART(initState,mazeWorldGraph,goalState,BestFirstSearchAgentProgram())


def ProblemSolvingVacuumAgentBFS(initState,vacuumWorldGraph,goalState):
    return VacuumProblemSolvingAgentSMART(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgram())

 
def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
    return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())

# ---- Lab 4: Rescue Robot agents ----
from src.rescueRobotAgentClass import RescueRobotAgent


def RescueRobotUCS(initState, labWorldGraph, goalState, name="UCS-Robot"):
    return RescueRobotAgent(name, initState, labWorldGraph, goalState, UniformCostSearchAgentProgram())


def RescueRobotIDS(initState, labWorldGraph, goalState, name="IDS-Robot"):
    return RescueRobotAgent(name, initState, labWorldGraph, goalState, IDSearchAgentProgram())
