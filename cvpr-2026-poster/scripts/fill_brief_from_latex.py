#!/usr/bin/env python3
"""
Seed poster_brief.md from an Overleaf or LaTeX source folder.

Example:
    python3 scripts/fill_brief_from_latex.py \
        --project-dir ./poster-workspace \
        --latex-dir ./overleaf \
        --copy-figures
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

DISPLAY_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
FIGURE_EXTS = [".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".pdf", ".eps"]
AFFILIATION_HINTS = (
    "university",
    "institute",
    "institution",
    "school",
    "college",
    "department",
    "faculty",
    "hospital",
    "lab",
    "laboratory",
    "research",
    "centre",
    "center",
    "academy",
    "company",
    "corp",
    "inc",
    "ltd",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill poster_brief.md from a LaTeX project.")
    parser.add_argument("--project-dir", required=True, help="Poster workspace directory.")
    parser.add_argument("--latex-dir", required=True, help="Overleaf or LaTeX source directory.")
    parser.add_argument("--main-tex", help="Explicit main tex file, relative to --latex-dir or absolute.")
    parser.add_argument("--copy-figures", action="store_true", help="Copy detected displayable figures into assets/figures/.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing non-placeholder fields in poster_brief.md.")
    return parser.parse_args()


def strip_comments(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        kept: list[str] = []
        escaped = False
        for char in line:
            if char == "%" and not escaped:
                break
            kept.append(char)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        cleaned_lines.append("".join(kept))
    return "\n".join(cleaned_lines)


def read_text(path: Path) -> str:
    return strip_comments(path.read_text(encoding="utf-8", errors="ignore"))


def resolve_main_tex(latex_dir: Path, explicit: str | None) -> Path:
    if explicit:
        explicit_path = Path(explicit)
        if not explicit_path.is_absolute():
            explicit_path = latex_dir / explicit_path
        if explicit_path.exists():
            return explicit_path.resolve()
        raise SystemExit(f"Main tex file not found: {explicit_path}")

    candidates = sorted(latex_dir.rglob("*.tex"))
    if not candidates:
        raise SystemExit(f"No .tex files found under: {latex_dir}")

    preferred_names = ("main.tex", "paper.tex", "cvpr.tex", "article.tex")
    for name in preferred_names:
        for path in candidates:
            if path.name.lower() == name:
                return path.resolve()

    scored = sorted(candidates, key=score_main_tex, reverse=True)
    return scored[0].resolve()


def score_main_tex(path: Path) -> tuple[int, int, int]:
    text = read_text(path)
    score = 0
    if r"\documentclass" in text:
        score += 100
    if r"\begin{document}" in text:
        score += 60
    if r"\maketitle" in text:
        score += 30
    if r"\begin{abstract}" in text:
        score += 20
    if r"\title" in text:
        score += 10
    return (score, -len(path.parts), -len(str(path)))


def resolve_tex_path(base_dir: Path, target: str) -> Path | None:
    candidate = (base_dir / target).expanduser()
    if candidate.suffix:
        return candidate.resolve() if candidate.exists() else None
    tex_candidate = candidate.with_suffix(".tex")
    if tex_candidate.exists():
        return tex_candidate.resolve()
    if candidate.exists():
        return candidate.resolve()
    return None


def expand_tex(path: Path, seen: set[Path] | None = None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)

    text = read_text(path)

    def replace_include(match: re.Match[str]) -> str:
        include_target = resolve_tex_path(path.parent, match.group(1).strip())
        if not include_target:
            return ""
        return "\n" + expand_tex(include_target, seen) + "\n"

    return re.sub(r"\\(?:input|include)\{([^}]+)\}", replace_include, text)


def extract_simple_macros(text: str) -> dict[str, str]:
    macros: dict[str, str] = {}
    patterns = [
        re.compile(r"\\(?:newcommand|renewcommand|providecommand)\s*\{\\([A-Za-z@]+)\}\s*(?:\[\s*0\s*\])?\s*\{([^{}]*)\}"),
        re.compile(r"\\def\\([A-Za-z@]+)\s*\{([^{}]*)\}"),
    ]
    for pattern in patterns:
        for name, value in pattern.findall(text):
            macros[name] = value.strip()
    return macros


def apply_macros(text: str, macros: dict[str, str]) -> str:
    expanded = text
    for _ in range(4):
        previous = expanded
        for name, value in macros.items():
            expanded = re.sub(rf"\\{re.escape(name)}\b", value, expanded)
        if expanded == previous:
            break
    return expanded


def extract_balanced(text: str, start_brace: int) -> tuple[str, int] | None:
    if start_brace < 0 or start_brace >= len(text) or text[start_brace] != "{":
        return None
    depth = 0
    buffer: list[str] = []
    index = start_brace
    while index < len(text):
        char = text[index]
        if char == "{" and not is_escaped(text, index):
            depth += 1
            if depth > 1:
                buffer.append(char)
        elif char == "}" and not is_escaped(text, index):
            depth -= 1
            if depth == 0:
                return ("".join(buffer), index + 1)
            buffer.append(char)
        else:
            if depth >= 1:
                buffer.append(char)
        index += 1
    return None


def is_escaped(text: str, index: int) -> bool:
    slash_count = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        slash_count += 1
        index -= 1
    return slash_count % 2 == 1


def find_command_argument(text: str, command: str) -> str:
    pattern = re.compile(rf"\\{re.escape(command)}(?:\[[^\]]*\])?\s*\{{", re.S)
    match = pattern.search(text)
    if not match:
        return ""
    brace_index = match.end() - 1
    extracted = extract_balanced(text, brace_index)
    return extracted[0] if extracted else ""


def find_environment(text: str, name: str) -> str:
    pattern = re.compile(rf"\\begin\{{{re.escape(name)}\}}(.*?)\\end\{{{re.escape(name)}\}}", re.S)
    match = pattern.search(text)
    return match.group(1) if match else ""


def plain_tex(text: str, macros: dict[str, str]) -> str:
    cleaned = apply_macros(text, macros)
    cleaned = cleaned.replace("\\\\", "\n")
    cleaned = cleaned.replace("~", " ")
    cleaned = cleaned.replace(r"\&", "&")
    cleaned = cleaned.replace(r"\_", "_")
    cleaned = cleaned.replace(r"\%", "%")
    cleaned = re.sub(r"\\(?:\\|newline|linebreak|par)\b", "\n", cleaned)
    cleaned = re.sub(r"\\and\b", "\n", cleaned)
    cleaned = re.sub(r"\\thanks\s*\{[^{}]*\}", "", cleaned)
    cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)

    while True:
        updated = re.sub(r"\\[A-Za-z@*]+(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", cleaned)
        if updated == cleaned:
            break
        cleaned = updated

    cleaned = re.sub(r"\\[A-Za-z@*]+(?:\[[^\]]*\])?", " ", cleaned)
    cleaned = cleaned.replace("{", "").replace("}", "")
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = re.sub(r"\n\s+", "\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def first_sentence(text: str) -> str:
    normalized = " ".join(text.split())
    match = re.match(r"(.+?[.!?])(?:\s|$)", normalized)
    return match.group(1).strip() if match else normalized


def parse_authors_and_affiliations(author_block: str, macros: dict[str, str]) -> tuple[str, str]:
    if not author_block:
        return ("", "")

    segments = [segment.strip() for segment in re.split(r"\\and\b", author_block) if segment.strip()]
    if not segments:
        segments = [author_block]

    authors: list[str] = []
    affiliations: list[str] = []

    for segment in segments:
        plain = plain_tex(segment, macros)
        lines = [clean_line(line) for line in plain.splitlines() if clean_line(line)]
        if not lines:
            continue

        author_lines: list[str] = []
        affiliation_lines: list[str] = []
        seen_affiliation = False

        for line in lines:
            if "@" in line:
                continue
            if looks_like_affiliation(line):
                affiliation_lines.append(line)
                seen_affiliation = True
                continue
            if seen_affiliation:
                affiliation_lines.append(line)
            else:
                author_lines.append(line)

        if not author_lines and lines:
            author_lines = [lines[0]]
            affiliation_lines = lines[1:]

        author_text = normalize_people_text(" ".join(author_lines))
        if author_text:
            authors.append(author_text)

        for line in affiliation_lines:
            if line and line not in affiliations:
                affiliations.append(line)

    if not affiliations:
        plain = plain_tex(author_block, macros)
        lines = [clean_line(line) for line in plain.splitlines() if clean_line(line) and "@" not in line]
        if len(lines) >= 2:
            authors = [normalize_people_text(lines[0])]
            affiliations = dedupe(lines[1:])

    return ("; ".join(dedupe(authors)), "; ".join(dedupe(affiliations)))


def clean_line(text: str) -> str:
    cleaned = text.strip(" ,;\\")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def normalize_people_text(text: str) -> str:
    text = clean_line(text)
    text = re.sub(r"\b(and)\b", ",", text, flags=re.IGNORECASE)
    parts = [clean_line(part) for part in re.split(r",|;", text) if clean_line(part)]
    return ", ".join(parts)


def looks_like_affiliation(line: str) -> bool:
    lowered = line.lower()
    if any(token in lowered for token in AFFILIATION_HINTS):
        return True
    if re.search(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", lowered):
        return False
    if re.search(r"\b(sydney|melbourne|adelaide|brisbane|perth|beijing|shanghai|tokyo|seoul|boston|denver|london)\b", lowered):
        return True
    return False


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if not item or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def collect_figures(path: Path, macros: dict[str, str], seen: set[Path] | None = None) -> list[dict[str, object]]:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return []
    seen.add(path)

    text = read_text(path)
    figures: list[dict[str, object]] = []

    for match in re.finditer(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", text, flags=re.S):
        env = match.group(1)
        caption_raw = find_command_argument(env, "caption")
        caption = clean_line(plain_tex(caption_raw, macros))
        graphics = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", env)
        for graphic in graphics:
            resolved = resolve_figure_path(path.parent, graphic.strip())
            figures.append(
                {
                    "source": resolved,
                    "reference": graphic.strip(),
                    "caption": caption,
                    "source_tex": path,
                }
            )

    for include in re.finditer(r"\\(?:input|include)\{([^}]+)\}", text):
        include_target = resolve_tex_path(path.parent, include.group(1).strip())
        if include_target:
            figures.extend(collect_figures(include_target, macros, seen))

    return figures


def resolve_figure_path(base_dir: Path, reference: str) -> Path | None:
    candidate = (base_dir / reference).expanduser()
    if candidate.suffix and candidate.exists():
        return candidate.resolve()
    if candidate.suffix:
        stemmed = candidate.with_suffix("")
    else:
        stemmed = candidate
    for ext in FIGURE_EXTS:
        probe = stemmed.with_suffix(ext)
        if probe.exists():
            return probe.resolve()
    return None


def copy_displayable_figures(records: list[dict[str, object]], project_dir: Path, overwrite: bool) -> list[dict[str, str]]:
    dst_root = project_dir / "assets" / "figures"
    dst_root.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, str]] = []
    used_names: set[str] = set()

    for record in records:
        source = record.get("source")
        if not isinstance(source, Path) or not source.exists():
            continue
        if source.suffix.lower() not in DISPLAY_EXTS:
            continue

        target = dst_root / source.name
        if target.name in used_names:
            target = unique_path(target)
        elif target.exists() and overwrite:
            pass
        elif target.exists():
            used_names.add(target.name)
            copied.append({"filename": target.name, "caption": str(record.get("caption", "")), "source": str(source)})
            continue

        shutil.copy2(source, target)
        used_names.add(target.name)
        copied.append({"filename": target.name, "caption": str(record.get("caption", "")), "source": str(source)})

    return copied


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    parent = path.parent
    stem = path.stem
    suffix = path.suffix
    index = 2
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def update_bullet_fields(path: Path, updates: dict[tuple[str, str], str], overwrite: bool) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    current_section = ""
    result: list[str] = []

    for line in lines:
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current_section = heading.group(1).strip()
            result.append(line)
            continue

        bullet = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if not bullet:
            result.append(line)
            continue

        key = bullet.group(1).strip()
        existing = bullet.group(2).strip()
        replacement = updates.get((current_section, key))
        if replacement is None:
            result.append(line)
            continue

        if not should_replace(existing, overwrite):
            result.append(line)
            continue

        result.append(f"- {key}: {replacement}")

    path.write_text("\n".join(result) + "\n", encoding="utf-8")


def should_replace(existing: str, overwrite: bool) -> bool:
    if overwrite:
        return True
    if not existing:
        return True
    lowered = existing.lower()
    placeholders = ("[add", "optional", "yes or no", "workspace override", "`main` / `findings` / `workshop`")
    return any(token in lowered for token in placeholders)


def write_extract_summary(path: Path, main_tex: Path, extracted: dict[str, str], figures: list[dict[str, object]], copied: list[dict[str, str]]) -> None:
    lines = [
        "# LaTeX Extraction Summary",
        "",
        f"- Main tex: `{main_tex}`",
        f"- Title: {extracted.get('title', '')}",
        f"- Authors: {extracted.get('authors', '')}",
        f"- Affiliations: {extracted.get('affiliations', '')}",
        "",
        "## Abstract",
        "",
        extracted.get("abstract", "") or "[not found]",
        "",
        "## Figures",
        "",
    ]

    if not figures:
        lines.append("- No figures detected.")
    else:
        for index, figure in enumerate(figures, start=1):
            source = figure.get("source")
            source_text = str(source) if isinstance(source, Path) and source else str(figure.get("reference", ""))
            caption = str(figure.get("caption", "")).strip() or "[no caption]"
            lines.append(f"- Figure {index}: `{source_text}`")
            lines.append(f"  - Caption: {caption}")

    if copied:
        lines.extend(["", "## Copied displayable figures", ""])
        for item in copied:
            lines.append(f"- `{item['filename']}`")
            if item["caption"]:
                lines.append(f"  - Caption: {item['caption']}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    latex_dir = Path(args.latex_dir).expanduser().resolve()

    brief_path = project_dir / "poster_brief.md"
    summary_path = project_dir / "references" / "latex-extract.md"
    if not brief_path.exists():
        raise SystemExit(f"Missing poster brief: {brief_path}")
    if not latex_dir.exists():
        raise SystemExit(f"Missing LaTeX directory: {latex_dir}")

    main_tex = resolve_main_tex(latex_dir, args.main_tex)
    expanded = expand_tex(main_tex)
    macros = extract_simple_macros(expanded)

    title = clean_line(plain_tex(find_command_argument(expanded, "title"), macros))
    author_block = find_command_argument(expanded, "author")
    authors, affiliations = parse_authors_and_affiliations(author_block, macros)
    abstract = clean_line(plain_tex(find_environment(expanded, "abstract"), macros))
    takeaway = first_sentence(abstract) if abstract else ""

    figure_records = collect_figures(main_tex, macros)
    copied_figures = copy_displayable_figures(figure_records, project_dir, overwrite=args.overwrite) if args.copy_figures else []

    updates: dict[tuple[str, str], str] = {}
    if title:
        updates[("Paper", "Title")] = title
    if authors:
        updates[("Paper", "Authors")] = authors
    if affiliations:
        updates[("Paper", "Affiliations")] = affiliations
    if abstract:
        updates[("Text blocks", "Short abstract, 2 to 3 sentences")] = abstract
    if takeaway:
        updates[("Story", "One-sentence takeaway")] = takeaway

    for index, item in enumerate(copied_figures[:4], start=1):
        updates[("Must-have figures", f"Figure {index}")] = item["filename"]

    update_bullet_fields(brief_path, updates, overwrite=args.overwrite)
    write_extract_summary(summary_path, main_tex, {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "abstract": abstract,
    }, figure_records, copied_figures)

    print(f"Detected main tex: {main_tex}")
    if title:
        print(f"Extracted title: {title}")
    if authors:
        print(f"Extracted authors: {authors}")
    if affiliations:
        print(f"Extracted affiliations: {affiliations}")
    if abstract:
        print("Extracted abstract into poster_brief.md")
    if copied_figures:
        print(f"Copied {len(copied_figures)} displayable figure(s) into assets/figures/")
    print(f"Wrote extraction summary: {summary_path}")
    print(f"Updated poster brief: {brief_path}")


if __name__ == "__main__":
    main()
