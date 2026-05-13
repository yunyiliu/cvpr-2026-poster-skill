#!/usr/bin/env python3
"""
Optimize poster column widths and figure card heights from local image aspect ratios.

Example:
    python3 scripts/optimize_poster_layout.py --project-dir ./poster-workspace
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from init_poster_project import write_editable_poster
from poster_image_utils import aspect_ratio, classify_aspect


FIGURE_CARD_IDS = ("overview", "results", "qualitative")
_PROJECT_DIR: Path | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize poster layout from figure aspect ratios.")
    parser.add_argument("--project-dir", required=True, help="Poster workspace directory.")
    return parser.parse_args()


def extract_img_src(html: str) -> str | None:
    match = re.search(r"<img\s+[^>]*src=['\"]([^'\"]+)['\"]", html)
    return match.group(1) if match else None


def optimize_columns(config: dict) -> None:
    columns = config.get("columns", [])
    if len(columns) == 4:
        _optimize_four_columns(config)
    elif len(columns) == 3:
        _optimize_three_columns(config)


def _optimize_four_columns(config: dict) -> None:
    target = config["widthMm"] - 2 * config["paddingMm"] - config["gapMm"] * 3
    cards = config["cards"]
    overview_ratio = local_ratio_from_cards(cards, "overview")
    results_ratio = local_ratio_from_cards(cards, "results")

    side = max(370, min(480, target * 0.22))
    center_total = target - 2 * side

    left_weight = clamp((overview_ratio or 1.6), 1.0, 2.6)
    right_weight = clamp((results_ratio or 1.5), 1.0, 2.6)
    total_weight = left_weight + right_weight
    col2 = center_total * (left_weight / total_weight)
    col3 = center_total - col2

    config["columns"][0]["widthMm"] = round(side, 1)
    config["columns"][1]["widthMm"] = round(col2, 1)
    config["columns"][2]["widthMm"] = round(col3, 1)
    config["columns"][3]["widthMm"] = round(side, 1)


def _optimize_three_columns(config: dict) -> None:
    target = config["widthMm"] - 2 * config["paddingMm"] - config["gapMm"] * 2
    cards = config["cards"]
    overview_ratio = local_ratio_from_cards(cards, "overview")
    results_ratio = local_ratio_from_cards(cards, "results")

    side = max(185, min(250, target * 0.28))
    center = target - 2 * side

    if (overview_ratio or 1.0) > (results_ratio or 1.0) + 0.3:
        center += 20
        side -= 10
    elif (results_ratio or 1.0) > (overview_ratio or 1.0) + 0.3:
        center += 20
        side -= 10

    config["columns"][0]["widthMm"] = round(side, 1)
    config["columns"][1]["widthMm"] = round(center, 1)
    config["columns"][2]["widthMm"] = round(side, 1)


def optimize_card_heights(config: dict) -> None:
    column_widths = {column["id"]: column["widthMm"] for column in config["columns"]}
    card_to_column = {}
    for column in config["columns"]:
        for card_id in column["cards"]:
            card_to_column[card_id] = column["id"]

    for card_id in FIGURE_CARD_IDS:
        card = config["cards"].get(card_id)
        if not card:
            continue
        ratio = local_ratio_from_cards(config["cards"], card_id)
        column_id = card_to_column.get(card_id)
        width_mm = column_widths.get(column_id)
        if not ratio or not width_mm:
            continue

        usable_width = max(120, width_mm - 16)
        figure_height = usable_width / ratio
        if classify_aspect(ratio) == "tall":
            figure_height += 35
        elif classify_aspect(ratio) == "square":
            figure_height += 18
        else:
            figure_height += 10
        caption_and_padding = 24
        desired = figure_height + caption_and_padding
        max_height = 260 if config["heightMm"] > 800 else 145
        min_height = 110 if config["heightMm"] > 800 else 75
        card["heightMm"] = round(clamp(desired, min_height, max_height), 1)


def maybe_move_tall_qualitative(config: dict) -> None:
    qual_ratio = local_ratio_from_cards(config["cards"], "qualitative")
    if not qual_ratio or qual_ratio >= 0.9 or len(config["columns"]) != 4:
        return

    columns = config["columns"]
    from_col = next((column for column in columns if "qualitative" in column["cards"]), None)
    target_col = columns[3]
    if not from_col or from_col["id"] == target_col["id"]:
        return

    from_col["cards"] = [card for card in from_col["cards"] if card != "qualitative"]
    if "qualitative" not in target_col["cards"]:
        target_col["cards"].insert(0, "qualitative")


def local_ratio_from_cards(cards: dict, card_id: str) -> float | None:
    card = cards.get(card_id)
    if not card:
        return None
    src = extract_img_src(card.get("html", ""))
    return _LOCAL_RATIO_RESOLVER(src)


def _LOCAL_RATIO_RESOLVER(rel_src: str | None) -> float | None:
    if _PROJECT_DIR is None or not rel_src:
        return None
    image_path = _PROJECT_DIR / "poster" / rel_src
    if not image_path.exists():
        return None
    return aspect_ratio(image_path)


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def main() -> None:
    args = parse_args()
    optimize_project(Path(args.project_dir).expanduser().resolve())


def optimize_project(project_dir: Path) -> None:
    global _PROJECT_DIR
    project_dir = Path(project_dir).expanduser().resolve()
    _PROJECT_DIR = project_dir
    skill_dir = Path(__file__).resolve().parents[1]
    config_path = project_dir / "poster" / "poster-config.json"

    if not config_path.exists():
        raise SystemExit(f"Missing poster config: {config_path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    optimize_columns(config)
    maybe_move_tall_qualitative(config)
    optimize_card_heights(config)
    write_editable_poster(project_dir, skill_dir, config)
    print(f"Optimized poster layout using figure aspect ratios: {config_path}")


if __name__ == "__main__":
    main()
