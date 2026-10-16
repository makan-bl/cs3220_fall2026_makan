# Streamlit app for Lab4 Task2: UCS Robot vs Iterative Deepening Robot

import io
import contextlib

import streamlit as st

from lab4_1 import (
    makeLaboratory,
    LaboratoryEnvironment,
    RescueRobot,
    FREE,
    WALL,
    DRONE,
    TARGET,
    START,
)

from Lab4_2 import (
    UCSAgentProgram,
    IDSearchAgentProgram,
    displayPlan,
    displayResult,
    determineWinner,
)


# colour and label for each cell type
CELL_STYLE = {
    FREE: ("#f4f4f4", ""),
    WALL: ("#3a3a3a", ""),
    DRONE: ("#e4572e", "D"),
    TARGET: ("#2e9e5b", "T"),
    START: ("#2f6fd6", "S"),
}

PATH_COLOUR = "#f2c94c"


# capture everything a function prints so Streamlit can show it
def captureOutput(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        function(*arguments)
    return output.getvalue()


# list of cells the robot actually walked through, with step numbers
def pathSteps(visited):
    steps = {}
    for number, cell in enumerate(visited):
        if number > 0 and cell not in steps:
            steps[cell] = number
    return steps


def drawMaze(maze, steps=None):
    if steps is None:
        steps = {}

    html = "<table style='border-collapse:collapse;margin:auto'>"

    html += "<tr><td></td>"
    for column in range(len(maze)):
        html += f"<td style='text-align:center;font-size:12px'>{column}</td>"
    html += "</tr>"

    for row in range(len(maze)):
        html += f"<tr><td style='padding-right:6px;font-size:12px'>{row}</td>"

        for column in range(len(maze)):
            cell_type = int(maze[row, column])
            colour, label = CELL_STYLE[cell_type]
            text_colour = "#fff"

            # mark free cells on the robot's route with the step number
            if (row, column) in steps and cell_type == FREE:
                colour = PATH_COLOUR
                label = str(steps[(row, column)])
                text_colour = "#000"

            # drone on the route: keep it red, show the step number too
            elif (row, column) in steps and cell_type == DRONE:
                label = "D" + str(steps[(row, column)])

            html += (
                f"<td style='width:40px;height:40px;background:{colour};"
                f"border:1px solid #999;text-align:center;font-weight:bold;"
                f"font-size:13px;color:{text_colour}'>{label}</td>"
            )

        html += "</tr>"

    html += "</table>"
    return html


def runCompetition():
    # both robots use the same laboratory
    maze, start, goal = makeLaboratory()
    environment = LaboratoryEnvironment(maze, start, goal)

    starting_energy = 100

    ucs_robot = RescueRobot(
        "UCS", start, goal, environment.graph,
        UCSAgentProgram, starting_energy
    )

    ids_robot = RescueRobot(
        "IDDFS", start, goal, environment.graph,
        IDSearchAgentProgram, starting_energy
    )

    environment.add_thing(ucs_robot)
    environment.add_thing(ids_robot)

    plans = captureOutput(displayPlan, ucs_robot)
    plans += captureOutput(displayPlan, ids_robot)

    execution = captureOutput(environment.run)

    results = captureOutput(displayResult, ucs_robot)
    results += captureOutput(displayResult, ids_robot)

    winner = captureOutput(determineWinner, ucs_robot, ids_robot)

    drone_rows = []
    for location in environment.drones:
        drone_rows.append({
            "Location": str(location),
            "Attack power": environment.drones[location].attack_power,
        })

    st.session_state.result = {
        "maze": maze,
        "start": start,
        "goal": goal,
        "drones": drone_rows,
        "ucs_steps": pathSteps(ucs_robot.visited),
        "ids_steps": pathSteps(ids_robot.visited),
        "ucs_status": ucs_robot.status,
        "ids_status": ids_robot.status,
        "ucs_energy": round(ucs_robot.performance, 2),
        "ids_energy": round(ids_robot.performance, 2),
        "ucs_cost": ucs_robot.path_cost,
        "ids_cost": ids_robot.path_cost,
        "plans": plans,
        "execution": execution,
        "results": results,
        "winner": winner,
    }


st.set_page_config(page_title="Lab4 Task2", layout="wide")

st.title("Lab4 Task2: UCS Robot vs Iterative Deepening Robot")
st.write(
    "Both robots start with 100 energy in the same random laboratory. "
    "Move costs: Left = 2, Up = 4, Right = 2, Down = 1."
)

if st.button("Run a new competition") or "result" not in st.session_state:
    with st.spinner("Generating laboratory and planning routes..."):
        runCompetition()

result = st.session_state.result

st.write("**Starting position:**", result["start"],
         "  **Rescue target:**", result["goal"])

st.subheader("Laboratory")
st.markdown(drawMaze(result["maze"]), unsafe_allow_html=True)
st.caption("S = start, T = rescue target, D = security drone, dark = wall")

st.subheader("Routes taken")
st.caption("Yellow numbers show the order of the robot's moves. D3 = drone met on move 3.")

left, right = st.columns(2)

with left:
    st.markdown("### UCS")
    st.markdown(drawMaze(result["maze"], result["ucs_steps"]), unsafe_allow_html=True)
    st.metric("Status", result["ucs_status"])
    st.metric("Remaining energy", result["ucs_energy"])
    st.metric("Total movement cost", result["ucs_cost"])

with right:
    st.markdown("### IDDFS")
    st.markdown(drawMaze(result["maze"], result["ids_steps"]), unsafe_allow_html=True)
    st.metric("Status", result["ids_status"])
    st.metric("Remaining energy", result["ids_energy"])
    st.metric("Total movement cost", result["ids_cost"])

st.subheader("Winner")
st.success(result["winner"].replace("WINNER", "").strip())

st.subheader("Security drones")
st.table(result["drones"])

st.subheader("Planned routes")
st.code(result["plans"].strip(), language=None)

st.subheader("Step-by-step execution")
st.code(result["execution"].strip(), language=None)

st.subheader("Final results")
st.code(result["results"].strip(), language=None)

st.subheader("Numeric maze")
st.caption("0 = free, 1 = wall, 2 = drone, 3 = target, 4 = start")
st.dataframe(result["maze"])
