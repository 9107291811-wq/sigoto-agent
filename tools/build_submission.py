from __future__ import annotations

import argparse
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOT_FILES = (
    "__init__.py",
    "cards.py",
    "deck.py",
    "policy.py",
    "scoring.py",
    "scoring_text.py",
    "state.py",
)


def add_file(archive: tarfile.TarFile, source: Path, arcname: str) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing required file: {source}")
    archive.add(source, arcname=arcname)


def build_submission(variant: str) -> Path:
    variant_dir = ROOT / "variants" / variant
    if not variant_dir.is_dir():
        raise FileNotFoundError(f"Unknown variant: {variant_dir}")

    deck_path = variant_dir / "deck.csv"
    deck_count = len([line for line in deck_path.read_text().splitlines() if line.strip()])
    if deck_count != 60:
        raise ValueError(f"{deck_path} must contain 60 cards, got {deck_count}")

    out_dir = ROOT / "dist" / variant
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "submission.tar.gz"

    with tarfile.open(out_path, "w:gz") as archive:
        add_file(archive, ROOT / "main.py", "main.py")
        add_file(archive, deck_path, "deck.csv")

        config_path = variant_dir / "variant_config.json"
        if config_path.exists():
            add_file(archive, config_path, "variant_config.json")

        for file_name in BOT_FILES:
            add_file(archive, ROOT / "bot" / file_name, f"bot/{file_name}")

    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Kaggle submission tarball for a deck variant.")
    parser.add_argument("variant", choices=("deck_a", "deck_b"), help="Variant folder under variants/.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_path = build_submission(args.variant)
    print(f"created: {out_path}")
    with tarfile.open(out_path, "r:gz") as archive:
        print("contents:")
        for name in archive.getnames():
            print(f"- {name}")


if __name__ == "__main__":
    main()
