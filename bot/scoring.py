from typing import Any

from .cards import ENERGY_IDS, FIGHTING_ENERGY_IDS, SPECIAL_ENERGY_IDS, card_name
from .state import (
    attached_energy_ids,
    card_id,
    count_species,
    count_species_in_play,
    energy_count,
    has_species,
    has_species_in_play,
    in_play_cards,
    option_card,
    option_debug_text,
    option_target,
    rough_hand_count,
    rough_turn,
    target_name,
    zone_cards,
)


TYPE_PLAY = 7
TYPE_ATTACH = 8
TYPE_ABILITY = 9
TYPE_PUT_OR_EVOLVE = 10
TYPE_RETREAT = 12
TYPE_ATTACK = 13
TYPE_END = 14

POKEMON_NAMES = {
    "solrock",
    "lunatone",
    "okidogi",
    "binacle",
    "barbaracle",
    "clefairy",
}


CARD_BASE = {
    "solrock": 930,
    "lunatone": 910,
    "okidogi": 880,
    "binacle": 820,
    "barbaracle": 760,
    "clefairy": 740,
    "prism_energy": 560,
    "legacy_energy": 560,
    "basic_fighting_energy": 420,
    "dusk_ball": 900,
    "poke_pad": 880,
    "fighting_gong": 840,
    "night_stretcher": 700,
    "brocks_scouting": 760,
    "urbain": 720,
    "lillies_determination": 700,
    "tarragon": 640,
    "boss_orders": 560,
    "air_balloon": 360,
    "battle_cage": 620,
}


def base_card_score(name: str) -> int:
    return CARD_BASE.get(name, 0)


def setup_active_score(name: str) -> int:
    if name == "okidogi":
        return 1200
    if name == "solrock":
        return 700
    if name == "binacle":
        return 520
    if name == "lunatone":
        return 460
    if name == "clefairy":
        return 420
    return 0


def setup_bench_score(name: str, obs_dict: dict) -> int:
    early = rough_turn(obs_dict) <= 2
    score = 0
    in_play = count_species_in_play(obs_dict, name) if name in POKEMON_NAMES else 0

    if name == "solrock":
        if in_play >= 1:
            return -2000
        score += 1800
        if has_species(obs_dict, "lunatone") and not has_species_in_play(obs_dict, "solrock"):
            score += 1000
    elif name == "lunatone":
        if in_play >= 1:
            return -2000
        score += 1780
        if has_species(obs_dict, "solrock") and not has_species_in_play(obs_dict, "lunatone"):
            score += 1000
    elif name == "okidogi":
        score += 980 if in_play == 0 else (380 if in_play == 1 else -500)
    elif name == "binacle":
        score += 720 if in_play == 0 else -360
    elif name == "barbaracle":
        score += 760 if has_species(obs_dict, "binacle") and in_play == 0 else -500
    elif name == "clefairy":
        score += 560 if in_play == 0 else -260

    if early and name in ("solrock", "lunatone"):
        score += 500
    return score


def search_card_score(name: str, obs_dict: dict) -> int:
    score = 0
    in_play = count_species_in_play(obs_dict, name) if name in POKEMON_NAMES else 0
    total = count_species(obs_dict, name) if name in POKEMON_NAMES else 0

    if name == "solrock":
        if in_play >= 1:
            return -2000
        score += 2200 if total == 0 else 260
        if has_species(obs_dict, "lunatone") and not has_species_in_play(obs_dict, "solrock"):
            score += 1400
    elif name == "lunatone":
        if in_play >= 1:
            return -2000
        score += 2180 if total == 0 else 240
        if has_species(obs_dict, "solrock") and not has_species_in_play(obs_dict, "lunatone"):
            score += 1400
    elif name == "okidogi":
        score += 980 if in_play == 0 else (420 if in_play == 1 else -520)
    elif name == "binacle":
        score += 680 if in_play == 0 else -380
    elif name == "barbaracle":
        score += 760 if has_species(obs_dict, "binacle") and in_play == 0 else -600
    elif name == "clefairy":
        score += 620 if in_play == 0 else -220
    elif name in ("prism_energy", "legacy_energy"):
        score += 420
    elif name == "basic_fighting_energy":
        score += 220
    return score


def play_score(name: str, obs_dict: dict) -> int:
    score = 500 + base_card_score(name)
    if name in ("dusk_ball", "poke_pad"):
        score += 600
    if name == "fighting_gong":
        score += 520
    if name == "battle_cage":
        score += 420
    if name == "air_balloon":
        score -= 120
    hand_count = rough_hand_count(obs_dict)
    if name == "urbain":
        score += 650
    if name == "lillies_determination":
        score += 700 if hand_count is not None and hand_count <= 3 else 260
    if name == "brocks_scouting":
        score += 620
    if name == "tarragon":
        score += 360
    return score


def attach_score(energy_id: int | None, target_card: dict | None, obs_dict: dict) -> int:
    if energy_id not in ENERGY_IDS:
        return -500

    target = card_name(card_id(target_card))
    existing_count = energy_count(target_card)
    existing_ids = attached_energy_ids(target_card)
    has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in existing_ids)
    has_fighting = any(attached_id in FIGHTING_ENERGY_IDS for attached_id in existing_ids)

    if existing_count >= 3:
        return -5000
    if existing_count >= 2:
        return -2600

    score = 0
    if energy_id in SPECIAL_ENERGY_IDS:
        score += 900
        if target == "okidogi":
            score += 1800 if not has_special else -900
        elif target == "clefairy":
            score += 1600 if not has_special else -900
        elif target == "solrock":
            score += 120 if existing_count == 0 else -900
        else:
            score -= 360

    if energy_id in FIGHTING_ENERGY_IDS:
        score += 280
        if target == "okidogi":
            score += 1180 if has_special and not has_fighting else (680 if existing_count == 0 else -900)
        elif target == "clefairy":
            score += 1080 if has_special and not has_fighting else (620 if existing_count == 0 else -900)
        elif target == "solrock" and has_species_in_play(obs_dict, "lunatone"):
            score += 520 if existing_count == 0 else -900
        elif target == "lunatone":
            score -= 600
        elif target in ("binacle", "barbaracle"):
            score -= 420
        else:
            score -= 260

    return score


def attack_score(option: dict, obs_dict: dict) -> int:
    attack_id = option.get("attackId")
    if attack_id is None:
        return 0

    # Known from visual logs: Solrock's Cosmic Beam is 980.
    if int(attack_id) == 980:
        return 900 if has_species_in_play(obs_dict, "lunatone") else 220

    return 620


def score_option(option: Any, obs_dict: dict) -> int:
    if not isinstance(option, dict):
        return 0

    opt_type = int(option.get("type") or -1)
    card = option_card(obs_dict, option)
    cid = card_id(card)
    name = card_name(cid)

    if opt_type == TYPE_END:
        return -250

    if opt_type == TYPE_RETREAT:
        return 120

    if opt_type == TYPE_ATTACK:
        return attack_score(option, obs_dict)

    if opt_type == TYPE_ATTACH:
        return attach_score(cid, option_target(obs_dict, option), obs_dict)

    if opt_type == TYPE_PLAY:
        if name in POKEMON_NAMES:
            return base_card_score(name) + setup_bench_score(name, obs_dict)
        return play_score(name, obs_dict)

    if opt_type == TYPE_ABILITY:
        return 1250

    if opt_type == TYPE_PUT_OR_EVOLVE:
        return base_card_score(name) + setup_bench_score(name, obs_dict)

    # Card selection prompts such as setup, search, and to-hand use card options.
    if name:
        if rough_turn(obs_dict) == 0 and len(zone_cards(obs_dict, "active")) == 0:
            return setup_active_score(name)
        if rough_turn(obs_dict) == 0 and len(in_play_cards(obs_dict)) > 0:
            return setup_bench_score(name, obs_dict)
        return base_card_score(name) + search_card_score(name, obs_dict)

    return 0
