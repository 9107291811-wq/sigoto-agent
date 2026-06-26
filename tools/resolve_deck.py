import csv
import argparse
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECKLIST_PATH = ROOT / "data" / "decklist_v2.json"
OUTPUT_PATH = ROOT / "deck.csv"


NAME_ALIASES = {
    "basic {f} energy": ["basic {f} energy", "fighting energy", "basic fighting energy"],
    "poke pad": ["poke pad", "poké pad"],
}


def norm(value):
    text = "" if value is None else str(value)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def norm_no(value):
    text = norm(value)
    match = re.search(r"\d+", text)
    return match.group(0) if match else text


def find_csv(input_root):
    root = Path(input_root)
    for name in ("EN_Card_Data.csv", "EN Card Data.csv"):
        matches = list(root.rglob(name))
        if matches:
            return matches[0]
    matches = list(root.rglob("*Card*Data*.csv"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Could not find EN card data CSV under {root}")


def get_field(row, *candidates):
    normalized = {norm(k): v for k, v in row.items()}
    for candidate in candidates:
        key = norm(candidate)
        if key in normalized:
            return normalized[key]
    raise KeyError(f"Missing any column of {candidates}. Columns: {list(row.keys())}")


def load_cards(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    cards = []
    for row in rows:
        cards.append(
            {
                "id": int(get_field(row, "Card ID", "card_id", "id")),
                "name": get_field(row, "Card Name", "name"),
                "expansion": get_field(row, "Expansion", "expansion"),
                "collection_no": get_field(row, "Collection No.", "Collection No", "collection_no"),
            }
        )
    return cards


def candidate_names(name):
    normalized = norm(name)
    names = NAME_ALIASES.get(normalized, [normalized])
    return {norm(item) for item in names}


def exact_match(cards, item):
    names = candidate_names(item["name"])
    expansion = norm(item["expansion"])
    collection_no = norm_no(item["collection_no"])
    return [
        card
        for card in cards
        if norm(card["name"]) in names
        and norm(card["expansion"]) == expansion
        and norm_no(card["collection_no"]) == collection_no
    ]


def name_match(cards, item):
    names = candidate_names(item["name"])
    return [card for card in cards if norm(card["name"]) in names]


def resolve_item(cards, item):
    exact = exact_match(cards, item)
    if exact:
        return exact[0], "exact"

    by_name = name_match(cards, item)
    if by_name:
        return by_name[0], "reprint/name"

    raise ValueError(
        "No legal card found for "
        f"{item['count']} {item['name']} {item['expansion']} {item['collection_no']}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Resolve a readable decklist into CABT card IDs.")
    parser.add_argument("input_root", nargs="?", default="/kaggle/input", help="Folder containing EN card data CSV.")
    parser.add_argument("--decklist", type=Path, default=DECKLIST_PATH, help="Readable decklist JSON.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output deck.csv path.")
    return parser.parse_args()


def main():
    args = parse_args()
    input_root = Path(args.input_root)
    csv_path = find_csv(input_root)
    cards = load_cards(csv_path)
    decklist = json.loads(args.decklist.read_text(encoding="utf-8"))

    deck_ids = []
    print(f"card csv: {csv_path}")
    print("resolved:")
    for item in decklist:
        card, mode = resolve_item(cards, item)
        deck_ids.extend([card["id"]] * int(item["count"]))
        print(
            f"{item['count']} {item['name']} {item['expansion']} {item['collection_no']}"
            f" -> {card['id']} {card['name']} {card['expansion']} {card['collection_no']} ({mode})"
        )

    if len(deck_ids) != 60:
        raise ValueError(f"Deck has {len(deck_ids)} cards, expected 60")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(str(card_id) for card_id in deck_ids) + "\n", encoding="utf-8")
    print(f"wrote: {args.output}")


if __name__ == "__main__":
    main()
