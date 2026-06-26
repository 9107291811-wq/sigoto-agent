from typing import Any

from .scoring_text import as_text
from .state import has_species, missing_setup_bonus, option_text, rough_hand_count, rough_turn


BASE_CARD_PRIORITY = [
    ("okidogi", 1000),
    ("solrock", 930),
    ("lunatone", 910),
    ("binacle", 860),
    ("barbaracle", 850),
    ("lillie's clefairy", 830),
    ("clefairy", 820),
    ("prism energy", 800),
    ("legacy energy", 800),
    ("fighting energy", 760),
    ("basic {f} energy", 760),
    ("dusk ball", 735),
    ("poke pad", 730),
    ("poké pad", 730),
    ("fighting gong", 720),
    ("night stretcher", 700),
    ("brock's scouting", 690),
    ("lillie's determination", 680),
    ("urbain", 675),
    ("tarragon", 665),
    ("boss's orders", 650),
    ("air balloon", 620),
    ("battle cage", 610),
]


BASE_ACTION_PRIORITY = [
    ("ability", 820),
    ("draw", 760),
    ("demolish", 720),
    ("full moon", 700),
    ("cosmic beam", 660),
    ("attack", 620),
    ("evolve", 560),
    ("attach", 540),
    ("play", 500),
    ("retreat", 220),
    ("pass", -250),
    ("end", -300),
]


NON_SUPPORTER_KEYWORDS = (
    "dusk ball",
    "poke pad",
    "poké pad",
    "fighting gong",
    "night stretcher",
    "air balloon",
    "battle cage",
)


SUPPORTER_KEYWORDS = (
    "brock's scouting",
    "lillie's determination",
    "urbain",
    "tarragon",
    "boss's orders",
)


SPECIAL_ENERGY_KEYWORDS = ("prism energy", "legacy energy")
FIGHTING_ENERGY_KEYWORDS = ("fighting energy", "basic {f} energy")


def has_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def base_keyword_score(text: str) -> int:
    score = 0
    for keyword, value in BASE_CARD_PRIORITY:
        if keyword in text:
            score += value
    for keyword, value in BASE_ACTION_PRIORITY:
        if keyword in text:
            score += value
    return score


def setup_score(text: str, obs_dict: dict, context: str) -> int:
    score = 0
    early = rough_turn(obs_dict) <= 2

    if "setupactivepokemon" in context:
        if "okidogi" in text:
            score += 700
        if "solrock" in text:
            score += 420
        if "binacle" in text:
            score += 320
        if "lunatone" in text:
            score += 280
        if "lillie's clefairy" in text:
            score += 240

    if "setupbenchpokemon" in context or "bench" in context or "pokemon" in context:
        if early:
            if "solrock" in text:
                score += missing_setup_bonus(obs_dict, "solrock", 900, 120)
            if "lunatone" in text:
                score += missing_setup_bonus(obs_dict, "lunatone", 880, 100)

        if "okidogi" in text:
            score += 520 if has_species(obs_dict, "okidogi") else 720
        if "binacle" in text:
            score += 620 if not has_species(obs_dict, "binacle") else 220
        if "barbaracle" in text:
            score += 650 if has_species(obs_dict, "binacle") else -180
        if "lillie's clefairy" in text:
            score += 420 if has_species(obs_dict, "okidogi") else 300

    return score


def search_score(text: str, obs_dict: dict, context: str) -> int:
    score = 0
    is_search = any(word in context for word in ("deck", "search", "select", "card"))
    if not is_search:
        return score

    if "solrock" in text:
        score += missing_setup_bonus(obs_dict, "solrock", 850, 120)
    if "lunatone" in text:
        score += missing_setup_bonus(obs_dict, "lunatone", 830, 100)
    if "okidogi" in text:
        score += 680 if not has_species(obs_dict, "okidogi") else 360
    if "binacle" in text:
        score += 620 if not has_species(obs_dict, "binacle") else 180
    if "barbaracle" in text:
        score += 680 if has_species(obs_dict, "binacle") else -220
    if "lillie's clefairy" in text:
        score += 360

    if has_keyword(text, SPECIAL_ENERGY_KEYWORDS):
        score += 520
    if has_keyword(text, FIGHTING_ENERGY_KEYWORDS):
        score += 340

    return score


def energy_score(text: str, obs_dict: dict) -> int:
    score = 0
    is_attach = "attach" in text or "energy" in text
    if not is_attach:
        return score

    if has_keyword(text, SPECIAL_ENERGY_KEYWORDS):
        if "okidogi" in text:
            score += 900
        elif "lillie's clefairy" in text or "clefairy" in text:
            score += 860
        else:
            score += 560

    if has_keyword(text, FIGHTING_ENERGY_KEYWORDS):
        if "okidogi" in text:
            score += 620
        elif "lillie's clefairy" in text or "clefairy" in text:
            score += 600
        elif "solrock" in text and has_species(obs_dict, "lunatone"):
            score += 450
        elif "lunatone" in text:
            score -= 80
        else:
            score += 120

    # Avoid wasting extra basic energy when the option text already exposes a
    # loaded attacker. This is deliberately soft because exact energy state is
    # not always represented in the option text.
    if has_keyword(text, FIGHTING_ENERGY_KEYWORDS) and "energies" in text and "okidogi" in text:
        score -= 160

    return score


def trainer_score(text: str, obs_dict: dict) -> int:
    score = 0
    hand_count = rough_hand_count(obs_dict)

    if has_keyword(text, NON_SUPPORTER_KEYWORDS):
        score += 240

    if "battle cage" in text:
        score += 220

    if "air balloon" in text:
        score += 90

    if "brock's scouting" in text:
        score += 420

    if "lillie's determination" in text:
        score += 520 if hand_count is not None and hand_count <= 3 else 260

    if "urbain" in text:
        score += 540

    if "tarragon" in text:
        score += 360

    if "boss's orders" in text:
        score += 260
        if "ex" in text or "retreat" in text:
            score += 380

    return score


def attack_score(text: str, obs_dict: dict) -> int:
    score = 0
    if "demolish" in text or ("okidogi" in text and "attack" in text):
        score += 1000
    if "full moon" in text or ("lillie's clefairy" in text and "attack" in text):
        score += 900
    if "cosmic beam" in text:
        score += 760 if has_species(obs_dict, "lunatone") else 180
    if "attack" in text and not any(name in text for name in ("okidogi", "clefairy", "cosmic beam")):
        score += 120
    return score


def score_option(option: Any, obs_dict: dict) -> int:
    text = option_text(option)
    select = obs_dict.get("select") or {}
    context = as_text(select.get("context", "")) + " " + as_text(select.get("type", ""))

    return (
        base_keyword_score(text)
        + setup_score(text, obs_dict, context)
        + search_score(text, obs_dict, context)
        + energy_score(text, obs_dict)
        + trainer_score(text, obs_dict)
        + attack_score(text, obs_dict)
    )
