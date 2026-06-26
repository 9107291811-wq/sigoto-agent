# Kaggle Notebook Cells

## 1. Pull Latest Agent From GitHub

Run this whenever you want Kaggle to use the latest local changes that you pushed to GitHub.

```python
from pathlib import Path
import shutil
import os

REPO_URL = "https://github.com/9107291811-wq/sigoto-agent.git"

agent_dir = Path("/kaggle/working/ptcg-agent")

if agent_dir.exists():
    shutil.rmtree(agent_dir)

!git clone --depth 1 {REPO_URL} /kaggle/working/ptcg-agent

print("files:", os.listdir(agent_dir))
print("bot files:", os.listdir(agent_dir / "bot"))
print("deck lines:", len((agent_dir / "deck.csv").read_text().splitlines()))
```

## 2. Run One Practice Battle And Export vis.json

```python
import os, sys, json, importlib, random
from pathlib import Path
from kaggle_environments import make

AGENT_DIR = Path("/kaggle/working/ptcg-agent")
os.chdir(AGENT_DIR)

if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

import main
importlib.reload(main)

deck = []
for line in (AGENT_DIR / "deck.csv").read_text().splitlines():
    line = line.strip()
    if line:
        deck.append(int(line))

seed = random.randint(0, 999999)
env = make("cabt", configuration={"decks": [deck, deck], "seed": seed})
env.run([main.agent, main.agent])

vis = env.steps[0][0]["visualize"]

out = Path("/kaggle/working/vis.json")
out.write_text(json.dumps(vis), encoding="utf-8")

print("seed:", seed)
print("created:", out)
```

## 3. Create visualizer.html

You only need to create/download this once.

```python
from pathlib import Path

html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>visualizer</title>
</head>
<body>
    <div>Choose vis.json</div>
    <input type="file" id="fileInput">
    <script>
        document.getElementById('fileInput').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const obj = JSON.parse(e.target.result);

                const input = document.createElement("input");
                input.type = "hidden";
                input.name = "json";

                if ("steps" in obj) {
                    input.value = JSON.stringify(obj["steps"][0][0]["visualize"]);
                } else {
                    input.value = e.target.result;
                }

                const form = document.createElement("form");
                form.method = "POST";
                form.action = "https://ptcgvis.heroz.jp/Visualizer/Replay/0";
                form.target = "_blank";
                form.appendChild(input);

                document.body.appendChild(form);
                form.submit();
            };
            reader.readAsText(file);
        });
    </script>
</body>
</html>'''

Path("/kaggle/working/visualizer.html").write_text(html, encoding="utf-8")
print("created: /kaggle/working/visualizer.html")
```

## Routine

1. Codex edits local `sigoto-agent`.
2. Push changes to GitHub.
3. Kaggle cell 1 pulls latest code.
4. Kaggle cell 2 creates fresh `vis.json`.
5. Download `vis.json`.
6. Open local `visualizer.html` and choose `vis.json`.
