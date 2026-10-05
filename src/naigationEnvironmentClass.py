# NavigationEnvironment - the environment for problem-solving navigation agents
# (used by the tutorial part of the notebook and by lab3app_navExample.py)
from src.environmentClass import Environment


class NavigationEnvironment(Environment):
  def __init__(self, graph):
    super().__init__()
    self.status = graph          # the state space (a Graph object)
    self.goals = {}              # agent -> its goal(s), saved before the agent plans

  def percept(self, agent):
    # fully observable: the agent perceives its current state (city / node)
    return agent.state

  def is_agent_alive(self, agent):
    return agent.alive

  def is_done(self):
    return not any(agent.alive for agent in self.agents)

  def add_thing(self, thing, location=None):
    if thing in self.agents:
      print("Can't add the same agent twice")
      return
    if location is not None:
      thing.state = location
    goal = thing.goal
    self.goals[thing] = list(goal) if isinstance(goal, list) else goal
    self.agents.append(thing)
    # a problem-solving agent formulates the goal & the problem and searches when it enters the env
    thing(self.percept(thing))
    print("The Agent in {} with performance {}".format(thing.state, thing.performance))

  def execute_action(self, agent, action):
    if not self.is_agent_alive(agent) or action is None:
      return
    agent.state = action          # in a graph problem the action == the node to move to
    agent.performance -= 1
    print("Agent in {} with performance = {}".format(agent.state, agent.performance))

    if len(agent.seq) == 0:        # the whole plan is executed
      goal = self.goals[agent]
      if isinstance(goal, list) and len(goal) > 1:
        print("Agent reached all goals")
      else:
        print("Agent reached the goal: {}".format(goal[0] if isinstance(goal, list) else goal))
      agent.goal = agent.state     # lets the web app recognise the goal state
      agent.alive = False          # the work is done
    elif agent.performance <= 0:
      agent.alive = False
      print("Agent in {} is dead.".format(agent.state))

  def step(self):
    if self.is_done():
      print("There is no one here who could work...")
      return
    for agent in self.agents:
      if agent.alive:
        action = agent.seq.pop(0) if agent.seq else None
        print("Agent decided to do {}.".format(action))
        self.execute_action(agent, action)

  def run(self, steps=10):
    for step in range(steps):
      if self.is_done():
        return
      print("step {0}:".format(step+1))
      self.step()
