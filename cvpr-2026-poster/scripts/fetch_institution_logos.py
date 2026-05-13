#!/usr/bin/env python3
"""
Fetch institution logos into assets/logos/auto/ as a fallback when the user
did not manually provide school or lab logos.

Example:
    python3 scripts/fetch_institution_logos.py --project-dir ./poster-workspace
"""

from __future__ import annotations

import argparse
import html
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DISPLAY_EXTS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"}
USER_AGENT = "Mozilla/5.0 (compatible; CVPRPosterSkill/1.0; +https://github.com/yunyiliu/cvpr-2026-poster-skill)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch institution logos as a fallback.")
    parser.add_argument("--project-dir", required=True, help="Poster workspace directory.")
    parser.add_argument("--force", action="store_true", help="Fetch even if user logos already exist.")
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

    return sections


def get_value(sections: dict[str, dict[str, object]], section: str, key: str) -> str:
    value = sections.get(section, {}).get(key, "")
    if isinstance(value, list):
        return " ".join(str(item) for item in value if str(item).strip())
    return str(value).strip()


def get_list(sections: dict[str, dict[str, object]], section: str, key: str) -> list[str]:
    value = sections.get(section, {}).get(key, [])
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def fetch_logos_if_missing(project_dir: Path, force: bool = False, verbose: bool = True) -> list[Path]:
    project_dir = Path(project_dir).expanduser().resolve()
    assets_logos = project_dir / "assets" / "logos"
    auto_dir = assets_logos / "auto"
    auto_dir.mkdir(parents=True, exist_ok=True)

    existing_manual = [
        path for path in assets_logos.rglob("*")
        if path.is_file() and path.suffix.lower() in DISPLAY_EXTS and "official" not in path.parts and "auto" not in path.parts
    ]
    if existing_manual and not force:
        if verbose:
            print("User logos already exist in assets/logos/. Skipping auto-fetch.")
        return []

    brief_path = project_dir / "poster_brief.md"
    if not brief_path.exists():
        if verbose:
            print(f"Missing poster brief: {brief_path}")
        return []

    sections = parse_brief(brief_path)
    institution_websites = get_list(sections, "Paper", "Institution websites, optional")
    affiliations_text = get_value(sections, "Paper", "Affiliations")
    institutions = infer_institutions(affiliations_text)

    saved: list[Path] = []
    seen_domains: set[str] = set()
    covered_institutions: set[str] = set()

    for index, website in enumerate(institution_websites):
        hint = institutions[index] if index < len(institutions) else url_domain(website)
        try:
            saved_path = fetch_logo_from_website(website, auto_dir, institution_hint=hint)
        except Exception:
            saved_path = None
        if saved_path:
            seen_domains.add(url_domain(website))
            saved.append(saved_path)
            if index < len(institutions):
                covered_institutions.add(institution_key(institutions[index]))
            if verbose:
                print(f"Fetched logo from {website} -> {saved_path.name}")

    for institution in institutions:
        key = institution_key(institution)
        if key in covered_institutions:
            continue
        if any(token_match(institution, path.stem) for path in saved):
            covered_institutions.add(key)
            continue
        homepage = search_official_homepage(institution)
        if not homepage:
            continue
        domain = url_domain(homepage)
        if domain in seen_domains:
            continue
        try:
            saved_path = fetch_logo_from_website(homepage, auto_dir, institution_hint=institution)
        except Exception:
            saved_path = None
        if saved_path:
            seen_domains.add(domain)
            saved.append(saved_path)
            covered_institutions.add(key)
            if verbose:
                print(f"Fetched logo for {institution} -> {saved_path.name}")

    if verbose and not saved:
        print("No institution logos were fetched automatically.")
    return saved


def infer_institutions(text: str) -> list[str]:
    if not text:
        return []
    cleaned = re.sub(r"\[[^\]]+\]|\([^)]+\)|\b\d+\b", "", text)
    parts = re.split(r";|\||\band\b", cleaned, flags=re.IGNORECASE)
    institutions = []
    for part in parts:
        candidate = part.strip(" ,")
        if len(candidate) < 4:
            continue
        institutions.append(candidate)
    return dedupe(institutions)


def search_official_homepage(institution: str) -> str | None:
    query = urllib.parse.quote(f"{institution} official site")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    html_text = fetch_text(url)
    if not html_text:
        return None

    urls = re.findall(r'href="(?:/l/\?kh=-1&uddg=|//duckduckgo.com/l/\?uddg=)([^"]+)"', html_text)
    for encoded in urls:
        decoded = urllib.parse.unquote(html.unescape(encoded))
        if decoded.startswith("http"):
            return decoded

    links = re.findall(r'href="(https?://[^"]+)"', html_text)
    for link in links:
        if "duckduckgo.com" not in link:
            return html.unescape(link)
    return None


def fetch_logo_from_website(website: str, output_dir: Path, institution_hint: str = "") -> Path | None:
    html_text = fetch_text(website)
    if not html_text:
        return None

    candidates = extract_logo_candidates(html_text, website, institution_hint)
    for candidate in sorted(candidates, key=lambda item: item["score"], reverse=True):
        saved = download_logo(candidate["url"], output_dir, slugify(institution_hint or url_domain(website)))
        if saved:
            return saved
    return None


def extract_logo_candidates(html_text: str, page_url: str, institution_hint: str = "") -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    lower_hint = institution_hint.lower()

    for match in re.finditer(r"<img\b([^>]+)>", html_text, flags=re.IGNORECASE):
        attrs = parse_attrs(match.group(1))
        src = attrs.get("src", "")
        if not src or src.startswith("data:"):
            continue
        absolute = urllib.parse.urljoin(page_url, html.unescape(src))
        score = 0
        haystack = " ".join([attrs.get("alt", ""), attrs.get("class", ""), attrs.get("id", ""), src]).lower()
        if "logo" in haystack or "brand" in haystack:
            score += 80
        if lower_hint and any(token in haystack for token in keywords_for_hint(lower_hint)):
            score += 30
        if absolute.lower().endswith(".svg"):
            score += 30
        elif absolute.lower().endswith(".png"):
            score += 18
        if any(bad in haystack for bad in ("icon", "favicon", "avatar", "sprite")):
            score -= 40
        if score > 0:
            candidates.append({"url": absolute, "score": score})

    for match in re.finditer(r"<meta\b([^>]+property=['\"]og:image['\"][^>]*)>", html_text, flags=re.IGNORECASE):
        attrs = parse_attrs(match.group(1))
        content = attrs.get("content", "")
        if content:
            candidates.append({"url": urllib.parse.urljoin(page_url, html.unescape(content)), "score": 18})

    for match in re.finditer(r"<link\b([^>]+)>", html_text, flags=re.IGNORECASE):
        attrs = parse_attrs(match.group(1))
        rel = attrs.get("rel", "").lower()
        href = attrs.get("href", "")
        if not href:
            continue
        absolute = urllib.parse.urljoin(page_url, html.unescape(href))
        haystack = f"{rel} {href}".lower()
        score = 0
        if "logo" in haystack:
            score += 40
        if "icon" in haystack:
            score += 8
        if absolute.lower().endswith(".svg"):
            score += 16
        elif absolute.lower().endswith(".png"):
            score += 8
        if score > 0:
            candidates.append({"url": absolute, "score": score})

    deduped: dict[str, dict[str, object]] = {}
    for candidate in candidates:
        current = deduped.get(candidate["url"])
        if current is None or candidate["score"] > current["score"]:
            deduped[candidate["url"]] = candidate
    return list(deduped.values())


def parse_attrs(fragment: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value1, value2, value3 in re.findall(
        r"([a-zA-Z_:.-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
        fragment,
    ):
        attrs[key.lower()] = value1 or value2 or value3 or ""
    return attrs


def download_logo(url: str, output_dir: Path, stem: str) -> Path | None:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "").lower()
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    if len(data) < 40:
        return None

    ext = suffix_from_url_or_type(url, content_type, data)
    if ext not in DISPLAY_EXTS:
        return None

    filename = unique_path(output_dir / f"{stem}{ext}")
    filename.write_bytes(data)
    return filename


def suffix_from_url_or_type(url: str, content_type: str, data: bytes) -> str:
    path_ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if path_ext in DISPLAY_EXTS:
        return path_ext
    if "svg" in content_type or data.lstrip().startswith(b"<svg"):
        return ".svg"
    if "png" in content_type or data.startswith(b"\x89PNG"):
        return ".png"
    if "jpeg" in content_type or data.startswith(b"\xff\xd8"):
        return ".jpg"
    if "gif" in content_type or data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if "webp" in content_type or data[:4] == b"RIFF":
        return ".webp"
    return ""


def fetch_text(url: str) -> str:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=15) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="ignore")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return ""


def url_domain(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.lower()


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "institution-logo"


def institution_key(text: str) -> str:
    return slugify(text)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 2
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def token_match(left: str, right: str) -> bool:
    left_tokens = set(re.findall(r"[a-z0-9]+", left.lower()))
    right_tokens = set(re.findall(r"[a-z0-9]+", right.lower()))
    return bool(left_tokens & right_tokens)


def keywords_for_hint(hint: str) -> list[str]:
    words = [word for word in re.findall(r"[a-z0-9]+", hint.lower()) if len(word) > 2]
    return words[:4]


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def main() -> None:
    args = parse_args()
    saved = fetch_logos_if_missing(Path(args.project_dir), force=args.force, verbose=True)
    if saved:
        print(f"Saved {len(saved)} auto-fetched logo(s).")


if __name__ == "__main__":
    main()
