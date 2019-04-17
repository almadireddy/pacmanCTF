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
from game import Directions, Actions
from capture import GameState
from game import Agent
import math

#################
# Team creation #
#################

infinity = float('inf')


def createTeam(firstIndex, secondIndex, isRed,
               first='OffenseAgent', second='DefenseAgent'):
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

class AlphaBetaAgent(CaptureAgent):
    def __init__(self, index):
        CaptureAgent.__init__(self, index)

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)

    def chooseAction(self, gameState):
        # type: (GameState) -> str

        def alpha_beta_cutoff_search(game_state, d):
            """Search game to determine best action; use alpha-beta pruning.
            This version cuts off search and uses an evaluation function."""

            def cutoff_test(state, depth):
                # type: (GameState, int) -> bool
                return state.isOver() or depth > d

            # Functions used by alpha-beta
            def max_value(state, alpha, beta, depth, index):
                # type: (GameState, int, int, int, int) -> float

                index = index % 4

                if cutoff_test(state, depth):
                    return self.evaluate_state(state, index)  # pass in whether maximizer or minimizer

                value = -infinity
                for action in state.getLegalActions(index):
                    new_state = state.generateSuccessor(index, action).deepCopy()
                    value = max(value, min_value(new_state,
                                                 alpha, beta, depth + 1, index + 1))
                    if value >= beta:
                        return value
                    alpha = max(alpha, value)

                return value

            def min_value(state, alpha, beta, depth, index):
                # type: (GameState, int, int, int, int) -> float
                index = index % 4

                if cutoff_test(state, depth):
                    return self.evaluate_state(state, index)  # pass in whether maximizer or minimizer

                value = infinity
                for action in state.getLegalActions(index):
                    new_state = state.generateSuccessor(index, action).deepCopy()
                    value = min(value, max_value(new_state,
                                                 alpha, beta, depth + 1, index + 1))
                    if value <= alpha:
                        return value
                    beta = min(beta, value)
                return value

            # Body of alpha-beta_cutoff_search starts here:
            # The default test cuts off at depth d or at a terminal state
            best_score = -infinity
            a = best_score
            b = infinity
            best_action = None

            x = [x for x in game_state.getLegalActions(self.index) if x != "Stop"]
            for ac in x:
                v = min_value(game_state.generateSuccessor(self.index, ac), a, b, 1, self.index)
                print "Action: ", ac, "| Score:", v
                if v > best_score:
                    best_score = v
                    best_action = ac

            print " -- Best Value:", best_score, "| Best Action:", best_action
            print " "
            return best_action

        return alpha_beta_cutoff_search(gameState, 4)

    def get_weights(self, maximizer=True):
        # type: (bool) -> dict
        if maximizer:
            return {'score': 10}
        else:
            return {'score': -10}

    def get_features(self, game_state, index=0):
        # type: (GameState, int) -> dict
        return {'score': self.getScore(game_state)}

    def evaluate_state(self, game_state, index=0):
        # type: (GameState, int) -> float

        maximizer = True if not index == self.index or index == ((self.index + 2) % 4) else False
        weights = self.get_weights(maximizer)
        features = self.get_features(game_state, index)

        value = 0
        for x in weights:
            value += weights[x] * features[x]

        return value


class OffenseAgent(AlphaBetaAgent):
    def __init__(self, index):
        CaptureAgent.__init__(self, index)
        print "My Index:", index
        self.startPosition = (0, 0)
        self.isRed = False

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)
        self.startPosition = game_state.getInitialAgentPosition(self.index)
        if self.index in game_state.getRedTeamIndices():
            self.isRed = True
        print self.startPosition

    def get_features(self, game_state, index=0):
        # type: (GameState, int) -> dict
        distance_from_start = self.getMazeDistance(game_state.getAgentPosition(self.index),
                                                   self.startPosition)

        score = self.getScore(game_state)
        agent_state = game_state.getAgentState(index)
        num_carrying = agent_state.numCarrying
        ''' self.isPacman = isPacman
            self.scaredTimer = 0
            self.numCarrying = 0
            self.numReturned = 0
        '''

        food_list = self.getFood(game_state).asList()
        distance_to_food = 0
        food_remaining = len(food_list)

        if len(food_list) > 0:
            my_pos = agent_state.getPosition()
            distance_to_food = min([self.getMazeDistance(my_pos, food) for food in food_list])

        is_pac_man = agent_state.isPacman

        return_home = 0

        enemies = [game_state.getAgentState(i) for i in self.getOpponents(game_state)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() is not None]

        nearest_ghost = 0

        if len(ghosts) > 0:
            dists = [self.getMazeDistance(game_state.getAgentPosition(self.index), a.getPosition()) for a in ghosts]
            nearest_ghost = min(dists)

        if nearest_ghost > 3:  # ghost distance threshold
            nearest_ghost = 0
        elif 0 < nearest_ghost <= 3:
            return_home = self.getMazeDistance(game_state.getAgentPosition(index),
                                               self.startPosition)

        if return_home > 0:
            num_carrying = -num_carrying

        to_return = {
            'score': score,
            'distanceFromStart': distance_from_start,
            'closestFood': distance_to_food,
            'isPacMan': 1 if is_pac_man else 0,
            'numCarrying': num_carrying,
            'foodRemaining': food_remaining,
            'returnHome': return_home,
            'nearestGhost': nearest_ghost
        }

        print "   -- ", to_return
        return to_return

    def get_weights(self, maximizer=True):
        # type: (bool) -> dict

        if maximizer:
            return {
                'score': -10,
                'distanceFromStart': -3,
                'closestFood': 3,
                'isPacMan': 10,
                'distanceToMinimize': -2
            }
        else:
            return {
                'score': -1000,
                'closestFood': -500,
                'isPacMan': 50,
                'numCarrying': 2500,
                'foodRemaining': -500,
                'nearestGhost': 3000,
                'returnHome': -5000
            }


class DefenseAgent(AlphaBetaAgent):
    def __init__(self, index):
        CaptureAgent.__init__(self, index)

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)

    def get_features(self, game_state, index=0):
        # type: (GameState, int) -> dict
        agent_state = game_state.getAgentState(self.index)
        my_pos = agent_state.getPosition()
        enemies = [game_state.getAgentState(i) for i in self.getOpponents(game_state)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        num_invaders = len(invaders)

        capsules = self.getCapsulesYouAreDefending(game_state)

        if len(capsules) > 0:
            closest_capsule = min([self.getMazeDistance(my_pos, c) for c in capsules])
        else:
            closest_capsule = 0

        if len(invaders) > 0:
            invader_distance = min([self.getMazeDistance(my_pos, a.getPosition()) for a in invaders])
        else:
            invader_distance = 0

        to_return = {
            'numInvaders': num_invaders,
            'invaderDistance': invader_distance,
            'closestCapsule': closest_capsule
        }

        print "Defense Features: ", to_return

        return to_return

    def get_weights(self, maximizer=True):
        # type: (bool) -> dict

        return {
            "numInvaders": -2000,
            "invaderDistance": -75,
            "closestCapsule": -50
        }
