# Streamlit app for Lab4 Task1: Rescue Robot in a Hazardous Laboratory Maze

import io
import contextlib

import streamlit as st

from lab4_1 import (
    makeLaboratory,
    LaboratoryEnvironment,
    FREE,
    WALL,
    DRONE,
    TARGET,
    START,
)


# colour and label for each cell type
CELL_STYLE = {
    FREE: ("#f4f4f4", ""),
    WALL: ("#3a3a3a", ""),
    DRONE: ("#e4572e", "D"),
    TARGET: ("#2e9e5b", "T"),
    START: ("#2f6fd6", "S"),
}


def drawMaze(maze):
    html = "<table style='border-collapse:collapse;margin:auto'>"

    # column numbers
    html += "<tr><td></td>"
    for column in range(len(maze)):
        html += f"<td style='text-align:center;font-size:12px'>{column}</td>"
    html += "</tr>"

    for row in range(len(maze)):
        html += f"<tr><td style='padding-right:6px;font-size:12px'>{row}</td>"

        for column in range(len(maze)):
            colour, label = CELL_STYLE[int(maze[row, column])]
            text_colour = "#000" if label == "" else "#fff"

            html += (
                f"<td style='width:44px;height:44px;background:{colour};"
                f"border:1px solid #999;text-align:center;font-weight:bold;"
                f"color:{text_colour}'>{label}</td>"
            )

        html += "</tr>"

    html += "</table>"
    return html


def newLaboratory():
    maze, start, goal = makeLaboratory()
    st.session_state.maze = maze
    st.session_state.start = start
    st.session_state.goal = goal
    st.session_state.environment = LaboratoryEnvironment(maze, start, goal)


st.set_page_config(page_title="Lab4 Task1", layout="centered")

st.title("Lab4 Task1: Rescue Robot Laboratory")
st.write("A random 7 x 7 laboratory with about 25% walls and 10% security drones.")

if st.button("Generate new laboratory") or "maze" not in st.session_state:
    newLaboratory()

maze = st.session_state.maze
environment = st.session_state.environment

st.subheader("Laboratory")
st.markdown(drawMaze(maze), unsafe_allow_html=True)
st.caption("S = start, T = rescue target, D = security drone, dark = wall")

st.write("**Starting position:**", st.session_state.start)
st.write("**Rescue target:**", st.session_state.goal)
st.write("**Number of graph nodes:**", len(environment.graph.nodes()))

st.subheader("Numeric maze")
st.caption("0 = free, 1 = wall, 2 = drone, 3 = target, 4 = start")
st.dataframe(maze)

st.subheader("Security drones")
drone_rows = []
for location in environment.drones:
    drone_rows.append({
        "Location": str(location),
        "Attack power": environment.drones[location].attack_power,
    })
st.table(drone_rows)

st.subheader("Transition model")
st.caption("state -> {action: next state}   (0 = Left, 1 = Up, 2 = Right, 3 = Down)")
output = io.StringIO()
with contextlib.redirect_stdout(output):
    for state in environment.transition_model:
        print(state, ":", environment.transition_model[state])
st.code(output.getvalue(), language=None)
