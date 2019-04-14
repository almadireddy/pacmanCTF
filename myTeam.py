# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState


#################
# Team creation #
#################

def createTeam(first_index, second_index, isRed,
               first='MiniMaxAgent', second='MiniMaxAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using first_index and second_index as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(first_index, isRed), eval(second)(second_index, isRed)]


##########
# Agents #
##########


class MiniMaxAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """
    def __init__(self, index, isRed):
        CaptureAgent.__init__(self, index)
        self.isRed = isRed  # maximize on red if true
        self.redTeamIndices = False

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """
        CaptureAgent.registerInitialState(self, game_state)

        self.redTeamIndices = game_state.getRedTeamIndices()

    def chooseAction(self, game_state):
        # type: (GameState) -> str
        def value(game_state, depth, next_index, action):
            # type: (GameState, int, int, str) -> int

            max_depth = 3
            if depth > max_depth:
                return utility(game_state)
            if game_state.isOver():
                return game_state.getScore()*100

            if next_index % 4 in self.redTeamIndices:
                if self.isRed:
                    return max_value(game_state.generateSuccessor(next_index % 4, action), depth + 1, next_index + 1)
                else:
                    return min_value(game_state.generateSuccessor(next_index % 4, action), depth + 1, next_index + 1)
            else:
                if self.isRed:
                    return min_value(game_state.generateSuccessor(next_index % 4, action), depth + 1, next_index + 1)
                else:
                    return max_value(game_state.generateSuccessor(next_index % 4, action), depth + 1, next_index + 1)

        def max_value(game_state, depth, index):
            # type: (GameState, int, int) -> int
            v = -1000000

            for action in game_state.getLegalActions(index % 4):
                v = max(v, value(game_state.generateSuccessor(index % 4, action), depth, index, action))
            return v

        def min_value(game_state, index, depth):
            # type: (GameState, int, int) -> int
            v = 1000000
            for action in game_state.getLegalActions(index % 4):
                v = min(v, value(game_state.generateSuccessor(index % 4, action), depth + 1, index + 1, action))
            return v

        def utility(game_state):
            # type: (GameState) -> int
            return 0

        best_action = None
        best_value = None
        print game_state.getLegalActions(self.index)
        for ac in game_state.getLegalActions(self.index):
            val = value(game_state, 0, self.index, ac)
            if val > best_value:
                best_action = ac
                best_value = val

        return best_action


class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        '''
        You should change this in your own agent.
        '''

        return random.choice(actions)
