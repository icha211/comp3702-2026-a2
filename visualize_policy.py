import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch, Rectangle

from game_env import GameEnv
from solution import Solver


TILE_COLORS = {
    GameEnv.GROUND_TILE: "#f4f2e9",
    GameEnv.ROCK_TILE: "#414a4d",
    GameEnv.CRATER_TILE: "#9a755b",
    GameEnv.LAVA_TILE: "#dc593d",
    GameEnv.LAUNCH_TILE: "#55a58b",
}
ACTION_MARKS = {
    "L": "<-", "R": "->", "U": "^", "D": "v",
}


def main():
    parser = argparse.ArgumentParser(description="Render a solved CrystalRover policy and value map.")
    parser.add_argument("testcase", help="Testcase path, for example testcases/L1.txt")
    parser.add_argument("--solver", choices=("vi", "pi"), default="vi")
    parser.add_argument("--iteration", type=int, help="Render after this many algorithm iterations")
    parser.add_argument("--output", default="artifacts/policy-values.png")
    parser.add_argument("--show", action="store_true", help="Open the rendered figure after saving it")
    args = parser.parse_args()

    env = GameEnv(args.testcase)
    solver = Solver(env)
    if args.solver == "vi":
        if args.iteration is None:
            solver.vi_plan_offline()
            iterations_run = None
        else:
            solver.vi_initialise()
            iterations_run = 0
            while iterations_run < args.iteration and not solver.vi_is_converged():
                solver.vi_iteration()
                iterations_run += 1
        choose_action = solver.vi_select_action
    else:
        if args.iteration is None:
            solver.pi_plan_offline()
            iterations_run = None
        else:
            solver.pi_initialise()
            iterations_run = 0
            while iterations_run < args.iteration and not solver.pi_is_converged():
                solver.pi_iteration()
                iterations_run += 1
        choose_action = solver.pi_select_action

    figure, axis = plt.subplots(figsize=(max(8, env.n_cols * 0.72), max(4, env.n_rows * 0.72)))
    axis.set_facecolor("#252b2d")
    norm = Normalize(vmin=min(solver._values.values()), vmax=max(solver._values.values()))
    value_map = plt.get_cmap("viridis")

    for row in range(env.n_rows):
        for col in range(env.n_cols):
            tile = env.grid_data[row][col]
            if tile in (GameEnv.GROUND_TILE, GameEnv.CRYSTAL_TILE):
                if candidates := [state for state in solver._states if state[:2] == (row, col)]:
                    state_key = min(candidates, key=lambda candidate: candidate[2].bit_count())
                    fill = value_map(norm(solver._values[state_key]))
                else:
                    state_key = None
                    fill = TILE_COLORS[GameEnv.GROUND_TILE]
            else:
                state_key = None
                fill = TILE_COLORS.get(tile, TILE_COLORS[GameEnv.GROUND_TILE])

            axis.add_patch(Rectangle((col, row), 1, 1, facecolor=fill,
                                     edgecolor="#d8d8d0", linewidth=0.65))
            if (row, col) in env.crystal_positions:
                axis.text(col + 0.5, row + 0.32, "C", ha="center", va="center",
                          fontsize=11, fontweight="bold", color="#4b3d10")
            elif (row, col) in env.launch_positions:
                axis.text(col + 0.5, row + 0.32, "E", ha="center", va="center",
                          fontsize=11, fontweight="bold", color="#103f35")
            elif (row, col) in env.lava_positions:
                axis.text(col + 0.5, row + 0.32, "L", ha="center", va="center",
                          fontsize=11, fontweight="bold", color="white")
            elif tile == GameEnv.ROCK_TILE:
                axis.text(col + 0.5, row + 0.5, "R", ha="center", va="center",
                          fontsize=9, color="white")
            elif tile == GameEnv.CRATER_TILE:
                axis.text(col + 0.5, row + 0.5, "*", ha="center", va="center",
                          fontsize=12, color="white")

            if state_key is not None:
                state = type(env.get_init_state())(row, col, tuple(
                    (state_key[2] >> index) & 1 for index in range(env.n_crystals)))
                action = choose_action(state)
                kind = action[0].upper()
                direction = action[1:].upper()
                mark = ACTION_MARKS[direction]
                axis.text(col + 0.5, row + 0.12, f"{solver._values[state_key]:.1f}",
                          ha="center", va="center", fontsize=6.5, color="#17201d")
                axis.text(col + 0.5, row + 0.69, f"{kind}{mark}", ha="center", va="center",
                          fontsize=7.0, color="#ffffff",
                          fontweight="bold")

    axis.scatter(env.init_col + 0.5, env.init_row + 0.5, marker="o", s=100,
                 facecolors="none", edgecolors="#efcf4a", linewidths=2, label="Start")
    axis.set_xlim(0, env.n_cols)
    axis.set_ylim(env.n_rows, 0)
    axis.set_aspect("equal")
    axis.set_xticks(range(env.n_cols + 1))
    axis.set_yticks(range(env.n_rows + 1))
    axis.set_xticklabels([])
    axis.set_yticklabels([])
    axis.tick_params(length=0)
    iteration_label = "converged" if iterations_run is None else f"iteration {iterations_run}"
    axis.set_title(f"{Path(args.testcase).stem} | {args.solver.upper()} {iteration_label}",
                   loc="left", fontsize=14, fontweight="bold", pad=12)

    scalar = plt.cm.ScalarMappable(norm=norm, cmap=value_map)
    figure.colorbar(scalar, ax=axis, fraction=0.025, pad=0.025, label="Expected discounted return")
    legend = [Patch(facecolor=TILE_COLORS[GameEnv.ROCK_TILE], label="Rock"),
              Patch(facecolor=TILE_COLORS[GameEnv.CRATER_TILE], label="Crater"),
              Patch(facecolor=TILE_COLORS[GameEnv.LAVA_TILE], label="Lava"),
              Patch(facecolor=TILE_COLORS[GameEnv.LAUNCH_TILE], label="Launch")]
    axis.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.035),
                ncol=4, frameon=False)
    figure.tight_layout()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    print(f"Saved {output}")
    if args.show:
        plt.show()
    plt.close(figure)


if __name__ == "__main__":
    main()