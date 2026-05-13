#!/usr/bin/env python3
"""
Scaffold a CVPR 2026 poster workspace.

Example:
    python3 scripts/init_poster_project.py \
        --project-dir ./poster-workspace \
        --track main \
        --paper-id 12345 \
        --title "My Paper"
"""

from __future__ import annotations

import argparse
from pathlib import Path


TRACK_SPECS = {
    "main": {
        "size": "84in x 42in",
        "metric_size": "2134mm x 1067mm",
        "columns": "4",
        "job_name_format": "FULL NAME + PAPER ID",
    },
    "findings": {
        "size": "84in x 42in",
        "metric_size": "2134mm x 1067mm",
        "columns": "4",
        "job_name_format": "FULL NAME + PAPER ID",
    },
    "workshop": {
        "size": "42in x 21in",
        "metric_size": "1067mm x 533mm",
        "columns": "3",
        "job_name_format": "FULL NAME + WORKSHOP ACRONYM + PAPER ID",
    },
}


def build_poster_brief(args: argparse.Namespace, spec: dict[str, str]) -> str:
    qr_target = args.qr_url or "[add QR target]"
    title = args.title or "[add final title]"
    paper_id = args.paper_id or "[add paper id]"
    presenter = args.presenter or "[add presenter name]"
    template_source = args.template_source or "[optional template PDF/PPTX/Slides export]"

    return f"""# Poster Brief

## Paper

- Title: {title}
- Paper ID: {paper_id}
- Track: {args.track}
- Authors: [add final authors]
- Affiliations: [add affiliations]
- Presenter: {presenter}

## Format

- Size: {spec["size"]}
- Metric size: {spec["metric_size"]}
- Orientation: landscape
- Columns: {args.columns or spec["columns"]}
- Output: PDF
- Bleed: none

## Links

- QR target: {qr_target}
- Paper link: [add paper link]
- Code link: [add code link]
- Demo or video link: [optional]

## Story

- One-sentence takeaway:
- Problem:
- Why it matters:
- Core idea:
- Main result:
- Conclusion:

## Text blocks

- Short abstract, 2 to 3 sentences:
- Method bullets:
- Results bullets:
- Conclusion bullets:
- Key equations, optional:

## Must-have figures

- Figure 1:
- Figure 2:
- Figure 3:
- Figure 4:

## Tables and metrics

- Main table source:
- Metrics to emphasize:
- Baselines to include:

## Style

- Template source: {template_source}
- Match official CVPR-style spacing and header hierarchy
- Use little text and a few large expressive figures
- Do not copy-paste the paper
"""


def build_poster_outline(args: argparse.Namespace, spec: dict[str, str]) -> str:
    columns = args.columns or spec["columns"]
    return f"""# Poster Outline

## Header

- Title
- Authors and affiliations
- QR code

## Column 1

- Problem or motivation
- Why current methods fall short
- Main contributions

## Column 2

- Method overview
- Main pipeline figure

## Column 3

- Key mechanism or ablation
- Error analysis or intuition figure

## Column 4

- Quantitative results
- Qualitative examples
- Conclusion

## Notes

- Planned columns: {columns}
- Track: {args.track}
- Keep text readable from a distance
"""


def build_print_checklist(spec: dict[str, str]) -> str:
    return f"""# Print Checklist

- Final size matches {spec["size"]}.
- Orientation is landscape.
- Export is PDF.
- No bleed is included.
- Figures remain readable at full poster size.
- QR code opens the intended final destination.
- Job name follows: {spec["job_name_format"]}.
- Final uploaded file is the final file.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a CVPR 2026 poster workspace.")
    parser.add_argument("--project-dir", required=True, help="Directory to create for the poster workspace.")
    parser.add_argument("--track", choices=sorted(TRACK_SPECS.keys()), default="main")
    parser.add_argument("--paper-id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--presenter", default="")
    parser.add_argument("--qr-url", default="")
    parser.add_argument("--template-source", default="")
    parser.add_argument("--columns", choices=["3", "4"], default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = TRACK_SPECS[args.track]
    project_dir = Path(args.project_dir).expanduser().resolve()

    for relative in [
        "assets/figures",
        "assets/logos",
        "references",
        "output",
    ]:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

    files = {
        "poster_brief.md": build_poster_brief(args, spec),
        "poster_outline.md": build_poster_outline(args, spec),
        "print_checklist.md": build_print_checklist(spec),
        "references/notes.md": "# Notes\n\n- Add links to the official template here.\n- Add figure captions or pending design notes here.\n",
    }

    for relative_path, content in files.items():
        path = project_dir / relative_path
        path.write_text(content, encoding="utf-8")

    print(f"Created poster workspace at: {project_dir}")
    print("Next steps:")
    print("1. Add figures to assets/figures/")
    print("2. Add logos to assets/logos/")
    print("3. Fill poster_brief.md and poster_outline.md")
    print("4. Export the final poster as PDF with no bleed")


if __name__ == "__main__":
    main()
