from typing import Any

from .cards import SPECIES_IDS, card_name
from .scoring_text import as_text


def current_state(obs_dict: dict) -> dict:
    return obs_dict.get("current") or {}


def your_index(obs_dict: dict) -> int:
    return int(current_state(obs_dict).get("yourIndex") or 0)


def your_player(obs_dict: dict) -> dict:
    players = current_state(obs_dict).get("players") or []
    index = your_index(obs_dict)
    if index < len(players):
        return players[index] or {}
    return {}


def zone_cards(obs_dict: dict, zone: str) -> list[dict]:
    cards = your_player(obs_dict).get(zone) or []
    return [card for card in cards if card]


def in_play_cards(obs_dict: dict) -> list[dict]:
    return zone_cards(obs_dict, "active") + zone_cards(obs_dict, "bench")


def setup_relevant_cards(obs_dict: dict) -> list[dict]:
    return in_play_cards(obs_dict) + zone_cards(obs_dict, "hand")


def card_id(card: Any) -> int | None:
    if isinstance(card, dict) and card.get("id") is not None:
        return int(card["id"])
    return None


def option_card(obs_dict: dict, option: dict) -> dict | None:
    area = option.get("area")
    index = option.get("index")
    if index is None:
        return None

    player = your_player(obs_dict)
    if area is None:
        cards = player.get("hand") or []
    elif int(area) == 2:
        cards = player.get("hand") or []
    elif int(area) == 1:
        cards = (obs_dict.get("select") or {}).get("deck") or player.get("deck") or []
    elif int(area) == 3:
        cards = player.get("discard") or []
    elif int(area) == 4:
        cards = player.get("active") or []
    elif int(area) == 5:
        cards = player.get("bench") or []
    elif int(area) == 12:
        cards = current_state(obs_dict).get("looking") or []
    else:
        cards = []

    if int(index) < len(cards):
        return cards[int(index)]
    return None


def option_target(obs_dict: dict, option: dict) -> dict | None:
    area = option.get("inPlayArea")
    index = option.get("inPlayIndex")
    if area is None or index is None:
        return None

    player = your_player(obs_dict)
    if int(area) == 4:
        cards = player.get("active") or []
    elif int(area) == 5:
        cards = player.get("bench") or []
    else:
        cards = []

    if int(index) < len(cards):
        return cards[int(index)]
    return None


def option_name(obs_dict: dict, option: dict) -> str:
    return card_name(card_id(option_card(obs_dict, option)))


def target_name(obs_dict: dict, option: dict) -> str:
    return card_name(card_id(option_target(obs_dict, option)))


def has_species(obs_dict: dict, species: str, include_hand: bool = True) -> bool:
    ids = SPECIES_IDS[species]
    cards = setup_relevant_cards(obs_dict) if include_hand else in_play_cards(obs_dict)
    return any(card_id(card) in ids for card in cards)


def has_species_in_play(obs_dict: dict, species: str) -> bool:
    return has_species(obs_dict, species, include_hand=False)


def count_species(obs_dict: dict, species: str, include_hand: bool = True) -> int:
    ids = SPECIES_IDS[species]
    cards = setup_relevant_cards(obs_dict) if include_hand else in_play_cards(obs_dict)
    return sum(1 for card in cards if card_id(card) in ids)


def count_species_in_play(obs_dict: dict, species: str) -> int:
    return count_species(obs_dict, species, include_hand=False)


def energy_count(card: dict | None) -> int:
    if not isinstance(card, dict):
        return 0
    return len(card.get("energyCards") or card.get("energies") or [])


def attached_energy_ids(card: dict | None) -> list[int]:
    if not isinstance(card, dict):
        return []
    return [card_id(energy) for energy in card.get("energyCards") or []]


def rough_turn(obs_dict: dict) -> int:
    return int(current_state(obs_dict).get("turn") or 0)


def rough_hand_count(obs_dict: dict) -> int | None:
    value = your_player(obs_dict).get("handCount")
    return int(value) if value is not None else None


def option_debug_text(obs_dict: dict, option: dict) -> str:
    text = as_text(option)
    name = option_name(obs_dict, option)
    target = target_name(obs_dict, option)
    if name:
        text += " " + name
    if target:
        text += " target_" + target
    return text
