import sys
import time

import numpy as np

try:
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
except ImportError:
    coo_matrix = None
    spsolve = None

from game_env import GameEnv
from game_state import GameState

StateKey = tuple[int, int, int]
Outcome = tuple[StateKey, float, float]
ActionTransitions = list[tuple[str, tuple[Outcome, ...]]]
"""
solution.py

This file is a template you should use to implement your solution.

You should implement each of the method stubs below. You may add additional methods and/or classes to this file if you 
wish. You may also create additional source files and import to this file if you wish.

COMP3702 Assignment 2 "CrystalRover" Support Code

Last updated by vp 09/09/2026
"""


class Solver:

    STUDENT_NAME = "Khairunnisa Rahmahdani Danang" # replace with your name
    STUDENT_ID = "50220353"  # replace with your student ID
    GITHUB_USERNAME = "icha211" # replace with your GitHub username

    def __init__(self, game_env: GameEnv):
        self.game_env = game_env
        self._directions = {
            game_env.WALK_LEFT: (0, -1), game_env.WALK_RIGHT: (0, 1),
            game_env.WALK_UP: (-1, 0), game_env.WALK_DOWN: (1, 0),
            game_env.BOOST_LEFT: (0, -1), game_env.BOOST_RIGHT: (0, 1),
            game_env.BOOST_UP: (-1, 0), game_env.BOOST_DOWN: (1, 0),
            game_env.JUMP_LEFT: (0, -1), game_env.JUMP_RIGHT: (0, 1),
            game_env.JUMP_UP: (-1, 0), game_env.JUMP_DOWN: (1, 0),
        }
        self._crystal_indices = {pos: i for i, pos in enumerate(game_env.crystal_positions)}
        self._launch_positions = set(game_env.launch_positions)
        self._transition_rows: list[ActionTransitions] = []
        self._state_index: dict[StateKey, int] = {}
        self._values: dict[StateKey, float] = {}
        self._policy: dict[StateKey, str] = {}
        self._states: tuple[StateKey, ...] = ()
        self._vi_delta = float('inf')
        self._pi_converged = False
        self._mdp_built = False

    @staticmethod
    def testcases_to_attempt():
        """
        Return a list of testcase numbers you want your solution to be evaluated for.
        """
        # TODO: modify below if desired (e.g. disable larger testcases if you're having problems with RAM usage, etc)
        return [1, 2, 3, 4, 5]

    # === Value Iteration ==============================================================================================
    
        def vi_initialise(self):
            """
            Initialise any variables required before the start of Value Iteration.
            """
            #
            # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
            #  perform value iteration in this method.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def vi_is_converged(self):
            """
            Check if Value Iteration has reached convergence.
            :return: True if converged, False otherwise
            """
            #
            # TODO: Implement code to check if Value Iteration has reached convergence here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def vi_iteration(self):
            """
            Perform a single iteration of Value Iteration (i.e. loop over the state space once).
            """
            #
            # TODO: Implement code to perform a single iteration of Value Iteration here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def vi_plan_offline(self):
            """
            Plan using Value Iteration.
            """
            # !!! In order to ensure compatibility with tester, you should not modify this method !!!
            self.vi_initialise()
            while True:
                self.vi_iteration()
    
                # NOTE: vi_iteration is always called before vi_is_converged
                if self.vi_is_converged():
                    break
    
        def vi_get_state_value(self, state: GameState):
            """
            Retrieve V(s) for the given state.
            :param state: the current state
            :return: V(s)
            """
            #
            # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
            #  value for V(s) has not yet been computed, this function should return 0.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def vi_select_action(self, state: GameState):
            """
            Retrieve the optimal action for the given state (based on values computed by Value Iteration).
            :param state: the current state
            :return: optimal action for the given state (element of ACTIONS)
            """
            #
            # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        # === Policy Iteration =============================================================================================
    
        def pi_initialise(self):
            """
            Initialise any variables required before the start of Policy Iteration.
            """
            #
            # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
            #  perform policy iteration in this method. You can assume an initial policy of always applying WALK_RIGHT.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def pi_is_converged(self):
            """
            Check if Policy Iteration has reached convergence.
            :return: True if converged, False otherwise
            """
            #
            # TODO: Implement code to check if Policy Iteration has reached convergence here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def pi_iteration(self):
            """
            Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
            policy improvement).
            """
            #
            # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        def pi_plan_offline(self):
            """
            Plan using Policy Iteration.
            """
            # !!! In order to ensure compatibility with tester, you should not modify this method !!!
            self.pi_initialise()
            while True:
                self.pi_iteration()
    
                # NOTE: pi_iteration is always called before pi_is_converged
                if self.pi_is_converged():
                    break
    
        def pi_select_action(self, state: GameState):
            """
            Retrieve the optimal action for the given state (based on values computed by Value Iteration).
            :param state: the current state
            :return: optimal action for the given state (element of ACTIONS)
            """
            #
            # TODO: Implement code to return an action for the given state (based on your stored PI policy) here.
            #
            # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
            #
            pass
    
        # === Helper Methods ===============================================================================================
        #
        #
        # TODO: Add any additional methods here
        #
        #
    
    