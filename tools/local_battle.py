import argparse
import json
import os
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CABT_DIR = ROOT.parent / "kaggle-env-src" / "kaggle_environments" / "envs" / "cabt"


def load_deck(path: Path) -> list[int]:
    return [int(line.strip()) for line in path.read_text().splitlines() if line.strip()]


def add_engine_path(cabt_dir: Path) -> None:
    if not (cabt_dir / "cg").exists():
        raise FileNotFoundError(
            f"Could not find cabt engine cg folder: {cabt_dir / 'cg'}"
        )
    sys.path.insert(0, str(cabt_dir))
    sys.path.insert(0, str(ROOT))


def run_one(game_index: int, args: argparse.Namespace) -> dict:
    add_engine_path(args.cabt_dir)

    from cg.game import battle_finish, battle_select, battle_start, visualize_data
    from main import agent

    deck = load_deck(args.deck)
    if len(deck) != 60:
        raise ValueError(f"Deck must have 60 cards, got {len(deck)}: {args.deck}")

    if args.debug:
        os.environ["SIGOTO_DEBUG"] = "1"
    else:
        os.environ.pop("SIGOTO_DEBUG", None)

    obs, start_data = battle_start(deck, deck)
    error_player = getattr(start_data, "errorPlayer", -1)
    if obs is None or error_player >= 0:
        battle_finish()
        raise RuntimeError(f"battle_start failed, errorPlayer={error_player}")

    obs_log = [""]
    action_log = [None]
    steps = 0
    try:
        while obs["current"]["result"] < 0 and steps < args.max_steps:
            action = agent(obs)
            obs.pop("search_begin_input", None)
            obs_log.append(obs)
            action_log.append(action)
            obs = battle_select(action)
            steps += 1

        vis = json.loads(visualize_data())
        for i in range(len(vis)):
            if i < len(obs_log):
                vis[i]["obs"] = obs_log[i]
                vis[i]["action"] = [action_log[i], action_log[i]]

        result = int(obs["current"]["result"])
        out = args.out_dir / f"local_vis_{game_index:03d}.json"
        out.write_text(json.dumps(vis), encoding="utf-8")
        return {"game": game_index, "steps": steps, "result": result, "file": str(out)}
    finally:
        battle_finish()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local CABT battles and export visualizer JSON.")
    parser.add_argument("--games", type=int, default=1, help="Number of battles to run.")
    parser.add_argument("--max-steps", type=int, default=500, help="Stop a battle after this many choices.")
    parser.add_argument("--deck", type=Path, default=ROOT / "deck.csv", help="Deck CSV path.")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "local_runs", help="Output directory.")
    parser.add_argument(
        "--cabt-dir",
        type=Path,
        default=Path(os.environ.get("CABT_DIR", DEFAULT_CABT_DIR)),
        help="Directory containing cabt.py and cg/.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Python random seed.")
    parser.add_argument("--debug", action="store_true", help="Print option scores from the agent.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.cabt_dir = args.cabt_dir.resolve()
    args.deck = args.deck.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.seed is not None:
        random.seed(args.seed)

    summaries = []
    for game_index in range(1, args.games + 1):
        summaries.append(run_one(game_index, args))

    summary_path = args.out_dir / "summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    for item in summaries:
        print(
            f"game={item['game']} result={item['result']} "
            f"steps={item['steps']} file={item['file']}"
        )
    print(f"summary={summary_path}")


if __name__ == "__main__":
    main()
