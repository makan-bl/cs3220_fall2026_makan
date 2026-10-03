import random
from src.environmentProClass import environmentPro
from src.thingClass import Thing
from src.locations import *

from src.catFriendlyHouse_membersClass import Food,Milk,Sausage,Mouse,Dog

from src.agentClass import Agent, proCatAgent, MouseAgent, CatAgent


#catFriendlyHouse_envClass
class catFriendlyHouse_env(environmentPro):
  def __init__(self):
    super().__init__()
    self.locations=[loc_A, loc_B, loc_C]

  def default_location(self, thing):
    print("The item is starting in random location...")
    return random.choice(self.locations)
  
    
  

  def update_status(self):
    #the state of each room depends on the kind of Food located there
    self.status = {}
    for loc in self.locations:
      names = [type(f).__name__ for f in self.list_things_at(loc, Food)]
      if len(names) == 0:
        self.status[loc] = 'Empty'
      elif len(names) == 1:
        self.status[loc] = names[0]
      else:
        self.status[loc] = names

  def percept(self, agent):
    #returns the agent's location and the status of that location (like TrivialVacuumEnvironment)
    self.update_status()
    return agent.location, self.status[agent.location]

  def move_cat(self, agent):
    #1 move in the Cat's direction; each movement -> performance -1
    idx = self.locations.index(agent.location)
    last = len(self.locations) - 1
    if agent.direction:
      if idx == last:  #last room reached, but not ALL items are consumed
        agent.changeDirection()
        idx -= 1
      else:
        idx += 1
    else:
      if idx == 0:     #room (0,0) is the end of the hunt
        print("The Cat-Agent is back in room {}. The hunt is over!".format(agent.location))
        agent.alive = False
        return
      idx -= 1
    agent.location = self.locations[idx]
    agent.performance -= 1
    print("The Agent moved to {}".format(agent.location))

  def execute_action(self, agent, action):
    #changes the state of the environment based on what the agent does.
    if not self.is_agent_alive(agent):
      return
    loc = agent.location
    foods = self.list_things_at(loc, Food)

    if action == 'GoAhead':
      print("The Agent decided to {} at location: {}".format(action, loc))
      self.move_cat(agent)

    elif action == 'Drink':
      if agent.drink(foods[0]):
        print("The Agent decided to {} {} at location: {}".format(action, foods[0], loc))
        self.delete_thing(foods[0])

    elif action == 'Eat':
      if agent.eat(foods[0]):
        print("The Agent decided to {} {} at location: {}".format(action, foods[0], loc))
        self.delete_thing(foods[0])

    elif action == 'Catch':
      mouse = foods[0]
      if agent.catch(mouse):
        print("The Agent did {} {} at location: {}".format(action, mouse, loc))
      else:
        print("The Cat-Agent is too weak (performance {}) to catch {}. The Mouse survived and ran away!".format(agent.performance, mouse))
      self.delete_thing(mouse)

    print("Cat performance: {}".format(agent.performance))
    if len(self.list_things_at_all_food()) == 0:
      print("No food left in the house. The hunt is over!")
      agent.alive = False

  def list_things_at_all_food(self):
    return [t for t in self.things if isinstance(t, Food)]

  def is_done(self):
    no_agents = not any(agent.is_alive() for agent in self.agents)
    no_food = len(self.list_things_at_all_food()) == 0
    return no_agents or no_food



  #catFriendlyHouse_envClass
class catFriendlyHouse2_env(environmentPro):
  def __init__(self):
    super().__init__()
    self.locations=[loc_A, loc_B, loc_C, loc_D]

  def default_location(self, thing):
    print("The item is starting in random location...")
    return random.choice(self.locations)
  
  #Return all agants exactly at a given location
  def list_agents_at(self, location, thingClass=Thing):
      return [agent for agent in self.agents if agent.location == location and isinstance(agent, thingClass)]

  def percept(self, agent):
    #return a list of things AND a list of agents that are in our agent's location
    things = self.list_things_at(agent.location)
    agents = self.list_agents_at(agent.location)
    return agent.location, things, agents

  def check_game_over(self, agent):
    if agent.performance <= 0:
      agent.alive = False
      print("Cat performance is {}.... GAME OVER!".format(agent.performance))

  def move_cat(self, agent):
    #1 move in the Cat's direction; at the last room the direction changes automatically
    idx = self.locations.index(agent.location)
    last = len(self.locations) - 1
    if (agent.direction and idx == last) or (not agent.direction and idx == 0):
      agent.changeDirection()
    idx = idx + 1 if agent.direction else idx - 1
    agent.location = self.locations[idx]
    agent.performance -= 5    #each movement for a Cat -> performance -5
    self.check_game_over(agent)
  

  def add_thing(self, thing, location=None): # improved  
    # perf = original one not 0 like in parent class
    #from src.agentClass import Agent
    if thing in self.agents:
      print("Can't add the same agent twice")
    else:
      if isinstance(thing, Agent):
        #thing.performance = 0
        thing.location = location if location is not None else self.default_location(thing)
        self.agents.append(thing)
        print(f"Welcome! You are added in location {thing.location}")
    if thing in self.things and thing.location==location:
      print("Can't add the same agent twice")
    else:
      if not isinstance(thing, Agent):
        thing.location = location if location is not None else self.default_location(thing)
        self.things.append(thing)
    
  def execute_action(self, agent, action):
    #changes the state of the environment based on what the agent does.
    if self.is_agent_alive(agent):
      #the current agent is Cat & Mouse is still there
      if isinstance(agent, proCatAgent) and len(self.agents+self.things)>0:
        print("Some items are still there ....")
        if action=='Go ahead':
          print("The Agent decided to {} at location: {}".format(action,agent.location))
          self.move_cat(agent)

        elif action=='Catch':
          mice = self.list_agents_at(agent.location, MouseAgent)
          if len(mice) == 0:
            print("Agent tried to Catch, but no MouseAgent was found at {}.".format(agent.location))
          else:
            mouse = mice[0]
            if agent.performance < mouse.performance*5:   #weak Cat
              agent.performance -= 10
              print("The Cat is too weak to catch {} at location: {}. Cat performance: {}".format(mouse,agent.location,agent.performance))
              self.check_game_over(agent)
            else:
              agent.performance += 10
              print("The Agent did Catch {} at location: {}".format(mouse,agent.location))
              self.delete_thing(mouse)
              if len([a for a in self.agents if isinstance(a, MouseAgent)]) == 0:
                print("There is nothing for Agent Cat here. Done!")
                agent.alive=False

        elif action=='Check direction':
          print("The Agent decided to {} at location: {}".format(action,agent.location))
          self.move_cat(agent)

        elif action=='Fight':
          dogs = self.list_things_at(agent.location, Dog)
          if agent.performance >= 10:   #only super strong Cat wins
            agent.performance += 20
            print("The Agent won the Fight with {} at location: {}. The Dog ran away!".format(dogs[0],agent.location))
            self.delete_thing(dogs[0])
          else:
            agent.performance -= 10
            print("The Dog won the Fight at location: {}. Cat performance: {}".format(agent.location,agent.performance))
            self.check_game_over(agent)

      elif isinstance(agent, MouseAgent):
        print("the Agent Mouse is still running with a performance {}".format(agent.performance))
        agent.location = action
        print("The Agent Mouse decided to move to {}".format(action))
        agent.performance -= 1    #each movement -> performance -1
        self.update_agent_alive(agent)

      else:
          print("There is nothing for Agent Cat here. Done!")
          agent.alive=False
    
    
  def is_done(self):
    no_agents = not any(agent.is_alive() for agent in self.agents)
    #return no_agents or no_items
    return no_agents
    
    








  

