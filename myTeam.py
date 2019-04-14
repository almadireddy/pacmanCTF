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
import math

#################
# Team creation #
#################

infinity = float('inf')


def createTeam(firstIndex, secondIndex, isRed,
               first='AlphaBetaAgent', second='AlphaBetaAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
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
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

def alpha_beta_cutoff_search(game_state, d=4, cutoff_test=None, eval_fn=None, max_player_index=0):
    player = max_player_index

    def max_value(st, alpha, beta, depth, player):
        if cutoff_test(st, depth):
            return eval_fn(st, player)

        val = -infinity
        for action in game_state.getLegalActions(player % 4):
            print "depth: ", depth, " | max: ", action
            val = max(val,
                      min_value(game_state.generateSuccessor(player % 4, action), alpha, beta, depth + 1, player + 1))

            if val >= beta:
                return val

            alpha = max(alpha, val)

        return val

    def min_value(st, alpha, beta, depth, player):
        if cutoff_test(st, depth):
            return eval_fn(st, player)

        val = infinity
        for action in game_state.getLegalActions(player % 4):
            print "depth: ", depth, " | min: ", action
            val = min(val,
                      max_value(game_state.generateSuccessor(player % 4, action), alpha, beta, depth + 1, player + 1))

            if val <= alpha:
                return val

            beta = min(beta, val)

        return val

    cutoff_test = (cutoff_test or (lambda st, depth: depth > d or st.isOver()))
    eval_fn = eval_fn
    best_score = -infinity
    beta = infinity
    best_action = None

    for ac in game_state.getLegalActions(player):
        v = min_value(game_state.generateSuccessor(player, ac), best_score, beta, 1, player)

        if v > best_score:
            best_score = v
            best_action = ac
    print "Best action: ", best_action
    return best_action


class AlphaBetaAgent(CaptureAgent):
    def registerInitialState(self, game_state):
        CaptureAgent.registerInitialState(self, game_state)

    def chooseAction(self, game_state):
        return alpha_beta_cutoff_search(game_state, 4, None, self.utility, self.index)

    def utility(self, game_state, index):
        carrying = game_state.getAgentState(index % 4).numCarrying
        returned = game_state.getAgentState(index % 4).numReturned

        red = False

        if index % 4 in game_state.getRedTeamIndices():  # we are red
            red = True

        if red:
            capsule_difference = len(game_state.getBlueCapsules()) - len(game_state.getRedCapsules())
            food = game_state.getBlueFood()
            my_food = game_state.getRedFood()
        else:
            capsule_difference = len(game_state.getRedCapsules()) - len(game_state.getBlueCapsules())
            food = game_state.getRedFood()
            my_food = game_state.getBlueFood()

        lowest_distance = 10000
        highest_distance = 0
        pos = game_state.getAgentPosition(index % 4)
        remaining = 0

        for i, x in enumerate(food):
            for j, y in enumerate(food[i]):
                if food[i][j]:
                    length = self.distancer.getDistance(pos, (i, j))

                    if length < lowest_distance:
                        lowest_distance = length
                    if length > highest_distance:
                        highest_distance = length

        for i, x in enumerate(my_food):
            for j, y in enumerate(my_food[i]):
                if my_food[i][j]:
                    remaining += 1

        if red:
            eval = -carrying - returned - capsule_difference - game_state.getScore() + 2**lowest_distance + remaining + ((lowest_distance + highest_distance)/2)
        else:
            eval = carrying + returned + capsule_difference + game_state.getScore() - 2**lowest_distance - remaining - ((lowest_distance + highest_distance)/2)
        print " -- ", eval
        return eval


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
