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

#################
# Team creation #
#################

infinity = float('inf')


def createTeam(firstIndex, secondIndex, isRed,
               first='AlphaBetaAgent', second='DefensiveAgent'):
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

def alpha_beta_cutoff_search(game_state, d=4, eval_fn=None, max_player_index=0):
    player = max_player_index

    def max_value(st, alpha, beta, depth, player):
        # type: (GameState, int, int, int, int) -> int

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
        # type: (GameState, int, int, int, int) -> int

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

    def cutoff_test(st, depth):
        # type: (GameState, int) -> bool
        return depth > d or st.isOver()

    eval_fn = eval_fn
    best_score = -infinity
    beta = infinity
    best_action = None

    acs = game_state.getLegalActions(player)
    for ac in acs:
        v = min_value(game_state.generateSuccessor(player, ac), best_score, beta, 1, player + 1)

        if v > best_score:
            best_score = v
            best_action = ac
    print "Best action: ", best_action
    return best_action


class DefensiveAgent(CaptureAgent):
    def __init__(self, index):
        self.index = index
        self.observationHistory = []

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1
        if (successor.getAgentState(self.index).scaredTimer > 0):
            features['numInvaders'] = 0
            if (features['invaderDistance'] <= 2): features['invaderDistance'] = 2
        teamNums = self.getTeam(gameState)
        initPos = gameState.getInitialAgentPosition(teamNums[0])
        # use the minimum noisy distance between our agent and their agent
        features['DistancefromStart'] = myPos[0] - initPos[0]
        if (features['DistancefromStart'] < 0): features['DistancefromStart'] *= -1
        if (features['DistancefromStart'] >= 10): features['DistancefromStart'] = 10
        if (features['DistancefromStart'] <= 4): features['DistancefromStart'] += 1
        if (features['DistancefromStart'] == 1):
            features['DistancefromStart'] == -9999
        features['DistancefromStart'] *= 2.5
        features['stayApart'] = self.getMazeDistance(gameState.getAgentPosition(teamNums[0]),
                                                     gameState.getAgentPosition(teamNums[1]))
        features['onDefense'] = 1
        features['offenseFood'] = 0

        if myState.isPacman:
            features['onDefense'] = -1

        if (len(invaders) == 0 and successor.getScore() != 0):
            features['onDefense'] = -1
            features['offenseFood'] = min(
                [self.getMazeDistance(myPos, food) for food in self.getFood(successor).asList()])
            features['foodCount'] = len(self.getFood(successor).asList())
            features['DistancefromStart'] = 0
            features['stayAprts'] += 2
            features['stayApart'] *= features['stayApart']
        if (len(invaders) != 0):
            features['stayApart'] = 0
            features['DistancefromStart'] = 0
        return features

    def getWeights(self, gameState, action):
        return {'foodCount': -20, 'offenseFood': -1, 'DistancefromStart': 3, 'numInvaders': -40000, 'onDefense': 20,
                'stayApart': 45, 'invaderDistance': -1800, 'stop': -400, 'reverse': -250}


class AlphaBetaAgent(CaptureAgent):
    def __init__(self, index):
        CaptureAgent.__init__(self, index)

        self.index = index
        self.observationHistory = []

        self.isRed = False

    def registerInitialState(self, game_state):
        # type: (GameState) -> None
        CaptureAgent.registerInitialState(self, game_state)
        if self.index in game_state.getRedTeamIndices():
            self.isRed = True
        else:
            self.isRed = False

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def get_successor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def get_weights(self, gameState, action):
        return {'eatInvader': 5, 'closeInvader': 0, 'teammateDist': 1.5, 'nearbyFood': -1, 'eatCapsule': 10.0,
                'normalGhosts': -20, 'eatGhost': 1.0, 'scaredGhosts': 0.1, 'stuck': -5, 'eatFood': 1}

    def get_features(self, game_state, action):
        # type: (GameState, Actions) -> util.Counter
        features = util.Counter()
        successor = self.get_successor(game_state, action)

        # Get other variables for later use
        food = self.getFood(game_state)
        capsules = game_state.getCapsules()
        foodList = food.asList()
        walls = game_state.getWalls()
        x, y = game_state.getAgentState(self.index).getPosition()
        vx, vy = Actions.directionToVector(action)
        newx = int(x + vx)
        newy = int(y + vy)

        # Get set of invaders and defenders
        enemies = [game_state.getAgentState(a) for a in self.getOpponents(game_state)]
        invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        defenders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        # Check if pacman has stopped
        if action == Directions.STOP:
            features["stuck"] = 1.0

        # Get ghosts close by
        for ghost in invaders:
            ghostpos = ghost.getPosition()
            neighbors = Actions.getLegalNeighbors(ghostpos, walls)
            if (newx, newy) == ghostpos:
                if ghost.scaredTimer == 0:
                    features["scaredGhosts"] = 0
                    features["normalGhosts"] = 1
                else:
                    features["eatFood"] += 2
                    features["eatGhost"] += 1
            elif ((newx, newy) in neighbors) and (ghost.scaredTimer > 0):
                features["scaredGhosts"] += 1
            elif (successor.getAgentState(self.index).isPacman) and (ghost.scaredTimer > 0):
                features["scaredGhosts"] = 0
                features["normalGhosts"] += 1

        # How to act if scared or not scared
        if game_state.getAgentState(self.index).scaredTimer == 0:
            for ghost in defenders:
                ghostpos = ghost.getPosition()
                neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                if (newx, newy) == ghostpos:
                    features["eatInvader"] = 1
                elif (newx, newy) in neighbors:
                    features["closeInvader"] += 1
        else:
            for ghost in enemies:
                if ghost.getPosition() != None:
                    ghostpos = ghost.getPosition()
                    neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                    if (newx, newy) in neighbors:
                        features["closeInvader"] += -10
                        features["eatInvader"] = -10
                    elif (newx, newy) == ghostpos:
                        features["eatInvader"] = -10

        # Get capsules when nearby
        for cx, cy in capsules:
            if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
                features["eatCapsule"] = 1.0

        # When to eat
        if not features["normalGhosts"]:
            if food[newx][newy]:
                features["eatFood"] = 1.0
            if len(foodList) > 0:
                tempFood = []
                for food in foodList:
                    food_x, food_y = food
                    adjustedindex = self.index - self.index % 2
                    check1 = food_y > (adjustedindex / 2) * walls.height / 3
                    check2 = food_y < ((adjustedindex / 2) + 1) * walls.height / 3
                    if (check1 and check2):
                        tempFood.append(food)
                if len(tempFood) == 0:
                    tempFood = foodList
                mazedist = [self.getMazeDistance((newx, newy), food) for food in tempFood]
                if min(mazedist) is not None:
                    walldimensions = walls.width * walls.height
                    features["nearbyFood"] = float(min(mazedist)) / walldimensions
        features.divideAll(10.0)

        return features

    def evaluate(self, gameState, action):
        features = self.get_features(gameState, action)
        weights = self.get_weights(gameState, action)
        return features * weights


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
