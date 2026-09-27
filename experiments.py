import argparse
import random
import time
from copy import deepcopy
from pathlib import Path

from game_env import GameEnv
from solution import Solver


def run_planner(testcase, algorithm):
    env = GameEnv(testcase)
    solver = Solver(env)
    initialise = solver.vi_initialise if algorithm == "vi" else solver.pi_initialise
    iterate = solver.vi_iteration if algorithm == "vi" else solver.pi_iteration
    converged = solver.vi_is_converged if algorithm == "vi" else solver.pi_is_converged
    start = time.perf_counter()
    initialise()
    iterations = 0
    while iterations < 1000 and not converged():
        iterate()
        iterations += 1
    elapsed = time.perf_counter() - start
    return env, solver, iterations, elapsed


def trace_most_likely_policy(env, solver):
    state = (env.init_row, env.init_col, 0)
    visited = set()
    path = []
    while not solver._is_terminal(state) and state not in visited:
        visited.add(state)
        path.append(state[:2])
        action = solver._policy.get(state)
        if action is None:
            action = solver._greedy_action(state, solver._values)
        outcomes = solver._outcomes_for(state, action)
        state = max(outcomes, key=lambda outcome: outcome[1])[0]
    path.append(state[:2])
    return path


def classify_route(path):
    top = sum(row == 2 for row, _ in path)
    middle = sum(row == 6 for row, _ in path)
    bottom = sum(row == 10 for row, _ in path)
    candidates = {
        "P1": top,
        "P2": middle,
        "P3": bottom,
    }
    return max(candidates, key=candidates.get) if max(candidates.values()) else "Other"


def sample_policy_routes(env, solver, trials=100):
    route_counts = {"P1": 0, "P2": 0, "P3": 0, "Other": 0}
    completed = 0
    for trial in range(trials):
        random.seed(env.episode_seed + trial)
        state = env.get_init_state()
        path = [(state.row, state.col)]
        for _ in range(200):
            if env.is_solved(state) or env.is_game_over(state):
                break
            action = solver.pi_select_action(state)
            state, _, _ = env.perform_action(state, action)
            path.append((state.row, state.col))
        completed += env.is_solved(state)
        route_counts[classify_route(path)] += 1
    return route_counts, completed / trials


def print_benchmarks(testcases):
    print("case,algorithm,iterations,seconds,seconds_per_iteration")
    for testcase in testcases:
        for algorithm in ("vi", "pi"):
            _, _, iterations, elapsed = run_planner(testcase, algorithm)
            print(f"{Path(testcase).stem},{algorithm.upper()},{iterations},{elapsed:.6f},"
                  f"{elapsed / max(iterations, 1):.6f}")


def print_risk_sweep(testcase):
    base_env = GameEnv(testcase)
    drifts = (0.05, 0.25, 0.45)
    penalties = (5.0, 500.0, 2000.0)
    print("drift / penalty," + ",".join(f"{penalty:.0f}" for penalty in penalties))
    for drift in drifts:
        outcomes = []
        for penalty in penalties:
            env = deepcopy(base_env)
            env.random_drift_prob = drift
            env.game_over_penalty = penalty
            solver = Solver(env)
            solver.pi_initialise()
            while not solver.pi_is_converged():
                solver.pi_iteration()
            route_counts, completion_rate = sample_policy_routes(env, solver)
            start_state = env.get_init_state()
            value = solver._values[solver._encode(start_state)]
            route_summary = "/".join(f"{route}:{route_counts[route]}%" for route in ("P1", "P2", "P3"))
            outcomes.append(f"{route_summary}; solved={completion_rate:.0%}; V={value:.1f}")
        print(f"{drift:.2f}," + ",".join(outcomes))


def main():
    parser = argparse.ArgumentParser(description="Reproduce assignment solver measurements.")
    parser.add_argument("testcases", nargs="*", default=["testcases/L1.txt", "testcases/L2.txt", "testcases/L3.txt"])
    parser.add_argument("--risk-sweep", help="Run the L4 drift/penalty sweep on this testcase")
    args = parser.parse_args()
    print_benchmarks(args.testcases)
    if args.risk_sweep:
        print_risk_sweep(args.risk_sweep)


if __name__ == "__main__":
    main()