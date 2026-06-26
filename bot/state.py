from .scoring_text import as_text


POKEMON_KEYWORDS = {
    "okidogi": ("okidogi",),
    "solrock": ("solrock",),
    "lunatone": ("lunatone",),
    "binacle": ("binacle",),
    "barbaracle": ("barbaracle",),
    "clefairy": ("lillie's clefairy", "clefairy"),
}


def visible_text(obs_dict: dict) -> str:
    current = obs_dict.get("current") or {}
    return as_text(current)


def option_text(option) -> str:
    return as_text(option)


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def count_visible_species(obs_dict: dict, species: str) -> int:
    text = visible_text(obs_dict)
    return sum(text.count(keyword) for keyword in POKEMON_KEYWORDS[species])


def has_species(obs_dict: dict, species: str) -> bool:
    return count_visible_species(obs_dict, species) > 0


def rough_turn(obs_dict: dict) -> int:
    text = visible_text(obs_dict)
    for marker in ('"turn":', '"turncount":', '"turn_count":'):
        if marker in text:
            tail = text.split(marker, 1)[1].lstrip()
            digits = []
            for char in tail:
                if char.isdigit():
                    digits.append(char)
                elif digits:
                    break
            if digits:
                return int("".join(digits))
    return 0


def rough_hand_count(obs_dict: dict) -> int | None:
    text = visible_text(obs_dict)
    for marker in ('"handcount":', '"hand_count":'):
        if marker in text:
            tail = text.split(marker, 1)[1].lstrip()
            digits = []
            for char in tail:
                if char.isdigit():
                    digits.append(char)
                elif digits:
                    break
            if digits:
                return int("".join(digits))
    return None


def missing_setup_bonus(obs_dict: dict, species: str, high: int, low: int = 0) -> int:
    return high if not has_species(obs_dict, species) else low
