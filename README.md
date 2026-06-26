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
