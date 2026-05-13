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
import shutil
from pathlib import Path


TRACK_SPECS = {
    "main": {
        "size": "84in x 42in",
        "metric_size": "2134mm x 1067mm",
        "width_mm": 2134,
        "height_mm": 1067,
        "columns": "4",
        "job_name_format": "FULL NAME + PAPER ID",
    },
    "findings": {
        "size": "84in x 42in",
        "metric_size": "2134mm x 1067mm",
        "width_mm": 2134,
        "height_mm": 1067,
        "columns": "4",
        "job_name_format": "FULL NAME + PAPER ID",
    },
    "workshop": {
        "size": "42in x 21in",
        "metric_size": "1067mm x 533mm",
        "width_mm": 1067,
        "height_mm": 533,
        "columns": "3",
        "job_name_format": "FULL NAME + WORKSHOP ACRONYM + PAPER ID",
    },
}

MAIN_FINDINGS_TEMPLATE = "CVPR MAIN & FINDINGS Poster Template.pptx"
WORKSHOP_TEMPLATE = "CVPR Workshop ONLY Poster Template.pptx"


def build_poster_brief(args: argparse.Namespace, spec: dict[str, str]) -> str:
    qr_target = args.qr_url or "[add QR target]"
    title = args.title or "[add final title]"
    paper_id = args.paper_id or "[add paper id]"
    presenter = args.presenter or "[add presenter name]"
    template_source = args.template_source or "[workspace override or bundled official template]"

    return f"""# Poster Brief

## Paper

- Title: {title}
- Paper ID: {paper_id}
- Track: {args.track}
- Authors: [add final authors]
- Affiliations: [add affiliations]
- Institution websites, optional:
  - 
- Presenter: {presenter}

Tip: if the paper has multiple schools or labs, list one website per institution in the same order as Affiliations.

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
  - 
  - 
  - 
- Results bullets:
  - 
  - 
  - 
- Conclusion bullets:
  - 
  - 
- Key equations, optional:

## Must-have figures

- Figure 1:
- Figure 2:
- Figure 3:
- Figure 4:

## Tables and metrics

- Main table source:
- Metrics to emphasize:
  - 
  - 
- Baselines to include:
  - 
  - 

## Style

- Template source: {template_source}
- Template priority: workspace override -> bundled official asset -> shared Drive export
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


def build_editable_poster_config(args: argparse.Namespace, spec: dict[str, str], logo_paths: list[str]) -> dict:
    if args.track in {"main", "findings"}:
        badge = "CVPR 2026 Main / Findings"
        columns = [
            {"id": "col1", "widthMm": 470, "cards": ["problem", "contrib"]},
            {"id": "col2", "widthMm": 540, "cards": ["overview", "method"]},
            {"id": "col3", "widthMm": 540, "cards": ["results", "qualitative"]},
            {"id": "col4", "widthMm": 470, "cards": ["table", "conclusion"]},
        ]
    else:
        badge = "CVPR 2026 Workshop"
        columns = [
            {"id": "col1", "widthMm": 300, "cards": ["problem", "contrib"]},
            {"id": "col2", "widthMm": 410, "cards": ["overview", "results"]},
            {"id": "col3", "widthMm": 300, "cards": ["table", "conclusion"]},
        ]

    conference_logos = [{"src": path, "alt": "CVPR 2026"} for path in logo_paths]
    logos: list[dict] = []
    qr_src = ""
    title = args.title or "CVPR 2026 Poster Title"

    cards = {
        "problem": {
            "title": "Problem & Motivation",
            "accent": "#1b5da2",
            "heightMm": 135 if args.track in {"main", "findings"} else 85,
            "html": (
                "<p><b>Replace this section</b> with a crisp motivation statement and the problem setting.</p>"
                "<ul><li>Why the task matters</li><li>Why current methods fall short</li><li>What makes your framing distinct</li></ul>"
            ),
        },
        "contrib": {
            "title": "Contributions",
            "accent": "#5a8f13",
            "html": (
                "<ul><li>Main contribution 1</li><li>Main contribution 2</li><li>Main contribution 3</li></ul>"
                "<p>Keep this card short and scan-friendly.</p>"
            ),
        },
        "overview": {
            "title": "Method Overview",
            "accent": "#1b5da2",
            "heightMm": 215 if args.track in {"main", "findings"} else 110,
            "html": (
                "<div class='fig'><div class='fig-box'>Drop your main method figure into <code>poster/figures/</code> and update the HTML.</div>"
                "<div class='fig-cap'><b>Overview.</b> Use this space for your main pipeline or architecture figure.</div></div>"
            ),
        },
        "method": {
            "title": "Method Details",
            "accent": "#2b7a68",
            "html": (
                "<ul><li>Key mechanism or module</li><li>Training or optimization detail</li><li>Optional equation or ablation hook</li></ul>"
                "<p>Prefer bullets over paragraphs.</p>"
            ),
        },
        "results": {
            "title": "Results",
            "accent": "#7a4bb3",
            "heightMm": 220 if args.track in {"main", "findings"} else 120,
            "html": (
                "<div class='fig'><div class='fig-box'>Place a qualitative or main results panel here.</div>"
                "<div class='fig-cap'><b>Results.</b> This card is intentionally large so it can absorb visual content.</div></div>"
            ),
        },
        "qualitative": {
            "title": "Qualitative Findings",
            "accent": "#d17823",
            "html": (
                "<p>Use this card for qualitative examples, error analysis, or a visual comparison.</p>"
                "<ul><li>Before vs after</li><li>Failure modes</li><li>Clinical or practical significance</li></ul>"
            ),
        },
        "table": {
            "title": "Main Quantitative Table",
            "accent": "#d17823",
            "heightMm": 150 if args.track in {"main", "findings"} else 95,
            "html": (
                "<table><thead><tr><th>Method</th><th>Metric</th><th>Metric</th></tr></thead>"
                "<tbody><tr><td>Baseline</td><td>0.00</td><td>0.00</td></tr><tr><td><b>Ours</b></td><td><b>0.00</b></td><td><b>0.00</b></td></tr></tbody></table>"
            ),
        },
        "conclusion": {
            "title": "Conclusion & Links",
            "accent": "#b14f4f",
            "html": (
                "<ul><li>Takeaway 1</li><li>Takeaway 2</li><li>Takeaway 3</li></ul>"
                "<p><b>Paper:</b> add link<br><b>Code:</b> add link<br><b>QR:</b> add final target</p>"
            ),
        },
    }

    return {
        "widthMm": spec["width_mm"],
        "heightMm": spec["height_mm"],
        "gapMm": 10,
        "paddingMm": 16,
        "fontScale": 1.0,
        "title": title,
        "authors": "Add authors here",
        "affiliations": "Add affiliations here",
        "badge": badge,
        "qr": {"src": qr_src, "label": "Paper / Project"},
        "logos": logos,
        "conferenceLogos": conference_logos,
        "columns": columns,
        "cards": cards,
    }


def write_editable_poster(project_dir: Path, skill_dir: Path, config: dict) -> None:
    template_path = skill_dir / "assets" / "editor" / "editable-poster-template.html"
    template_html = template_path.read_text(encoding="utf-8")
    poster_dir = project_dir / "poster"
    poster_dir.mkdir(parents=True, exist_ok=True)
    html = template_html.replace("__POSTER_CONFIG__", json_dumps(config))
    (poster_dir / "index.html").write_text(html, encoding="utf-8")
    (poster_dir / "poster-config.json").write_text(json_dumps(config, pretty=True), encoding="utf-8")


def json_dumps(data: dict, pretty: bool = False) -> str:
    import json
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def copy_bundled_assets(project_dir: Path, track: str, skill_dir: Path) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    logo_paths: list[str] = []
    templates_dir = skill_dir / "assets" / "official" / "templates"
    bundled_logos_dir = skill_dir / "assets" / "official" / "logos"
    workspace_templates_dir = project_dir / "references" / "templates"
    workspace_logos_dir = project_dir / "assets" / "logos" / "official"
    poster_logos_dir = project_dir / "poster" / "logos" / "official"

    workspace_templates_dir.mkdir(parents=True, exist_ok=True)
    workspace_logos_dir.mkdir(parents=True, exist_ok=True)
    poster_logos_dir.mkdir(parents=True, exist_ok=True)

    if track in {"main", "findings"}:
        template_path = templates_dir / MAIN_FINDINGS_TEMPLATE
    else:
        template_path = templates_dir / WORKSHOP_TEMPLATE

    if template_path.exists():
        target = workspace_templates_dir / template_path.name
        shutil.copy2(template_path, target)
        copied.append(str(target.relative_to(project_dir)))

    if bundled_logos_dir.exists():
        for item in sorted(bundled_logos_dir.iterdir()):
            if item.is_file() and not item.name.startswith("."):
                workspace_target = workspace_logos_dir / item.name
                poster_target = poster_logos_dir / item.name
                shutil.copy2(item, workspace_target)
                shutil.copy2(item, poster_target)
                copied.append(str(workspace_target.relative_to(project_dir)))
                copied.append(str(poster_target.relative_to(project_dir)))
                if item.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
                    logo_paths.append(str(poster_target.relative_to(project_dir / "poster")))

    # Copy PDF export helpers into the workspace root so users can run
    # `bash export_pdf.sh` / `bash bake_and_export.sh` immediately.
    export_dir = skill_dir / "assets" / "export"
    if export_dir.exists():
        for item in sorted(export_dir.iterdir()):
            if item.is_file() and item.suffix == ".sh":
                target = project_dir / item.name
                shutil.copy2(item, target)
                target.chmod(0o755)
                copied.append(str(target.relative_to(project_dir)))

    return copied, logo_paths


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
    skill_dir = Path(__file__).resolve().parents[1]

    for relative in [
        "assets/figures",
        "assets/logos",
        "references",
        "poster",
        "poster/figures",
        "poster/logos",
        "output",
    ]:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

    copied_assets, logo_paths = copy_bundled_assets(project_dir, args.track, skill_dir)
    editable_config = build_editable_poster_config(args, spec, logo_paths)
    write_editable_poster(project_dir, skill_dir, editable_config)

    notes_lines = [
        "# Notes",
        "",
        "- Add links to the official template here.",
        "- Add figure captions or pending design notes here.",
        "- Asset priority: workspace override -> bundled official asset -> shared Drive export.",
        "- Put school or lab logos under assets/logos/ and make sure the final header uses them if needed.",
    ]
    if copied_assets:
        notes_lines.append("- Bundled assets copied into this workspace:")
        for relative in copied_assets:
            notes_lines.append(f"  - {relative}")
    else:
        notes_lines.append("- No bundled asset was copied for this track.")

    files = {
        "poster_brief.md": build_poster_brief(args, spec),
        "poster_outline.md": build_poster_outline(args, spec),
        "print_checklist.md": build_print_checklist(spec),
        "references/notes.md": "\n".join(notes_lines) + "\n",
    }

    for relative_path, content in files.items():
        path = project_dir / relative_path
        path.write_text(content, encoding="utf-8")

    print(f"Created poster workspace at: {project_dir}")
    print("Next steps:")
    print("1. Add figures to assets/figures/")
    print("2. Add school or lab logos to assets/logos/")
    print("   If the paper has multiple institutions, prepare one logo or one website per institution.")
    print("3. If you have Overleaf or LaTeX source, run fill_brief_from_latex.py")
    print("4. Add an override template to references/ if needed")
    print("5. Open poster/index.html to edit the generated poster")
    print("6. Fill poster_brief.md and poster_outline.md")
    print("7. Export the final poster as PDF with no bleed")


if __name__ == "__main__":
    main()
