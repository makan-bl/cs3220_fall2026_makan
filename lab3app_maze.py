# Lab3 - Treasure Maze web app: 3 tabs, 1 tab per version
import io
import contextlib

import streamlit as st
import streamlit.components.v1 as components  # to display the HTML code
from pyvis.network import Network               # to create the graph as an interactive html object

from src.graphClass import Graph
from data.mazeData import mazeData, mazeDirections, mazeLocations, TREASURES, START, FINISH
from src.mazeEnvironmentClass import MazeEnvironment
from src.agents import MazeAgentBasic, MazeAgentAllTreasures, MazeAgentSpecificTreasure

HEADING_NAME = {'N': 'up', 'S': 'down', 'E': 'right', 'W': 'left'}


def run_and_capture(fn):
    """Run fn() and return everything it printed (the environment/agent log)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        fn()
    return buffer.getvalue()


def new_game(key, version, treasure=None):
    mazeGraph = Graph({node: dict(links) for node, links in mazeData.items()})
    env = MazeEnvironment(mazeGraph, mazeDirections)
    if version == 1:
        agent = MazeAgentBasic(mazeGraph, mazeDirections)
    elif version == 2:
        agent = MazeAgentAllTreasures(mazeGraph, mazeDirections)
    else:
        agent = MazeAgentSpecificTreasure(mazeGraph, mazeDirections, treasure)
    log = run_and_capture(lambda: env.add_thing(agent))
    st.session_state[key] = {"env": env, "agent": agent, "log": [log], "visited": [START],
                             "plan_length": len(agent.seq), "treasure": treasure}


def agent_step(key):
    game = st.session_state[key]
    game["log"].append(run_and_capture(game["env"].step))
    game["visited"].append(game["agent"].position)


def agent_run(key):
    game = st.session_state[key]
    while not game["env"].is_done():
        agent_step(key)


def build_graph(game):
    env, agent = game["env"], game["agent"]
    net = Network(bgcolor="#242020", font_color="white", height="600px", width="100%",
                  cdn_resources="remote")
    for node in sorted(env.status.nodes()):
        col, row = mazeLocations[node]
        label, color, size = node, "white", 12
        if node in game["visited"]:
            color = "orange"                      # where the Agent has been
        if node == START:
            color = "red"
        if node == FINISH:
            color = "green"
        treasure = env.treasures.get(node)        # treasures still lying in the maze
        if treasure:
            label = "{} {}".format(node, TREASURES[treasure])
            color = "gold"
        if node == agent.position:
            label = "{} \U0001F916".format(label)  # the Agent
            size = 22
        net.add_node(node, label=label, title=node, x=col * 60, y=row * 60,
                     physics=False, color=color, size=size)
    edges = []
    for node_source in env.status.nodes():
        for node_target in env.status.get(node_source):
            if set((node_source, node_target)) not in edges:
                net.add_edge(node_source, node_target, color="#bbbbbb")
                edges.append(set((node_source, node_target)))
    components.html(net.generate_html(), height=620)


def show_tab(key, version, goal_text):
    st.info("Goal: " + goal_text)

    treasure = None
    if version == 3:
        options = list(TREASURES.keys())
        treasure = st.selectbox("Which treasure must the Agent find?", options,
                                format_func=lambda t: "{} {}".format(TREASURES[t], t), key=key + "_choice")
        if key in st.session_state and st.session_state[key]["treasure"] != treasure:
            new_game(key, version, treasure)

    if key not in st.session_state:
        new_game(key, version, treasure)
    game = st.session_state[key]
    env, agent = game["env"], game["agent"]

    st.header("State of the Environment", divider="red")
    placed = ", ".join("{} {} at {}".format(TREASURES[t], t, n) for n, t in sorted(env.treasures.items(), key=lambda x: x[1]))
    st.write("Treasures still in the maze: " + (placed if placed else "none"))
    build_graph(game)

    collected = ", ".join("{} {}".format(TREASURES[t], t) for t in agent.collected) or "nothing yet"
    st.info("The Agent is at {} facing {} with performance {}.".format(agent.position, HEADING_NAME[agent.heading], agent.performance))
    st.info("Collected: {}".format(collected))
    st.info("Plan: {} actions (initial performance {}). Actions left: {}".format(
        game["plan_length"], len(env.status.nodes()) // 2, ", ".join(agent.seq) if agent.seq else "none"))

    if not agent.alive:
        if env.goal_reached(agent):
            st.success("The Agent reached the goal: the exit \U0001F3E0 {}!".format(FINISH))
        else:
            st.error("The Agent at {} is dead.".format(agent.position))

    c1, c2, c3 = st.columns(3)
    c1.button("Run One Agent's Step", key=key + "_step", on_click=agent_step, args=[key], disabled=not agent.alive)
    c2.button("Run to the end", key=key + "_run", on_click=agent_run, args=[key], disabled=not agent.alive)
    c3.button("New maze (new treasures)", key=key + "_new", on_click=new_game, args=[key, version, treasure])

    with st.expander("Agent log"):
        st.code("".join(game["log"]))


def main():
    st.title("Problem Solving Agents: Treasure Maze")
    st.caption("S = start (red), F = finish (green), gold = treasure, orange = visited, \U0001F916 = the Agent. "
               "Actions: advance / left / right. Search: Breadth-First Search.")
    tab1, tab2, tab3 = st.tabs(["Basic", "Treasure collection", "Specific treasure"])
    with tab1:
        show_tab("game_basic", 1, "reach the finish")
    with tab2:
        show_tab("game_all", 2, "collect ALL treasures and reach the finish")
    with tab3:
        show_tab("game_specific", 3, "find a particular treasure and then reach the finish")


if __name__ == '__main__':
    main()
