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

    ranked = sorted(
        range(len(options)),
        key=lambda i: (score_option(options[i], obs_dict), -i),
        reverse=True,
    )
    return ranked[:count]


def agent(obs_dict: dict) -> list[int]:
    return choose_indices(obs_dict)
