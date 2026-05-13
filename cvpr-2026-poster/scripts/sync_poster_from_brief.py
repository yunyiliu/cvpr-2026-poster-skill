#!/usr/bin/env python3
"""
Sync poster_brief.md into poster/poster-config.json and poster/index.html.

Example:
    python3 scripts/sync_poster_from_brief.py --project-dir ./poster-workspace
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from init_poster_project import TRACK_SPECS, write_editable_poster

DISPLAY_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync poster_brief.md into the editable poster.")
    parser.add_argument("--project-dir", required=True, help="Poster workspace directory.")
    return parser.parse_args()


def parse_brief(path: Path) -> dict[str, dict[str, object]]:
    sections: dict[str, dict[str, object]] = {}
    current_section: str | None = None
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current_section = heading.group(1).strip()
            sections[current_section] = {}
            current_key = None
            continue

        if current_section is None:
            continue

        bullet = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if bullet:
            current_key = bullet.group(1).strip()
            value = bullet.group(2).strip()
            sections[current_section][current_key] = value if value else []
            continue

        sub_bullet = re.match(r"^\s{2,}-\s+(.*)$", line)
        if sub_bullet and current_key:
            existing = sections[current_section].setdefault(current_key, [])
            if not isinstance(existing, list):
                existing = [str(existing)] if existing else []
                sections[current_section][current_key] = existing
            item = sub_bullet.group(1).strip()
            if item:
                existing.append(item)
            continue

        continuation = re.match(r"^\s{2,}(.+)$", line)
        if continuation and current_key:
            existing = sections[current_section].get(current_key, "")
            extra = continuation.group(1).strip()
            if isinstance(existing, list):
                if extra:
                    existing.append(extra)
            else:
                parts = [existing, extra] if existing else [extra]
                sections[current_section][current_key] = " ".join(part for part in parts if part)

    return sections


def get_value(sections: dict[str, dict[str, object]], section: str, key: str) -> str:
    value = sections.get(section, {}).get(key, "")
    if isinstance(value, list):
        return " ".join(item for item in value if item)
    return str(value).strip()


def get_list(sections: dict[str, dict[str, object]], section: str, key: str) -> list[str]:
    value = sections.get(section, {}).get(key, [])
    if isinstance(value, list):
        return [item.strip() for item in value if item and item.strip()]
    return [str(value).strip()] if str(value).strip() else []


def bullet_html(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{escape_html(item)}</li>" for item in items)
    return f"<ul>{lis}</ul>"


def para_html(text: str, bold: bool = False) -> str:
    if not text:
        return ""
    body = escape_html(text)
    if bold:
        body = f"<b>{body}</b>"
    return f"<p>{body}</p>"


def figure_card_html(rel_path: str | None, caption: str, fallback_text: str) -> str:
    if rel_path:
        return (
            "<div class='fig'>"
            f"<div class='fig-box'><img src='{escape_attr(rel_path)}' alt='figure'></div>"
            f"<div class='fig-cap'>{escape_html(caption)}</div>"
            "</div>"
        )
    return (
        "<div class='fig'>"
        f"<div class='fig-box'>{escape_html(fallback_text)}</div>"
        f"<div class='fig-cap'>{escape_html(caption)}</div>"
        "</div>"
    )


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_attr(text: str) -> str:
    return escape_html(text).replace("'", "&#39;")


def badge_for_track(track: str) -> str:
    if track == "workshop":
        return "CVPR 2026 Workshop"
    return "CVPR 2026 Main / Findings"


def copy_user_logos(project_dir: Path) -> list[str]:
    src_root = project_dir / "assets" / "logos"
    dst_root = project_dir / "poster" / "logos" / "user"
    dst_root.mkdir(parents=True, exist_ok=True)
    rel_paths: list[str] = []

    if not src_root.exists():
        return rel_paths

    for path in sorted(src_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DISPLAY_EXTS:
            continue
        if "official" in path.parts:
            continue
        target = dst_root / path.name
        shutil.copy2(path, target)
        rel_paths.append(str(target.relative_to(project_dir / "poster")))

    return rel_paths


def copy_figure_assets(project_dir: Path) -> list[str]:
    src_root = project_dir / "assets" / "figures"
    dst_root = project_dir / "poster" / "figures"
    dst_root.mkdir(parents=True, exist_ok=True)
    rel_paths: list[str] = []

    if not src_root.exists():
        return rel_paths

    for path in sorted(src_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DISPLAY_EXTS:
            continue
        target = dst_root / path.name
        shutil.copy2(path, target)
        rel_paths.append(str(target.relative_to(project_dir / "poster")))

    return rel_paths


def pick_figure(figures: list[str], keywords: tuple[str, ...], used: set[str]) -> str | None:
    for rel_path in figures:
        name = Path(rel_path).name.lower()
        if rel_path in used:
            continue
        if any(keyword in name for keyword in keywords):
            used.add(rel_path)
            return rel_path
    for rel_path in figures:
        if rel_path not in used:
            used.add(rel_path)
            return rel_path
    return None


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    skill_dir = Path(__file__).resolve().parents[1]
    brief_path = project_dir / "poster_brief.md"
    config_path = project_dir / "poster" / "poster-config.json"

    if not brief_path.exists():
        raise SystemExit(f"Missing poster brief: {brief_path}")
    if not config_path.exists():
        raise SystemExit(f"Missing poster config: {config_path}")

    sections = parse_brief(brief_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))

    track = get_value(sections, "Paper", "Track").lower() or "main"
    if track not in TRACK_SPECS:
        track = "main"

    user_logo_paths = copy_user_logos(project_dir)
    figure_paths = copy_figure_assets(project_dir)
    used_figures: set[str] = set()

    config["title"] = get_value(sections, "Paper", "Title") or config.get("title", "")
    config["authors"] = get_value(sections, "Paper", "Authors") or config.get("authors", "")
    config["affiliations"] = get_value(sections, "Paper", "Affiliations") or config.get("affiliations", "")
    config["badge"] = badge_for_track(track)

    official_logos = [logo for logo in config.get("logos", []) if "official/" in logo.get("src", "")]
    user_logos = [{"src": rel_path, "alt": Path(rel_path).stem} for rel_path in user_logo_paths]
    config["logos"] = user_logos + official_logos

    qr_target = get_value(sections, "Links", "QR target")
    if qr_target:
        config["qr"]["label"] = "QR target set in poster_brief.md"
        config["qr"]["src"] = ""

    takeaway = get_value(sections, "Story", "One-sentence takeaway")
    problem = get_value(sections, "Story", "Problem")
    why_it_matters = get_value(sections, "Story", "Why it matters")
    core_idea = get_value(sections, "Story", "Core idea")
    main_result = get_value(sections, "Story", "Main result")
    conclusion = get_value(sections, "Story", "Conclusion")

    short_abstract = get_value(sections, "Text blocks", "Short abstract, 2 to 3 sentences")
    method_bullets = get_list(sections, "Text blocks", "Method bullets")
    results_bullets = get_list(sections, "Text blocks", "Results bullets")
    conclusion_bullets = get_list(sections, "Text blocks", "Conclusion bullets")
    equations = get_value(sections, "Text blocks", "Key equations, optional")

    metrics = get_list(sections, "Tables and metrics", "Metrics to emphasize")
    baselines = get_list(sections, "Tables and metrics", "Baselines to include")
    paper_link = get_value(sections, "Links", "Paper link")
    code_link = get_value(sections, "Links", "Code link")
    demo_link = get_value(sections, "Links", "Demo or video link")

    overview_fig = pick_figure(figure_paths, ("overview", "method", "architecture", "pipeline", "teaser"), used_figures)
    results_fig = pick_figure(figure_paths, ("result", "results", "quant", "table"), used_figures)
    qualitative_fig = pick_figure(figure_paths, ("qual", "example", "demo", "ablation", "error"), used_figures)

    config["cards"]["problem"]["html"] = "".join(
        [
            para_html(takeaway, bold=True),
            para_html(problem),
            para_html(why_it_matters),
            bullet_html([item for item in [core_idea, main_result] if item]),
        ]
    ) or config["cards"]["problem"]["html"]

    contrib_items = get_list(sections, "Text blocks", "Conclusion bullets") or conclusion_bullets
    config["cards"]["contrib"]["html"] = "".join(
        [
            para_html(short_abstract),
            bullet_html(contrib_items[:3] if contrib_items else ["Add the top 3 contributions here"]),
        ]
    )

    overview_caption = "Main method overview figure."
    config["cards"]["overview"]["html"] = "".join(
        [
            figure_card_html(overview_fig, overview_caption, "Add a main overview figure to assets/figures/ and rerun sync."),
            para_html(core_idea),
        ]
    )

    method_parts = [bullet_html(method_bullets), para_html(equations), para_html(get_value(sections, "Story", "Core idea"))]
    config["cards"]["method"]["html"] = "".join(part for part in method_parts if part) or config["cards"]["method"]["html"]

    config["cards"]["results"]["html"] = "".join(
        [
            figure_card_html(results_fig, "Main results figure or table screenshot.", "Add a results figure to assets/figures/ and rerun sync."),
            bullet_html(results_bullets),
            para_html(main_result),
        ]
    )

    config["cards"]["qualitative"]["html"] = "".join(
        [
            figure_card_html(qualitative_fig, "Qualitative examples or failure analysis.", "Add a qualitative figure to assets/figures/ and rerun sync."),
            para_html(conclusion),
        ]
    )

    table_rows = []
    if baselines or metrics:
        header_cells = "".join(f"<th>{escape_html(metric)}</th>" for metric in (metrics or ["Metric 1", "Metric 2"]))
        baseline_label = ", ".join(baselines) if baselines else "Add baselines"
        value_cells = "".join("<td>fill</td>" for _ in (metrics or ["Metric 1", "Metric 2"]))
        table_rows.append(
            "<table><thead><tr><th>Method</th>"
            f"{header_cells}</tr></thead><tbody><tr><td>{escape_html(baseline_label)}</td>{value_cells}</tr>"
            f"<tr><td><b>Ours</b></td>{value_cells}</tr></tbody></table>"
        )
    else:
        table_rows.append(config["cards"]["table"]["html"])
    config["cards"]["table"]["html"] = "".join(table_rows)

    link_lines = [item for item in [f"Paper: {paper_link}" if paper_link else "", f"Code: {code_link}" if code_link else "", f"Demo: {demo_link}" if demo_link else "", f"QR target: {qr_target}" if qr_target else ""] if item]
    config["cards"]["conclusion"]["html"] = "".join(
        [
            bullet_html(conclusion_bullets or ["Add final takeaways here"]),
            para_html(conclusion),
            "".join(para_html(item) for item in link_lines),
        ]
    )

    write_editable_poster(project_dir, skill_dir, config)
    print(f"Updated poster/index.html and poster/poster-config.json from {brief_path}")


if __name__ == "__main__":
    main()
