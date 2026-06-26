import os


DECK_PATHS = (
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
    "/kaggle/working/ptcg-agent/deck.csv",
)


def read_deck_csv() -> list[int]:
    for path in DECK_PATHS:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return [int(line.strip()) for line in file if line.strip()]
    raise FileNotFoundError("deck.csv was not found")
