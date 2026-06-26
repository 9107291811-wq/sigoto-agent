CARD_NAMES = {
    6: "basic_fighting_energy",
    12: "legacy_energy",
    16: "prism_energy",
    116: "okidogi",
    272: "clefairy",
    675: "lunatone",
    676: "solrock",
    1051: "binacle",
    1052: "barbaracle",
    1097: "night_stretcher",
    1102: "dusk_ball",
    1142: "fighting_gong",
    1152: "poke_pad",
    1174: "air_balloon",
    1182: "boss_orders",
    1187: "mortys_conviction",
    1208: "iriss_fighting_spirit",
    1210: "brocks_scouting",
    1225: "hilda",
    1227: "lillies_determination",
    1236: "urbain",
    1238: "tarragon",
    1264: "battle_cage",
}


SPECIES_IDS = {
    "okidogi": {116},
    "solrock": {676},
    "lunatone": {675},
    "binacle": {1051},
    "barbaracle": {1052},
    "clefairy": {272},
}


SPECIAL_ENERGY_IDS = {12, 16}
FIGHTING_ENERGY_IDS = {6}
ENERGY_IDS = SPECIAL_ENERGY_IDS | FIGHTING_ENERGY_IDS


def card_name(card_id: int | None) -> str:
    if card_id is None:
        return ""
    return CARD_NAMES.get(int(card_id), f"id_{card_id}")
