import json
from typing import Any


CARD_PRIORITY = [
    ("okidogi", 1000),
    ("solrock", 930),
    ("lunatone", 900),
    ("binacle", 860),
    ("barbaracle", 850),
    ("fighting energy", 790),
    ("basic {f} energy", 790),
    ("prism energy", 760),
    ("fighting gong", 740),
    ("poke pad", 710),
    ("poké pad", 710),
    ("lillie's determination", 700),
    ("boss's orders", 680),
    ("ciphermaniac", 660),
    ("night stretcher", 650),
    ("energy switch", 640),
    ("energy retrieval", 630),
    ("dusk ball", 625),
    ("air balloon", 620),
    ("battle cage", 610),
    ("urbain", 600),
    ("cornerstone mask ogerpon", 590),
    ("lillie's clefairy", 570),
    ("munkidori", 550),
    ("genesect", 540),
    ("bloodmoon ursaluna", 530),
    ("moltres", 520),
]


ACTION_PRIORITY = [
    ("demolish", 650),
    ("good punch", 620),
    ("cosmic beam", 610),
    ("attack", 500),
    ("play", 450),
    ("evolve", 440),
    ("attach", 430),
    ("retreat", 120),
    ("pass", -100),
    ("end", -120),
]


def as_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False).lower()
    except TypeError:
        return str(value).lower()


def score_option(option: Any, obs_dict: dict) -> int:
    text = as_text(option)
    select = obs_dict.get("select") or {}
    context = as_text(select.get("context", "")) + " " + as_text(select.get("type", ""))

    score = 0
    for keyword, value in CARD_PRIORITY:
        if keyword in text:
            score += value

    for keyword, value in ACTION_PRIORITY:
        if keyword in text:
            score += value

    if "setupactivepokemon" in context:
        if "okidogi" in text:
            score += 500
        if "solrock" in text:
            score += 250

    if "setupbenchpokemon" in context:
        if "solrock" in text or "lunatone" in text:
            score += 450
        if "okidogi" in text:
            score += 300

    if "deck" in context or "search" in context:
        if "solrock" in text or "lunatone" in text:
            score += 300
        if "okidogi" in text:
            score += 250
        if "fighting energy" in text or "basic {f} energy" in text:
            score += 180

    if "hand" in context:
        if "fighting gong" in text or "poke pad" in text or "poké pad" in text:
            score += 180

    return score
