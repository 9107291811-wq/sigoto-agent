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

`main.py` is intentionally thin. Actual logic lives in `bot/`.

## Deck Variants

Deck A and Deck B are separated under `variants/`:

- `variants/deck_a/` is the current baseline deck.
- `variants/deck_b/` is the second deck workspace.

Each variant owns:

- `decklist.json` readable recipe
- `deck.csv` resolved 60-card ID list
- `strategy.md` strategy notes
- `variant_config.json` variant label

Build separate submission files with:

```powershell
cd "C:\Users\K\Documents\New project 8\sigoto-agent"
& "C:\Users\K\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\build_submission.py deck_a
& "C:\Users\K\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\build_submission.py deck_b
```

Outputs:

- `dist/deck_a/submission.tar.gz`
- `dist/deck_b/submission.tar.gz`

To resolve a variant decklist against the official card CSV:

```powershell
& "C:\Users\K\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\resolve_deck.py data --decklist variants\deck_b\decklist.json --output variants\deck_b\deck.csv
```

## Local battle loop

Run local battles before pushing to GitHub or Kaggle:

```powershell
cd "C:\Users\K\Documents\New project 8\sigoto-agent"
& "C:\Users\K\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\local_battle.py --games 3
```

Outputs are written to `local_runs/`:

- `local_vis_001.json`
- `local_vis_002.json`
- `summary.json`

Open a `local_vis_*.json` file with `visualizer.html`.

The script uses the local CABT engine at:

```text
C:\Users\K\Documents\New project 8\kaggle-env-src\kaggle_environments\envs\cabt
```

## Submit To Kaggle

1. Make sure the latest changes are pushed to GitHub.
2. In Kaggle Notebook, run the cells in `notebook_cells.md` to pull the newest agent and make sure one practice battle works.
3. Upload `dist/sigoto-agent-submission.tar.gz` to the competition submission page.

The `.tar.gz` should contain these files at the top level:

- `main.py`
- `deck.csv`
- `bot/`
