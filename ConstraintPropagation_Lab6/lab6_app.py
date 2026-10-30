# Lab 6. Constraint Propagation in solving CSPs
# Streamlit app for Task 1 (Vancouver tour) and Task 2 (Asterisk Sudoku)
# Based on the instructor's L6SimpleSudoku_example_v3.py
#
# Run locally:   streamlit run lab6_app.py

import io
import math
import contextlib

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # to display the HTML code
from pyvis.network import Network  # to create the graph as an interactive html object

from src.CSPclass import CSP
from src.algorithms import AC3


nodeColors = {
    "empty": "white",
    "filled": "yellow",
    "asterisk": "pink"
}


# ------------------------------------------------------------------
# Task 1 - Vancouver tour
# ------------------------------------------------------------------

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

attractions = ['Stanley Park', 'Granville Island', 'Vancouver Aquarium', 'Science World',
               'Gastown', 'Capilano Suspension Bridge', 'Canada Place']

requested = ['Vancouver Aquarium', 'Science World', 'Gastown']


def getTourCSP():
    # domains: all 7 days, except the two attractions with a fixed day
    tourDomains = {a: list(days) for a in attractions}
    tourDomains['Granville Island'] = ['Tue']
    tourDomains['Capilano Suspension Bridge'] = ['Wed']

    # neighbors: every attraction is constrained with every other attraction
    tourNeighbors = {a: [b for b in attractions if b != a] for a in attractions}

    # constraint: no 2 attractions can be visited on the same day
    tourConstraints = lambda X, x, Y, y: x != y

    return CSP(variables=None, domains=tourDomains, neighbors=tourNeighbors, constraints=tourConstraints)


def buildTourGraph(tourCSP, ac3=False):
    domainsDict = tourCSP.curr_domains if ac3 else tourCSP.domains

    net = Network(bgcolor="#242020", font_color="white", height="650px", width="100%",
                  cdn_resources="remote")

    for i, a in enumerate(attractions):
        # place the attractions on a circle so both graphs have the same layout
        x = 250 * math.cos(2 * math.pi * i / len(attractions))
        y = 250 * math.sin(2 * math.pi * i / len(attractions))
        color = nodeColors["filled"] if len(domainsDict[a]) == 1 else nodeColors["empty"]
        domainText = ", ".join(domainsDict[a])
        net.add_node(a, label=a + "\n" + domainText, title=domainText, color=color, size=15, x=x, y=y)

    for nodeFrom in tourCSP.neighbors:
        for nodeTo in tourCSP.neighbors[nodeFrom]:
            net.add_edge(nodeFrom, nodeTo, color="red")

    net.toggle_physics(False)
    components.html(net.generate_html(), height=680)


def task1():
    st.header("Task 1. Planning a Tour in Vancouver")
    st.write("Each attraction is a variable, its domain is the days it can be visited, "
             "and no 2 attractions can be visited on the same day ($X_i \\neq X_j$). "
             "Granville Island is fixed to **Tue** and Capilano Suspension Bridge to **Wed**.")

    if "tour_ac3" not in st.session_state:
        st.session_state["tour_ac3"] = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run AC-3", key="tour_run"):
            st.session_state["tour_ac3"] = True
    with col2:
        if st.button("Reset", key="tour_reset"):
            st.session_state["tour_ac3"] = False

    tourCSP = getTourCSP()
    ac3 = st.session_state["tour_ac3"]
    if ac3:
        with contextlib.redirect_stdout(io.StringIO()):  # AC3 prints every step; hide it
            result = AC3(tourCSP)
        st.success(f"AC-3 applied. Arc consistent: {result[0]}. Check the new domains.")

    # domains table (requested attractions first)
    rows = []
    for a in requested + [a for a in attractions if a not in requested]:
        row = {"Attraction": a + (" ⭐" if a in requested else ""),
               "Domain before AC-3": ", ".join(tourCSP.domains[a])}
        if ac3:
            row["Domain after AC-3"] = ", ".join(tourCSP.curr_domains[a])
        rows.append(row)
    st.caption("⭐ = attractions the task asks about")
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    tab1, tab2 = st.tabs(["Graph: original CSP", "Graph: after AC-3"])
    with tab1:
        buildTourGraph(tourCSP)
    with tab2:
        if ac3:
            buildTourGraph(tourCSP, ac3=True)
        else:
            st.info("Click **Run AC-3** to see this graph.")


# ------------------------------------------------------------------
# Task 2 - Asterisk Sudoku
# ------------------------------------------------------------------

rows = "ABCDEFGHI"
cols = "123456789"
cells = [r + c for r in rows for c in cols]

# the 9 shaded "asterisk" cells
asterisk = ['B5', 'C3', 'C7', 'E2', 'E5', 'E8', 'G3', 'G7', 'H5']

# the givens (start state of the puzzle)
filled = {'A2': 1, 'A8': 6,
          'B1': 3, 'B3': 9, 'B7': 1, 'B9': 5,
          'C2': 8, 'C4': 3, 'C6': 5, 'C8': 7,
          'D3': 2, 'D5': 7, 'D7': 8,
          'E4': 6, 'E6': 8,
          'F3': 8, 'F5': 9, 'F7': 2,
          'G2': 2, 'G4': 4, 'G6': 1, 'G8': 9,
          'H1': 9, 'H3': 4, 'H7': 6, 'H9': 1,
          'I2': 3, 'I8': 8}


def boxOf(cell):
    """Return which 3x3 region a cell is in, e.g. 'A1' -> (0, 0), 'E5' -> (1, 1)."""
    return (rows.index(cell[0]) // 3, (int(cell[1]) - 1) // 3)


def getAsteriskCSP():
    asteriskNeighbors = {}
    for c1 in cells:
        asteriskNeighbors[c1] = []
        for c2 in cells:
            if c1 == c2:
                continue
            sameRow = c1[0] == c2[0]
            sameCol = c1[1] == c2[1]
            sameBox = boxOf(c1) == boxOf(c2)
            bothAsterisk = c1 in asterisk and c2 in asterisk
            if sameRow or sameCol or sameBox or bothAsterisk:
                asteriskNeighbors[c1].append(c2)

    asteriskDomains = {var: [filled[var]] if var in filled else list(range(1, 10)) for var in cells}

    asteriskConstraints = lambda X, x, Y, y: x != y

    return CSP(variables=None, domains=asteriskDomains, neighbors=asteriskNeighbors, constraints=asteriskConstraints)


@st.cache_data
def runAsteriskAC3():
    """AC-3 on 81 cells takes a few seconds, so the result is cached."""
    asteriskCSP = getAsteriskCSP()
    with contextlib.redirect_stdout(io.StringIO()):  # AC3 prints every step; hide it
        result = AC3(asteriskCSP)
    return result, asteriskCSP.curr_domains


def drawGrid(domainsDict):
    """Show the 9x9 board as an HTML table. Each cell shows its domain."""
    html = """<style>
    .grid {border-collapse: collapse; margin: 8px 0;}
    .grid td {width: 54px; height: 54px; text-align: center; vertical-align: middle;
              border: 1px solid #999; color: #111; font-family: sans-serif; padding: 2px;}
    .grid td.given {background: #fff27a; font-size: 24px; font-weight: bold;}
    .grid td.ast {background: #f8c3cf;}
    .grid td.empty {background: #ffffff;}
    .grid td.small {font-size: 12px; line-height: 13px;}
    .grid td.solved {font-size: 24px; font-weight: bold; color: #0b6e2e;}
    .grid td.bl {border-left: 3px solid #222;} .grid td.bt {border-top: 3px solid #222;}
    .grid td.br {border-right: 3px solid #222;} .grid td.bb {border-bottom: 3px solid #222;}
    </style><table class="grid">"""
    for r in rows:
        html += "<tr>"
        for c in cols:
            cell = r + c
            values = domainsDict[cell]
            classes = []
            if cell in filled:
                classes.append("given")
            elif cell in asterisk:
                classes.append("ast")
            else:
                classes.append("empty")
            if cell not in filled:
                classes.append("solved" if len(values) == 1 else "small")
            if c in "147":
                classes.append("bl")
            if c == "9":
                classes.append("br")
            if r in "ADG":
                classes.append("bt")
            if r == "I":
                classes.append("bb")
            text = "".join(str(v) for v in values)
            if len(text) > 5:
                text = text[:5] + "<br>" + text[5:]
            html += f'<td class="{" ".join(classes)}" title="{cell}: {",".join(str(v) for v in values)}">{text}</td>'
        html += "</tr>"
    html += "</table>"
    components.html(html, height=570)


def buildAsteriskGraph(asteriskCSP, domainsDict):
    net = Network(bgcolor="#242020", font_color="white", height="900px", width="100%",
                  cdn_resources="remote")

    nodes = list(cells)
    nodeColorsList = []
    nodeTitles = []
    nodeLabels = []

    for node in nodes:
        if len(asteriskCSP.domains[node]) == 1:
            nodeColorsList.append(nodeColors["filled"])
        elif node in asterisk:
            nodeColorsList.append(nodeColors["asterisk"])
        else:
            nodeColorsList.append(nodeColors["empty"])
        nodeTitles.append(",".join(str(v) for v in domainsDict[node]))
        nodeLabels.append(node + "\n" + "".join(str(v) for v in domainsDict[node]))

    sizes = [10] * len(nodes)
    x_coords = [int(node[1]) * 90 for node in nodes]
    y_coords = [(rows.index(node[0]) + 1) * 90 for node in nodes]

    net.add_nodes(nodes, color=nodeColorsList, size=sizes, title=nodeTitles, label=nodeLabels,
                  x=x_coords, y=y_coords)

    for nodeFrom in asteriskCSP.neighbors.keys():
        for nodeTo in asteriskCSP.neighbors[nodeFrom]:
            if nodeFrom[0] == nodeTo[0]:            # row constraints
                net.add_edge(nodeFrom, nodeTo, color="red")
            elif nodeFrom[1] == nodeTo[1]:          # column constraints
                net.add_edge(nodeFrom, nodeTo, color="blue")
            elif boxOf(nodeFrom) == boxOf(nodeTo):  # 3x3 region constraints
                net.add_edge(nodeFrom, nodeTo, color="green")
            else:                                   # asterisk constraints
                net.add_edge(nodeFrom, nodeTo, color="orange")

    net.set_edge_smooth('dynamic')
    net.toggle_physics(False)
    components.html(net.generate_html(), height=930)


def task2():
    st.header("Task 2. Asterisk Sudoku")
    st.write("Each cell is a variable with domain 1–9 (a given cell has only its value). "
             "Two cells are neighbors if they share a **row**, a **column**, a **3x3 region**, "
             "or are both in the pink **asterisk**. Neighbors must be different ($X_i \\neq X_j$).")

    if "sudoku_ac3" not in st.session_state:
        st.session_state["sudoku_ac3"] = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run AC-3", key="sudoku_run"):
            st.session_state["sudoku_ac3"] = True
    with col2:
        if st.button("Reset", key="sudoku_reset"):
            st.session_state["sudoku_ac3"] = False

    asteriskCSP = getAsteriskCSP()
    ac3 = st.session_state["sudoku_ac3"]
    if ac3:
        with st.spinner("Running AC-3 on 81 cells..."):
            result, currDomains = runAsteriskAC3()
        st.success(f"AC-3 applied. Arc consistent: {result[0]}. Constraint checks: {result[1]}. "
                   "Check the new domains.")
        domainsDict = currDomains
    else:
        domainsDict = asteriskCSP.domains

    tab1, tab2, tab3 = st.tabs(["Board", "All cell domains", "Graph of constraints"])

    with tab1:
        st.caption("Yellow = given, pink = asterisk cell, white = empty cell. "
                   "Small digits = the cell's domain; a big green digit = AC-3 narrowed it to one value. "
                   "Hover over a cell to see its name.")
        drawGrid(domainsDict)

    with tab2:
        table = []
        for cell in cells:
            row = {"Cell": cell,
                   "Type": "given" if cell in filled else ("asterisk" if cell in asterisk else "empty"),
                   "Domain before AC-3": ", ".join(str(v) for v in asteriskCSP.domains[cell])}
            if ac3:
                row["Domain after AC-3"] = ", ".join(str(v) for v in currDomains[cell])
            table.append(row)
        st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True, height=600)

    with tab3:
        st.caption("Edges: red = row, blue = column, green = 3x3 region, orange = asterisk. "
                   "Hover over a node to see its domain.")
        if ac3:
            st.subheader("After AC-3")
        else:
            st.subheader("Original CSP")
        buildAsteriskGraph(asteriskCSP, domainsDict)


def main():
    st.set_page_config(page_title="Lab 6. Constraint Propagation", layout="wide")
    st.title("Lab 6. Constraint Propagation in solving CSPs")

    task = st.sidebar.radio("Choose a task", ["Task 1 - Vancouver tour", "Task 2 - Asterisk Sudoku"])

    if task.startswith("Task 1"):
        task1()
    else:
        task2()


if __name__ == '__main__':
    main()
