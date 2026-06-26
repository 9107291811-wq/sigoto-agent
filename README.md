# sigoto-agent

PTCG AI Battle Challenge practice agent.

Local edit loop:

1. Edit this folder with Codex.
2. Commit and push to GitHub.
3. In Kaggle Notebook, clone the latest repo into `/kaggle/working/ptcg-agent`.
4. Run a battle.
5. Export `vis.json`.
6. Open `vis.json` with `visualizer.html`.

Required submission files at top level:

- `main.py`
- `deck.csv`
- `bot/`
- `data/`

`main.py` is intentionally thin. Actual logic lives in `bot/`.
