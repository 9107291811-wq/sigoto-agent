import os

from .deck import read_deck_csv
from .scoring import score_option


def choose_indices(obs_dict: dict) -> list[int]:
    select = obs_dict.get("select")
    if select is None:
        return read_deck_csv()

    options = select.get("option") or []
    if not options:
        return []

    min_count = int(select.get("minCount") or 0)
    max_count = int(select.get("maxCount") or 0)

    if max_count <= 0:
        max_count = len(options)

    count = max(min_count, min(max_count, len(options)))
    if count <= 0:
        return []

    scored = [(i, score_option(options[i], obs_dict)) for i in range(len(options))]
    ranked = [
        i
        for i, _score in sorted(
            scored,
            key=lambda item: (item[1], -item[0]),
            reverse=True,
        )
    ]

    if os.getenv("SIGOTO_DEBUG") == "1":
        print("select:", select.get("type"), select.get("context"), "count:", count)
        for i, score in sorted(scored, key=lambda item: item[1], reverse=True)[:8]:
            print(" ", score, i, options[i])

    return ranked[:count]


def agent(obs_dict: dict) -> list[int]:
    return choose_indices(obs_dict)
