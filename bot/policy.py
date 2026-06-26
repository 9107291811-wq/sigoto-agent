import os

from .deck import read_deck_csv
from .scoring import reset_public_memory, score_option
from .state import card_id, in_play_cards, option_name, rough_turn, your_index
from .cards import card_name


UNIQUE_SETUP_NAMES = {"solrock", "lunatone", "binacle", "barbaracle", "clefairy"}
SETUP_ACTIVE_MEMORY: dict[int, str] = {}


def choose_indices(obs_dict: dict) -> list[int]:
    select = obs_dict.get("select")
    if select is None:
        SETUP_ACTIVE_MEMORY.clear()
        reset_public_memory()
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
    ranked_pairs = sorted(
        scored,
        key=lambda item: (item[1], -item[0]),
        reverse=True,
    )
    ranked = [i for i, _score in ranked_pairs]
    effect = select.get("effect")
    force_optional_pick = effect is not None

    selected: list[int] = []
    allow_duplicate_for_survival = len(in_play_cards(obs_dict)) <= 2
    selected_names: set[str] = set()
    if not allow_duplicate_for_survival:
        selected_names = {
            card_name(card_id(card))
            for card in in_play_cards(obs_dict)
            if card_name(card_id(card)) in UNIQUE_SETUP_NAMES
        }
    player_index = your_index(obs_dict)
    remembered_active = SETUP_ACTIVE_MEMORY.get(player_index)
    if (
        rough_turn(obs_dict) == 0
        and remembered_active in UNIQUE_SETUP_NAMES
        and not allow_duplicate_for_survival
    ):
        selected_names.add(remembered_active)
    for i, score in ranked_pairs:
        if min_count == 0 and score < 0 and not force_optional_pick:
            continue
        name = option_name(obs_dict, options[i])
        if name in UNIQUE_SETUP_NAMES and name in selected_names and len(selected) >= min_count:
            continue
        selected.append(i)
        if name in UNIQUE_SETUP_NAMES:
            selected_names.add(name)
        if len(selected) >= count:
            break

    if len(selected) < min_count:
        selected_set = set(selected)
        selected.extend(
            i for i in ranked if i not in selected_set
        )
        selected = selected[:min_count]

    if os.getenv("SIGOTO_DEBUG") == "1":
        print("select:", select.get("type"), select.get("context"), "count:", count)
        for i, score in sorted(scored, key=lambda item: item[1], reverse=True)[:8]:
            print(" ", score, i, options[i])

    if rough_turn(obs_dict) == 0 and selected:
        selected_option_name = option_name(obs_dict, options[selected[0]])
        if int(select.get("context") or -1) == 1 and selected_option_name in UNIQUE_SETUP_NAMES:
            SETUP_ACTIVE_MEMORY[player_index] = selected_option_name

    return selected


def agent(obs_dict: dict) -> list[int]:
    return choose_indices(obs_dict)
