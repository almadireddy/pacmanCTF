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
        if not is_pac_man:
            opposite = game_state.data.layout.getFurthestCorner(self.startPosition)
            distance_to_minimize = self.getMazeDistance(game_state.getAgentPosition(index),
                                                        opposite)
        else:
            if agent_state.numCarrying > 5:
                distance_to_minimize = self.getMazeDistance(game_state.getAgentPosition(index),
                                                            self.startPosition)
            else:
                distance_to_minimize = distance_to_food

        to_return = {
            'score': score,
            'distanceFromStart': distance_from_start,
            'closestFood': distance_to_food,
            'isPacMan': 1 if is_pac_man else 0,
            'numCarrying': num_carrying,
            'foodRemaining': food_remaining,
            'distanceToMinimize': distance_to_minimize
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
                'numCarrying': 250,
                'foodRemaining': -500
            }


class DefenseAgent(AlphaBetaAgent):
    def __init__(self, index):
        CaptureAgent.__init__(self, index)

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)

    def chooseAction(self, game_state):
        # type: (GameState) -> str
        legal_actions = game_state.getLegalActions(self.index)
        return legal_actions[random.randint(0, len(legal_actions)-1)]


class OldABAgent(CaptureAgent):
    def __init__(self, index, offense=True):
        CaptureAgent.__init__(self, index)

        self.index = index
        self.friendlyIndex = [index, (index + 2) % 4]
        self.enemyIndex = [index + 1, (index + 3) % 4]
        self.offense = offense

        self.observationHistory = []
        self.offenseWeights = {'closestFood': -10.0, 'foodRemaining': -5, 'score': -100}

        self.defenseWeights = {'foodCount': -20, 'offenseFood': -1, 'distanceFromStart': 3, 'numInvaders': -40000,
                               'onDefense': 20, 'stayApart': 45, 'invaderDistance': -1800,
                               'stop': -400, 'reverse': -250}
        self.isRed = False

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)

        if self.index in game_state.getRedTeamIndices():
            self.isRed = True
        else:
            self.isRed = False

    def evaluate_state(self, state, index, max):
        # type: (GameState, int, bool) -> float
        if index in self.friendlyIndex:
            if index == self.index:
                if self.offense:
                    return self.evaluate_offense(state, index, max)
                else:
                    return self.evaluate_defense(state, index, max)
            else:
                if self.offense:
                    return self.evaluate_defense(state, index, max)
                else:
                    return self.evaluate_offense(state, index, max)

        else:
            return self.evaluate_offense(state, index, max)

    def chooseAction(self, game_state):
        # type: (GameState) -> Actions
        def alpha_beta_cutoff_search(state, d=4):
            player = self.index

            def max_value(st, alpha, beta, depth, index):
                # type: (GameState, float, float, int, int) -> float
                index = index % 4

                if cutoff_test(st, depth):
                    return self.evaluate_state(st, index, True)

                val = -infinity
                for action in st.getLegalActions(index):
                    val = max(val,
                              min_value(st.generateSuccessor(index, action),
                                        alpha, beta, depth + 1, index + 1))

                    if val >= beta:
                        return val

                    alpha = max(alpha, val)

                return val

            def min_value(st, alpha, beta, depth, index):
                # type: (GameState, float, float, int, int) -> float
                index = index % 4

                if cutoff_test(st, depth):
                    return self.evaluate_state(st, index, False)

                val = infinity

                for action in st.getLegalActions(index):
                    val = min(val,
                              max_value(st.generateSuccessor(index, action),
                                        alpha, beta, depth + 1, index + 1))

                    if val <= alpha:
                        return val

                    beta = min(beta, val)

                return val

            def cutoff_test(st, depth):
                # type: (GameState, int) -> bool
                return depth >= d or st.isOver()

            best_score = -infinity
            b = infinity
            best_action = None

            acs = state.getLegalActions(player)
            print "My index: ", self.index
            for ac in acs:
                v = min_value(state.generateSuccessor(player, ac), best_score, b, 0, self.index)
                print "Action: ", ac, " | Value: ", v
                if v > best_score:
                    best_score = v
                    best_action = ac

            print "Best Action: ", best_action
            return best_action

        return alpha_beta_cutoff_search(game_state, 10)

    def get_offensive_features(self, game_state, index, max):
        # type: (GameState, int, bool) -> util.Counter
        features = util.Counter()

        # Get other variables for later use
        food = self.getFood(game_state)
        food_list = food.asList()
        walls = game_state.getWalls()
        if index in game_state.getRedTeamIndices():
            opponents = game_state.getBlueTeamIndices()
        else:
            opponents = game_state.getRedTeamIndices()

        min_distance = infinity
        for x, y in food_list:
            dist = self.getMazeDistance((x, y), game_state.getAgentPosition(index))
            if dist < min_distance:
                min_distance = dist

        features['closestFood'] = min_distance

        features['foodRemaining'] = len(food_list)

        features['score'] = self.getScore(game_state)

        features.divideAll(10.0)

        return features

    def get_defensive_features(self, game_state, action=Directions.STOP):
        # type: (GameState, str) -> util.Counter
        features = util.Counter()
        my_state = game_state.getAgentState(self.index)
        my_pos = my_state.getPosition()
        enemies = [game_state.getAgentState(i) for i in self.getOpponents(game_state)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(my_pos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        rev = Directions.REVERSE[game_state.getAgentState(self.index).configuration.direction]

        if game_state.getAgentState(self.index).scaredTimer > 0:
            features['numInvaders'] = 0
            if features['invaderDistance'] <= 2:
                features['invaderDistance'] = 2
        team_nums = self.getTeam(game_state)
        init_pos = game_state.getInitialAgentPosition(team_nums[0])
        # use the minimum noisy distance between our agent and their agent

        features['distanceFromStart'] = my_pos[0] - init_pos[0]
        if features['distanceFromStart'] < 0:
            features['distanceFromStart'] *= -1

        if features['distanceFromStart'] >= 10:
            features['distanceFromStart'] = 10

        if features['distanceFromStart'] <= 4:
            features['distanceFromStart'] += 1

        features['distanceFromStart'] *= 2.5

        features['stayApart'] = self.getMazeDistance(game_state.getAgentPosition(team_nums[0]),
                                                     game_state.getAgentPosition(team_nums[1]))
        features['onDefense'] = 1
        features['offenseFood'] = 0

        if my_state.isPacman:
            features['onDefense'] = -1

        if len(invaders) == 0 and game_state.getScore() != 0:
            features['onDefense'] = -1
            features['offenseFood'] = min(
                [self.getMazeDistance(my_pos, food) for food in self.getFood(game_state).asList()])
            features['foodCount'] = len(self.getFood(game_state).asList())
            features['distanceFromStart'] = 0
            features['stayApart'] += 2
            features['stayApart'] *= features['stayApart']

        if len(invaders) != 0:
            features['stayApart'] = 0
            features['distanceFromStart'] = 0

        return features

    def get_offensive_weights(self, gameState, index, max):
        # type: (GameState, int, bool) -> dict
        if max:
            new_dict = {}
            for x in self.offenseWeights:
                new_dict[x] = -self.offenseWeights[x]
            return new_dict

        return self.offenseWeights

    def get_defensive_weights(self, game_state, index):
        # type: (GameState, int) -> dict
        if index not in self.friendlyIndex:
            new_dict = {}
            for x in self.defenseWeights:
                new_dict[x] = -self.defenseWeights[x]
            return new_dict
        return self.defenseWeights

    def evaluate_offense(self, game_state, index, max):
        # type: (GameState, int, bool) -> float
        features = self.get_offensive_features(game_state, index, max)
        weights = self.get_offensive_weights(game_state, index, max)
        # print "Offense: ", index, " | ", features*weights
        return features * weights

    def evaluate_defense(self, game_state, index, max):
        # type: (GameState, int, bool) -> float
        features = self.get_defensive_features(game_state)
        weights = self.get_defensive_weights(game_state, index)
        # print "Defense: ", index, " | ", features*weights
        return features * weights
