#Lab5: PacMan search demo

import math
import time
import streamlit as st
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle, Circle, Wedge

import Lab5 as lab


#create an agent using the selected search
def create_agent(graph, food, ghosts, start, finish, name):

    heuristic = lab.manhattan

    if name == "A* Euclidean":

        heuristic = math.dist
        program = lab.A_StarSearchAgentProgram(heuristic)

    elif name == "A* Manhattan":

        program = lab.A_StarSearchAgentProgram(heuristic)

    elif name == "IDA* Manhattan":

        program = lab.IDA_StarSearchAgentProgram(heuristic)

    else:

        program = lab.RBFSearchAgentProgram(heuristic)

    agent = lab.PacManAgent(
        start,
        graph,
        finish,
        food,
        program,
        heuristic
    )

    world = lab.PacManEnvironment(
        graph,
        food,
        ghosts
    )

    world.add_thing(agent)

    return agent, world


#start a fresh run
def start_run(name, seed):

    maze, graph, food, ghosts, start, finish = lab.make_world(
        seed=seed
    )

    agent, world = create_agent(
        graph,
        food,
        ghosts,
        start,
        finish,
        name
    )

    st.session_state["maze"] = maze
    st.session_state["graph"] = graph
    st.session_state["food"] = food
    st.session_state["ghosts"] = ghosts

    st.session_state["start"] = start
    st.session_state["finish"] = finish

    st.session_state["agent"] = agent
    st.session_state["world"] = world

    st.session_state["settings"] = (name, seed)
    st.session_state["comparison"] = []


#draw the maze and the route travelled
def draw_maze(
    maze,
    agent,
    world,
    start,
    finish,
    show_plan,
    reveal
):

    figure, ax = plt.subplots(figsize=(7, 7))

    figure.patch.set_facecolor("#0e1525")
    ax.set_facecolor("#0e1525")

    for r in range(len(maze)):

        for c in range(len(maze[0])):

            if maze[r, c] == 0:

                wall = Rectangle(
                    (c - 0.47, r - 0.47),
                    0.94,
                    0.94,
                    facecolor="#283e82",
                    edgecolor="#4264bd"
                )

                ax.add_patch(wall)

    colors = [
        "#60a5fa",
        "#fb923c",
        "#4ade80",
        "#f87171",
        "#c084fc"
    ]

    number = 0

    for segment in agent.segments:

        x = []
        y = []

        for r, c in segment:

            x.append(c)
            y.append(r)

        ax.plot(
            x,
            y,
            color=colors[number % len(colors)],
            linewidth=3,
            alpha=0.8
        )

        number += 1

    if show_plan and agent.alive:

        if len(agent.seq) > 0 and agent.path is not None:

            x = []
            y = []

            for node in agent.path:

                x.append(node.state[1])
                y.append(node.state[0])

            ax.plot(
                x,
                y,
                "--",
                color="white",
                linewidth=1.5,
                alpha=0.6
            )

    for r, c in world.food:

        food_dot = Circle(
            (c, r),
            0.12,
            color="#fde047"
        )

        ax.add_patch(food_dot)

    for position in world.ghosts:

        ghost = world.ghosts[position]

        if reveal or position in agent.known_ghosts:

            r, c = position

            if ghost.alive:

                ghost_shape = Circle(
                    (c, r),
                    0.26,
                    color="#e879f9"
                )

                ax.add_patch(ghost_shape)

                ax.text(
                    c,
                    r,
                    "G",
                    color="#271138",
                    ha="center",
                    va="center",
                    fontsize=11,
                    weight="bold"
                )

            else:

                ax.text(
                    c,
                    r,
                    "X",
                    color="#e879f9",
                    ha="center",
                    va="center"
                )

    exit_box = Rectangle(
        (finish[1] - 0.35, finish[0] - 0.35),
        0.7,
        0.7,
        fill=False,
        edgecolor="#34d399",
        linewidth=2
    )

    ax.add_patch(exit_box)

    ax.text(
        finish[1],
        finish[0],
        "E",
        color="#34d399",
        ha="center",
        va="center"
    )

    ax.text(
        start[1],
        start[0] - 0.32,
        "S",
        color="#93c5fd",
        ha="center"
    )

    r, c = agent.state

    pacman = Wedge(
        (c, r),
        0.32,
        35,
        325,
        color="#facc15",
        zorder=10
    )

    eye = Circle(
        (c + 0.02, r - 0.15),
        0.035,
        color="#111827",
        zorder=11
    )

    ax.add_patch(pacman)
    ax.add_patch(eye)

    ax.set_xlim(-0.5, len(maze[0]) - 0.5)
    ax.set_ylim(len(maze) - 0.5, -0.5)

    ax.set_aspect("equal")

    ax.set_xticks(range(len(maze[0])))
    ax.set_yticks(range(len(maze)))

    ax.tick_params(
        colors="#a9b7cf",
        length=0
    )

    ax.set_xlabel("Column", color="#a9b7cf")
    ax.set_ylabel("Row", color="#a9b7cf")

    for border in ax.spines.values():
        border.set_visible(False)

    figure.tight_layout()

    return figure


#update the maze, scores, and recent events
def show_run(area, show_plan, reveal):

    agent = st.session_state["agent"]
    world = st.session_state["world"]
    food = st.session_state["food"]

    with area.container():

        scores = st.columns(4)

        scores[0].metric(
            "Moves",
            len(agent.route) - 1
        )

        scores[1].metric(
            "Food collected",
            str(len(agent.collected)) + " / " + str(len(food))
        )

        scores[2].metric(
            "Performance",
            round(agent.performance, 2)
        )

        scores[3].metric(
            "Expanded nodes",
            agent.expanded
        )

        board, details = st.columns([2, 1])

        with board:

            figure = draw_maze(
                st.session_state["maze"],
                agent,
                world,
                st.session_state["start"],
                st.session_state["finish"],
                show_plan,
                reveal
            )

            st.pyplot(figure, width=600)
            plt.close(figure)

            st.caption(
                "Gold dots: food · Green E: exit · "
                "G: ghost · X: defeated ghost"
            )

            st.caption(
                "Colored lines: travelled route · "
                "White dashed line: planned route"
            )

        with details:

            st.subheader("Mission status")

            if agent.status == "Success":

                st.success("All food collected. Exit reached!")

            elif agent.alive:

                st.info("Collect the food, then reach the exit.")

            else:

                st.error(agent.status)

            st.write(
                "**Current position:**",
                str(agent.state)
            )

            if agent.alive and len(agent.seq) > 0:

                if agent.path is not None:

                    st.write(
                        "**Next target:**",
                        str(agent.path[-1].state)
                    )

            elif agent.alive:

                st.caption(
                    "Next move will select the next food or exit."
                )

            st.write(
                "**Path cost:**",
                agent.total_cost
            )

            st.write(
                "**Ghosts discovered:**",
                len(agent.known_ghosts)
            )

            st.caption(
                "Expanded nodes measure planning work, not movement."
            )

            st.subheader("Recent events")

            for event in agent.events[-5:]:
                st.caption(event)

        with st.expander("Full event log"):

            for event in agent.events:
                st.write(event)


#compare fresh agents on the same maze
def compare_searches(names):

    rows = []

    for name in names:

        agent, world = create_agent(
            st.session_state["graph"],
            st.session_state["food"],
            st.session_state["ghosts"],
            st.session_state["start"],
            st.session_state["finish"],
            name
        )

        while agent.alive:
            world.step()

        row = {
            "Algorithm": name,
            "Status": agent.status,
            "Cost": agent.total_cost,
            "Food": len(agent.collected),
            "Expanded": agent.expanded,
            "Performance": round(agent.performance, 2)
        }

        rows.append(row)

    return rows


def main():

    st.set_page_config(
        page_title="Pac-Man Search Lab",
        page_icon="🟡",
        layout="wide"
    )

    st.title("🟡 Pac-Man Search Lab")

    st.caption(
        "Find the food. Survive the ghosts. Reach the exit."
    )

    names = [
        "A* Euclidean",
        "A* Manhattan",
        "IDA* Manhattan",
        "RBFS Manhattan"
    ]

    st.sidebar.header("Choose your search")

    name = st.sidebar.selectbox(
        "Algorithm",
        names
    )

    seed = st.sidebar.selectbox(
        "Maze seed",
        [3220, 7, 42]
    )

    st.sidebar.caption(
        "The same seed recreates the same maze."
    )

    show_plan = st.sidebar.checkbox(
        "Show planned route",
        value=True
    )

    reveal = st.sidebar.checkbox(
        "Reveal all ghosts",
        value=False
    )

    st.sidebar.caption(
        "Revealing ghosts changes the display only."
    )

    reset = st.sidebar.button("Reset run")

    if "settings" not in st.session_state:

        start_run(name, seed)

    elif st.session_state["settings"] != (name, seed) or reset:

        start_run(name, seed)

    with st.sidebar.expander("Maze rules"):

        st.write("Each move costs 1 performance point.")

        st.write("Food doubles the current performance.")

        st.write(
            "Pac-Man wins only when stronger than the ghost."
        )

        st.write(
            "Winning a fight reduces performance by 10%."
        )

        st.write(
            "Collect every food pellet before finishing."
        )

    agent = st.session_state["agent"]
    world = st.session_state["world"]

    buttons = st.columns(3)

    play = buttons[0].button(
        "▶ Play to exit",
        type="primary",
        disabled=not agent.alive
    )

    step = buttons[1].button(
        "Next move",
        disabled=not agent.alive
    )

    compare = buttons[2].button(
        "Compare all four"
    )

    area = st.empty()

    if step:

        world.step()
        st.rerun()

    if play:

        while agent.alive:

            world.step()

            show_run(
                area,
                show_plan,
                reveal
            )

            time.sleep(0.15)

        st.rerun()

    show_run(
        area,
        show_plan,
        reveal
    )

    if compare:

        with st.spinner("Comparing the searches..."):

            st.session_state["comparison"] = compare_searches(
                names
            )

    if len(st.session_state["comparison"]) > 0:

        st.subheader("Same maze, four searches")

        st.table(
            st.session_state["comparison"]
        )

        st.caption(
            "Each search starts fresh. Expansion totals "
            "include comparisons to all food targets."
        )

        st.caption(
            "Choosing the cheapest next food does not "
            "guarantee the cheapest complete tour."
        )


if __name__ == "__main__":
    main()