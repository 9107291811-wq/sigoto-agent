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
    hand_cards,
    in_play_cards,
    option_card,
    opponent_zone_cards,
    option_target,
    rough_hand_count,
    rough_turn,
    zone_cards,
)


TYPE_PLAY = 7
TYPE_ATTACH = 8
TYPE_ABILITY = 9
TYPE_PUT_OR_EVOLVE = 10
TYPE_RETREAT = 12
TYPE_ATTACK = 13
TYPE_END = 14
AIR_BALLOON_ID = 1174
CLEFAIRY_EX_ID = 272

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
    "prism_energy": 540,
    "legacy_energy": 620,
    "basic_fighting_energy": 420,
    "dusk_ball": 900,
    "poke_pad": 880,
    "fighting_gong": 840,
    "night_stretcher": 700,
    "brocks_scouting": 760,
    "urbain": 720,
    "hilda": 760,
    "mortys_conviction": 720,
    "lillies_determination": 700,
    "tarragon": 640,
    "boss_orders": 560,
    "air_balloon": 360,
    "battle_cage": 620,
}


def base_card_score(name: str) -> int:
    return CARD_BASE.get(name, 0)


def has_energy_in_hand(obs_dict: dict) -> bool:
    return any(card_id(card) in ENERGY_IDS for card in hand_cards(obs_dict))


def has_basic_fighting_in_hand(obs_dict: dict) -> bool:
    return any(card_id(card) in FIGHTING_ENERGY_IDS for card in hand_cards(obs_dict))


def has_support_in_hand(obs_dict: dict, name: str) -> bool:
    return any(card_name(card_id(card)) == name for card in hand_cards(obs_dict))


def has_energy_search_in_hand(obs_dict: dict) -> bool:
    names = {card_name(card_id(card)) for card in hand_cards(obs_dict)}
    return bool(names & {"fighting_gong", "night_stretcher", "hilda", "tarragon"})


def active_cards(obs_dict: dict) -> list[dict]:
    return zone_cards(obs_dict, "active")


def bench_cards(obs_dict: dict) -> list[dict]:
    return zone_cards(obs_dict, "bench")


def opponent_active_cards(obs_dict: dict) -> list[dict]:
    return opponent_zone_cards(obs_dict, "active")


def opponent_bench_cards(obs_dict: dict) -> list[dict]:
    return opponent_zone_cards(obs_dict, "bench")


def total_hp_left(card: dict | None) -> int:
    if not isinstance(card, dict):
        return 999
    hp = card.get("hp")
    if hp is not None:
        return int(hp)
    max_hp = card.get("maxHp")
    damage = card.get("damage") or 0
    if max_hp is not None:
        return max(0, int(max_hp) - int(damage))
    return 999


def is_active_card(obs_dict: dict, card: dict | None) -> bool:
    return any(card is active for active in active_cards(obs_dict))


def has_air_balloon(card: dict | None) -> bool:
    if not isinstance(card, dict):
        return False
    return any(card_id(tool) == AIR_BALLOON_ID for tool in card.get("tools") or [])


def target_energy_need(card: dict | None) -> int:
    name = card_name(card_id(card))
    if name in ("okidogi", "clefairy"):
        return 2
    if name == "solrock":
        return 1
    if name in ("binacle", "barbaracle"):
        return 1
    return 0


def is_attack_ready(card: dict | None, obs_dict: dict) -> bool:
    name = card_name(card_id(card))
    attached = attached_energy_ids(card)
    count = energy_count(card)
    has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached)
    if name in ("okidogi", "clefairy"):
        return count >= 2 and has_special
    if name == "solrock":
        return count >= 1 and has_species_in_play(obs_dict, "lunatone")
    return False


def is_one_energy_away(card: dict | None, obs_dict: dict) -> bool:
    name = card_name(card_id(card))
    attached = attached_energy_ids(card)
    count = energy_count(card)
    has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached)
    if name in ("okidogi", "clefairy"):
        return count == 1 and has_special
    if name == "solrock":
        return count == 0 and has_species_in_play(obs_dict, "lunatone")
    return False


def best_ready_attacker_damage(obs_dict: dict, include_retreat: bool = True) -> int:
    candidates = list(active_cards(obs_dict))
    if include_retreat:
        candidates += bench_cards(obs_dict)
    best = 0
    for card in candidates:
        name = card_name(card_id(card))
        if not is_attack_ready(card, obs_dict):
            continue
        if name == "okidogi":
            best = max(best, 170)
        elif name == "clefairy":
            your_bench = len(bench_cards(obs_dict))
            opp_bench = len(opponent_bench_cards(obs_dict))
            best = max(best, (your_bench + opp_bench) * 20)
        elif name == "solrock":
            best = max(best, 70)
    return best


def has_ready_bench_attacker(obs_dict: dict) -> bool:
    return any(is_attack_ready(card, obs_dict) for card in bench_cards(obs_dict))


def active_is_ready_attacker(obs_dict: dict) -> bool:
    return any(is_attack_ready(card, obs_dict) for card in active_cards(obs_dict))


def needs_lunatone_draw_now(obs_dict: dict) -> bool:
    if not has_species_in_play(obs_dict, "solrock") or not has_species_in_play(obs_dict, "lunatone"):
        return False
    if not has_basic_fighting_in_hand(obs_dict):
        return False
    hand_names = {card_name(card_id(card)) for card in hand_cards(obs_dict)}
    return "fighting_gong" in hand_names or "night_stretcher" in hand_names


def boss_priority_target(card: dict | None, obs_dict: dict) -> bool:
    if not isinstance(card, dict):
        return False
    if card_id(card) == CLEFAIRY_EX_ID and total_hp_left(card) <= best_ready_attacker_damage(obs_dict):
        return True
    opponent_cards = opponent_active_cards(obs_dict) + opponent_bench_cards(obs_dict)
    max_energy = max((energy_count(opponent_card) for opponent_card in opponent_cards), default=0)
    if max_energy > 0 and energy_count(card) == max_energy and total_hp_left(card) <= best_ready_attacker_damage(obs_dict):
        return True
    # Retreat cost is not exposed in the local observation, so keep Boss conservative
    # unless a clear prize-taking target exists.
    return False


def boss_has_priority_target(obs_dict: dict) -> bool:
    if any(boss_priority_target(card, obs_dict) for card in opponent_active_cards(obs_dict)):
        return False
    return any(boss_priority_target(card, obs_dict) for card in opponent_bench_cards(obs_dict))


def boss_target_score(option: dict, obs_dict: dict) -> int:
    index = option.get("index")
    bench = opponent_bench_cards(obs_dict)
    if index is None or int(index) >= len(bench):
        return -2500
    target = bench[int(index)]
    if not boss_priority_target(target, obs_dict):
        return -2500
    return 4000 + energy_count(target) * 350


def morty_discard_score(card: dict | None, obs_dict: dict) -> int:
    name = card_name(card_id(card))
    if name in ("solrock", "lunatone", "binacle", "barbaracle"):
        if count_species_in_play(obs_dict, name) >= 1:
            return 3600
    if name == "battle_cage":
        return 3300
    if name == "air_balloon":
        return 3000
    if name == "basic_fighting_energy":
        if any(is_attack_ready(card_in_play, obs_dict) for card_in_play in in_play_cards(obs_dict)):
            return 2700
        return 600
    if name in ("poke_pad", "dusk_ball"):
        attackers = {"okidogi", "clefairy"}
        if not any(card_name(card_id(card_in_play)) in attackers for card_in_play in in_play_cards(obs_dict)):
            return 500
        return 2400
    if name in ("boss_orders", "lillies_determination", "brocks_scouting", "tarragon"):
        return 2000
    if name == "hilda" and not hilda_is_high_value(obs_dict):
        return 1900
    if name == "mortys_conviction":
        return 1700
    return 1000


def lillie_return_score(card: dict | None, obs_dict: dict) -> int:
    name = card_name(card_id(card))
    if name == "barbaracle" and can_evolve_barbaracle_now(obs_dict):
        return -5000
    if name == "binacle" and not has_species_in_play(obs_dict, "binacle"):
        return -2600
    if name in ("okidogi", "clefairy"):
        if count_species_in_play(obs_dict, name) == 0:
            return -3000
        return -800
    if name in ("legacy_energy", "prism_energy"):
        if attacker_needs_high_value_energy(obs_dict):
            return -3200
        return 300
    if name == "basic_fighting_energy":
        if needs_lunatone_draw_now(obs_dict) or one_energy_from_attack_ready(obs_dict):
            return -1600
        return 800
    if name in ("solrock", "lunatone"):
        if not has_species_in_play(obs_dict, name):
            return -1800
        return 1800
    if name in ("battle_cage", "air_balloon"):
        return 2400
    if name in ("boss_orders", "mortys_conviction", "brocks_scouting", "tarragon"):
        return 1400
    if name in ("poke_pad", "dusk_ball", "fighting_gong", "night_stretcher", "hilda"):
        return 300
    return 1000


def promotion_score(card: dict | None, obs_dict: dict) -> int:
    name = card_name(card_id(card))
    if name == "lunatone":
        return 500
    if has_air_balloon(card):
        return 5000
    if is_attack_ready(card, obs_dict):
        if name == "okidogi":
            return 4300
        if name == "clefairy":
            return 4000
        if name == "solrock":
            return 3600
    if is_one_energy_away(card, obs_dict):
        if name == "okidogi":
            return 2600
        if name == "clefairy":
            return 2400
        if name == "solrock":
            return 2800
    if name == "barbaracle":
        return 1850
    if name == "binacle":
        return 1750
    if name == "solrock":
        return 1600
    if name == "okidogi":
        return 900
    if name == "clefairy":
        return 700
    if name:
        return 650
    return 0


def can_use_any_energy(card: dict | None, obs_dict: dict) -> bool:
    name = card_name(card_id(card))
    if name in ("okidogi", "clefairy"):
        return True
    if name == "solrock":
        return has_species_in_play(obs_dict, "lunatone")
    if name in ("binacle", "barbaracle"):
        return count_species_in_play(obs_dict, "okidogi") == 0 and count_species_in_play(obs_dict, "clefairy") == 0
    return False


def one_energy_from_attack_ready(obs_dict: dict) -> bool:
    for card in in_play_cards(obs_dict):
        if not can_use_any_energy(card, obs_dict):
            continue
        name = card_name(card_id(card))
        attached = attached_energy_ids(card)
        count = energy_count(card)
        has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached)
        if name in ("okidogi", "clefairy") and has_special and count == 1:
            return True
        if name == "solrock" and count == 0:
            return True
    return False


def attacker_needs_high_value_energy(obs_dict: dict) -> bool:
    for card in in_play_cards(obs_dict):
        name = card_name(card_id(card))
        if name not in ("okidogi", "clefairy"):
            continue
        attached = attached_energy_ids(card)
        count = energy_count(card)
        has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached)
        if count < 2 and not has_special:
            return True
        if count == 1 and has_special:
            return True
    return one_energy_from_attack_ready(obs_dict)


def hilda_can_complete_with_barbaracle(obs_dict: dict) -> bool:
    if not has_species_in_play(obs_dict, "binacle"):
        return False
    if has_species(obs_dict, "barbaracle"):
        return False
    for card in in_play_cards(obs_dict):
        name = card_name(card_id(card))
        attached = attached_energy_ids(card)
        has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached)
        if name in ("okidogi", "clefairy") and energy_count(card) == 1 and has_special:
            return True
        if name == "solrock" and has_species_in_play(obs_dict, "lunatone") and energy_count(card) == 0:
            return True
    return False


def can_evolve_barbaracle_now(obs_dict: dict) -> bool:
    return has_species_in_play(obs_dict, "binacle") and has_species(obs_dict, "barbaracle")


def hilda_is_high_value(obs_dict: dict) -> bool:
    return hilda_can_complete_with_barbaracle(obs_dict) or attacker_needs_high_value_energy(obs_dict)


def energy_completes_attacker(energy_id: int, target_card: dict | None, obs_dict: dict) -> bool:
    name = card_name(card_id(target_card))
    attached = attached_energy_ids(target_card)
    count = energy_count(target_card)
    has_special_after = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in attached) or energy_id in SPECIAL_ENERGY_IDS
    if name in ("okidogi", "clefairy"):
        return count == 1 and has_special_after
    if name == "solrock":
        return count == 0 and has_species_in_play(obs_dict, "lunatone")
    return False


def current_effect_name(obs_dict: dict) -> str:
    effect = (obs_dict.get("select") or {}).get("effect") or {}
    return card_name(card_id(effect))


def best_basic_attach_score(obs_dict: dict) -> int:
    scores = [attach_score(6, card, obs_dict) for card in in_play_cards(obs_dict)]
    return max(scores) if scores else -5000


def barbaracle_basic_attach_score(card: dict, obs_dict: dict) -> int:
    name = card_name(card_id(card))
    if name == "okidogi":
        return attach_score(6, card, obs_dict)
    if name == "solrock" and energy_count(card) == 0:
        return attach_score(6, card, obs_dict)
    if name in ("binacle", "barbaracle") and count_species_in_play(obs_dict, "okidogi") == 0:
        return attach_score(6, card, obs_dict)
    return -5000


def best_barbaracle_basic_attach_score(obs_dict: dict) -> int:
    scores = [barbaracle_basic_attach_score(card, obs_dict) for card in in_play_cards(obs_dict)]
    return max(scores) if scores else -5000


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
            return 260 if len(in_play_cards(obs_dict)) <= 2 else -2000
        score += 1800
        if has_species(obs_dict, "lunatone") and not has_species_in_play(obs_dict, "solrock"):
            score += 1000
    elif name == "lunatone":
        if in_play >= 1:
            return 240 if len(in_play_cards(obs_dict)) <= 2 else -2000
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
            return 200 if len(in_play_cards(obs_dict)) <= 2 else -2000
        score += 2200 if total == 0 else 260
        if has_species(obs_dict, "lunatone") and not has_species_in_play(obs_dict, "solrock"):
            score += 1400
    elif name == "lunatone":
        if in_play >= 1:
            return 180 if len(in_play_cards(obs_dict)) <= 2 else -2000
        score += 2180 if total == 0 else 240
        if has_species(obs_dict, "solrock") and not has_species_in_play(obs_dict, "lunatone"):
            score += 1400
    elif name == "okidogi":
        score += 1180 if in_play == 0 else (900 if in_play == 1 else -520)
    elif name == "binacle":
        has_set = has_species(obs_dict, "binacle") and has_species(obs_dict, "barbaracle")
        score += 680 if in_play == 0 and not has_set else -180
    elif name == "barbaracle":
        has_set = has_species(obs_dict, "binacle") and has_species(obs_dict, "barbaracle")
        if has_set:
            score -= 420
        else:
            score += 760 if has_species(obs_dict, "binacle") and in_play == 0 else -600
    elif name == "clefairy":
        score += 620 if in_play == 0 else -220
    elif name == "legacy_energy":
        score += 520
    elif name == "prism_energy":
        score += 420
    elif name == "basic_fighting_energy":
        score += 220
        if (
            current_effect_name(obs_dict) == "fighting_gong"
            and not has_energy_in_hand(obs_dict)
            and one_energy_from_attack_ready(obs_dict)
        ):
            score += 3600
    return score


def play_score(name: str, obs_dict: dict) -> int:
    score = 500 + base_card_score(name)
    if name == "boss_orders":
        return 3600 if boss_has_priority_target(obs_dict) else -2200
    if name == "hilda":
        if hilda_can_complete_with_barbaracle(obs_dict):
            return 5200
        if hilda_is_high_value(obs_dict):
            return 3600
        score += 320
    if name == "mortys_conviction":
        opponent_bench = len(opponent_bench_cards(obs_dict))
        if opponent_bench <= 2:
            return -900
        hand_count = rough_hand_count(obs_dict)
        score += opponent_bench * 180
        if hand_count is not None and hand_count <= 3:
            score += 1200
        if not has_energy_in_hand(obs_dict) and not has_energy_search_in_hand(obs_dict):
            score += 1100
        if has_support_in_hand(obs_dict, "lillies_determination"):
            score += 600
    if name in ("dusk_ball", "poke_pad"):
        score += 600
    if name == "fighting_gong":
        score += 520
        if not has_energy_in_hand(obs_dict) and one_energy_from_attack_ready(obs_dict):
            score += 900
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
    required_count = target_energy_need(target_card)
    existing_ids = attached_energy_ids(target_card)
    has_special = any(attached_id in SPECIAL_ENERGY_IDS for attached_id in existing_ids)
    has_fighting = any(attached_id in FIGHTING_ENERGY_IDS for attached_id in existing_ids)

    if required_count <= 0:
        return -2400
    if existing_count >= required_count:
        return -2600
    if existing_count >= 3:
        return -5000

    score = 0
    if energy_completes_attacker(int(energy_id), target_card, obs_dict):
        score += 700 if target == "solrock" else 2200
        if target_card in zone_cards(obs_dict, "active"):
            score += 400

    if energy_id in SPECIAL_ENERGY_IDS:
        score += 900
        if energy_id == 12:
            score += 260
        if target == "okidogi":
            score += 1800 if not has_special else -900
        elif target == "clefairy":
            score += 1600 if not has_special else -900
        elif target == "solrock":
            score += -900 if existing_count == 0 else -1400
            score -= 700
        elif target in ("binacle", "barbaracle"):
            score += -760 if existing_count == 0 and count_species_in_play(obs_dict, "okidogi") == 0 else -1000
        else:
            score -= 360

    if energy_id in FIGHTING_ENERGY_IDS:
        score += 280
        if target == "okidogi":
            score += 1180 if has_special and not has_fighting else (680 if existing_count == 0 else -900)
        elif target == "clefairy":
            score += 1080 if has_special and not has_fighting else (620 if existing_count == 0 else -900)
        elif target == "solrock" and has_species_in_play(obs_dict, "lunatone"):
            score += 900 if existing_count == 0 else -900
            if (
                existing_count == 0
                and is_active_card(obs_dict, target_card)
                and opponent_active_cards(obs_dict)
                and total_hp_left(opponent_active_cards(obs_dict)[0]) <= 140
            ):
                score += 1400
        elif target == "lunatone":
            score -= 600
        elif target in ("binacle", "barbaracle"):
            score += 420 if existing_count == 0 and count_species_in_play(obs_dict, "okidogi") == 0 else -760
        else:
            score -= 260

    return score


def attack_score(option: dict, obs_dict: dict) -> int:
    attack_id = option.get("attackId")
    if attack_id is None:
        return 0

    # Known from visual logs: Solrock's Cosmic Beam is 980.
    if int(attack_id) == 980:
        if has_species_in_play(obs_dict, "lunatone") and opponent_active_cards(obs_dict):
            if total_hp_left(opponent_active_cards(obs_dict)[0]) <= 140:
                return 2600
        return 900 if has_species_in_play(obs_dict, "lunatone") else 220

    return 620


def score_option(option: Any, obs_dict: dict) -> int:
    if not isinstance(option, dict):
        return 0

    opt_type = int(option.get("type") or -1)
    select = obs_dict.get("select") or {}
    context = int(select.get("context") or -1)
    card = option_card(obs_dict, option)
    cid = card_id(card)
    name = card_name(cid)

    if opt_type == TYPE_END:
        return -250

    if opt_type == TYPE_RETREAT:
        if not has_ready_bench_attacker(obs_dict):
            return -1800
        if active_is_ready_attacker(obs_dict):
            return -1600
        return 1200

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
        if name == "lunatone" and needs_lunatone_draw_now(obs_dict):
            return 5200
        if name == "barbaracle":
            return 7600 if can_evolve_barbaracle_now(obs_dict) else -900
        return base_card_score(name) + setup_bench_score(name, obs_dict)

    if current_effect_name(obs_dict) == "boss_orders":
        return boss_target_score(option, obs_dict)

    # Card selection prompts such as setup, search, and to-hand use card options.
    if name:
        if context == 4 and int(option.get("area") or -1) == 5:
            return promotion_score(card, obs_dict)
        if current_effect_name(obs_dict) == "hilda":
            if name == "barbaracle":
                return 4200
            if name == "legacy_energy":
                return 4100
            if name == "prism_energy":
                return 3800
            if name == "basic_fighting_energy":
                return 3400 if best_barbaracle_basic_attach_score(obs_dict) > 0 else 1800
            return -1000
        if current_effect_name(obs_dict) == "mortys_conviction":
            return morty_discard_score(card, obs_dict)
        if current_effect_name(obs_dict) == "lillies_determination":
            return lillie_return_score(card, obs_dict)
        if current_effect_name(obs_dict) == "lunatone":
            return 3000 if name == "basic_fighting_energy" else -1200
        if current_effect_name(obs_dict) == "barbaracle":
            if name == "basic_fighting_energy":
                return 1200 if best_barbaracle_basic_attach_score(obs_dict) > 0 else -900
            if name in POKEMON_NAMES:
                return barbaracle_basic_attach_score(card, obs_dict)
        if rough_turn(obs_dict) == 0 and len(zone_cards(obs_dict, "active")) == 0:
            return setup_active_score(name)
        if rough_turn(obs_dict) == 0 and len(in_play_cards(obs_dict)) > 0:
            return setup_bench_score(name, obs_dict)
        return base_card_score(name) + search_card_score(name, obs_dict)

    return 0
