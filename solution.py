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
        if not self._mdp_built:
            self._build_reachable_mdp()
        self._values = {state: 0.0 for state in self._states}
        self._vi_delta = float('inf')

    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        return self._vi_delta <= self.game_env.epsilon

    def vi_iteration(self):
        """
        Perform a single iteration of Value Iteration (i.e. loop over the state space once).
        """
        max_delta = 0.0
        for state in reversed(self._states):
            if self._is_terminal(state):
                next_value = 0.0
            else:
                next_value = max(self._action_value(outcomes, self._values)
                                 for _, outcomes in self._transition_rows[self._state_index[state]])
            max_delta = max(max_delta, abs(next_value - self._values[state]))
            self._values[state] = next_value
        self._vi_delta = max_delta

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
        return self._values.get(self._encode(state), 0.0)

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
        return self._greedy_action(self._encode(state), self._values)
    
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
        if not self._mdp_built:
            self._build_reachable_mdp()
        seed_values = {state: 0.0 for state in self._states}
        for _ in range(12):
            for state in reversed(self._states):
                if self._is_terminal(state):
                    seed_values[state] = 0.0
                else:
                    seed_values[state] = max(self._action_value(outcomes, seed_values)
                                              for _, outcomes in self._transition_rows[
                                                  self._state_index[state]])
        self._policy = {
            state: self._greedy_action(state, seed_values)
            for state in self._states if self._transition_rows[self._state_index[state]]
        }
        self._values = {state: 0.0 for state in self._states}
        self._pi_converged = False

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
        return self._pi_converged

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
        active_states = [state for state in self._states if not self._is_terminal(state)]
        count = len(active_states)
        rewards = np.zeros(count, dtype=float)
        indices = {state: i for i, state in enumerate(active_states)}
        matrix_rows = list(range(count))
        matrix_cols = list(range(count))
        matrix_data = [1.0] * count

        for row, state in enumerate(active_states):
            for next_state, probability, reward in self._outcomes_for(state, self._policy[state]):
                rewards[row] += probability * reward
                next_index = indices.get(next_state)
                if next_index is not None:
                    matrix_rows.append(row)
                    matrix_cols.append(next_index)
                    matrix_data.append(-self.game_env.gamma * probability)

        if coo_matrix is None:
            matrix = np.zeros((count, count), dtype=float)
            for row, col, value in zip(matrix_rows, matrix_cols, matrix_data):
                matrix[row, col] += value
            evaluated = np.linalg.solve(matrix, rewards)
        else:
            assert coo_matrix is not None and spsolve is not None
            matrix = coo_matrix((matrix_data, (matrix_rows, matrix_cols)), shape=(count, count)).tocsr()
            evaluated = spsolve(matrix, rewards)
        self._values = {state: 0.0 for state in self._states}
        for state, value in zip(active_states, evaluated):
            self._values[state] = float(value)

        improved = {}
        stable = True
        for state in active_states:
            action = self._greedy_action(state, self._values)
            improved[state] = action
            if action != self._policy[state]:
                stable = False
        self._policy = improved
        self._pi_converged = stable

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
        key = self._encode(state)
        if key in self._policy:
            return self._policy[key]
        return self._greedy_action(key, self._values)
    
        # === Helper Methods ===============================================================================================
        #
        #
        # TODO: Add any additional methods here
        #
        #

    def _encode(self, state):
        mask = sum(bit << i for i, bit in enumerate(state.crystal_status))
        return int(state.row), int(state.col), mask

    def _is_terminal(self, state):
        row, col, mask = state
        return (self.game_env.grid_data[row][col] == GameEnv.LAVA_TILE or
            ((row, col) in self._launch_positions and mask.bit_count() >= self.game_env.min_samples))

    def _legal_actions(self, state):
        row, col, _ = state
        if self.game_env.grid_data[row][col] == GameEnv.CRATER_TILE:
            return [action for action in GameEnv.ACTIONS if action in GameEnv.JUMP_ACTIONS]
        return [action for action in GameEnv.ACTIONS
                if action in GameEnv.WALK_ACTIONS or action in GameEnv.BOOST_ACTIONS]

    def _apply_move(self, state, action, distance):
        row, col, mask = state
        if action in GameEnv.JUMP_ACTIONS:
            if self.game_env.grid_data[row][col] != GameEnv.CRATER_TILE:
                return state, 0.0, False
        elif self.game_env.grid_data[row][col] == GameEnv.CRATER_TILE:
            return state, 0.0, False

        reward = -self.game_env.ACTION_COST[action]
        delta_row, delta_col = self._directions[action]
        for _ in range(distance):
            next_row = row + delta_row
            next_col = col + delta_col
            if not (0 <= next_row < self.game_env.n_rows and 0 <= next_col < self.game_env.n_cols and
                    self.game_env.grid_data[next_row][next_col] != GameEnv.ROCK_TILE):
                reward -= self.game_env.collision_penalty
                break
            row, col = next_row, next_col
            tile = self.game_env.grid_data[row][col]
            if tile in (GameEnv.CRATER_TILE, GameEnv.LAVA_TILE):
                break

        crystal_index = self._crystal_indices.get((row, col))
        if crystal_index is not None:
            mask |= 1 << crystal_index
        next_state = (row, col, mask)
        if self.game_env.grid_data[row][col] == GameEnv.LAVA_TILE:
            reward -= self.game_env.game_over_penalty
            return next_state, reward, True
        return next_state, reward, False

    def _outcomes_for(self, state, action):
        for candidate, outcomes in self._transition_rows[self._state_index[state]]:
            if candidate == action:
                return outcomes
        raise ValueError(f'Action {action} is not valid in state {state}')

    def _build_action_outcomes(self, state, action):
        env = self.game_env
        drift_probability = env.random_drift_prob
        direction_options = [(action, 1.0 - drift_probability)]
        direction_options.extend((perpendicular, drift_probability / 2.0)
                                 for perpendicular in env.PERPENDICULAR_ACTIONS[action])
        double_options = [(False, 1.0 - env.random_double_prob), (True, env.random_double_prob)]
        boost_distances = list(enumerate(env.boost_probabilities))
        accumulated = {}

        for movement, movement_probability in direction_options:
            if movement_probability == 0.0:
                continue
            for doubled, double_probability in double_options:
                if double_probability == 0.0:
                    continue
                first_distances = boost_distances if movement in GameEnv.BOOST_ACTIONS else [(1, 1.0)]
                for first_distance, first_probability in first_distances:
                    first_state, first_reward, game_over = self._apply_move(state, movement, first_distance)
                    branch_probability = movement_probability * double_probability * first_probability
                    if doubled and not game_over:
                        second_distances = boost_distances if movement in GameEnv.BOOST_ACTIONS else [(1, 1.0)]
                        for second_distance, second_probability in second_distances:
                            second_state, second_reward, _ = self._apply_move(
                                first_state, movement, second_distance)
                            probability = branch_probability * second_probability
                            entry = accumulated.setdefault(second_state, [0.0, 0.0])
                            entry[0] += probability
                            entry[1] += probability * (first_reward + second_reward)
                    else:
                        entry = accumulated.setdefault(first_state, [0.0, 0.0])
                        entry[0] += branch_probability
                        entry[1] += branch_probability * first_reward

        return tuple((next_state, probability, reward_sum / probability)
                     for next_state, (probability, reward_sum) in accumulated.items())

    def _build_reachable_mdp(self):
        init_row = self.game_env.init_row
        init_col = self.game_env.init_col
        assert init_row is not None and init_col is not None
        initial = (init_row, init_col, 0)
        states = [initial]
        self._state_index = {initial: 0}
        transition_rows = []
        cursor = 0
        while cursor < len(states):
            state = states[cursor]
            action_rows = []
            if not self._is_terminal(state):
                for action in self._legal_actions(state):
                    outcomes = self._build_action_outcomes(state, action)
                    action_rows.append((action, outcomes))
                    for next_state, _, _ in outcomes:
                        if next_state not in self._state_index:
                            self._state_index[next_state] = len(states)
                            states.append(next_state)
            transition_rows.append(action_rows)
            cursor += 1
        self._states = tuple(states)
        self._transition_rows = transition_rows
        self._mdp_built = True

    def _action_value(self, outcomes, values):
        gamma = self.game_env.gamma
        return sum(probability * (reward + gamma * values[next_state])
                   for next_state, probability, reward in outcomes)

    def _greedy_action(self, state, values):
        row = self._state_index.get(state)
        if row is None or not self._transition_rows[row]:
            return GameEnv.WALK_RIGHT
        best_action = self._transition_rows[row][0][0]
        best_value = self._action_value(self._transition_rows[row][0][1], values)
        for action, outcomes in self._transition_rows[row][1:]:
            value = self._action_value(outcomes, values)
            if value > best_value + 1e-12:
                best_action, best_value = action, value
        return best_action


    
    
