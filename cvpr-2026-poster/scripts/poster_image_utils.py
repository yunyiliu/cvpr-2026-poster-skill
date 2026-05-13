#!/usr/bin/env python3
"""
Utilities for reading local image dimensions without external dependencies.
"""

from __future__ import annotations

import struct
import xml.etree.ElementTree as ET
from pathlib import Path


def get_image_size(path: Path) -> tuple[int, int] | None:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return _png_size(path)
    if suffix in {".jpg", ".jpeg"}:
        return _jpeg_size(path)
    if suffix == ".gif":
        return _gif_size(path)
    if suffix == ".svg":
        return _svg_size(path)
    return None


def aspect_ratio(path: Path) -> float | None:
    size = get_image_size(path)
    if not size or not size[1]:
        return None
    return size[0] / size[1]


def classify_aspect(ratio: float | None) -> str:
    if ratio is None:
        return "unknown"
    if ratio >= 1.8:
        return "very-wide"
    if ratio >= 1.25:
        return "wide"
    if ratio >= 0.85:
        return "square"
    return "tall"


def _png_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        data = handle.read(24)
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def _gif_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        data = handle.read(10)
    if len(data) < 10 or data[:6] not in {b"GIF87a", b"GIF89a"}:
        return None
    return struct.unpack("<HH", data[6:10])


def _jpeg_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        data = handle.read()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None

    index = 2
    while index < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9}:
            continue
        if index + 1 >= len(data):
            break
        length = struct.unpack(">H", data[index:index + 2])[0]
        if length < 2 or index + length > len(data):
            break
        if marker in {
            0xC0, 0xC1, 0xC2, 0xC3,
            0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB,
            0xCD, 0xCE, 0xCF,
        }:
            start = index + 3
            if start + 4 > len(data):
                break
            height, width = struct.unpack(">HH", data[start:start + 4])
            return width, height
        index += length
    return None


def _svg_size(path: Path) -> tuple[int, int] | None:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    view_box = root.attrib.get("viewBox")
    if view_box:
        parts = view_box.replace(",", " ").split()
        if len(parts) == 4:
            try:
                width = float(parts[2])
                height = float(parts[3])
                if width > 0 and height > 0:
                    return int(round(width)), int(round(height))
            except ValueError:
                pass

    width = _parse_svg_length(root.attrib.get("width", ""))
    height = _parse_svg_length(root.attrib.get("height", ""))
    if width and height:
        return int(round(width)), int(round(height))
    return None


def _parse_svg_length(value: str) -> float | None:
    if not value:
        return None
    cleaned = value.strip().lower().replace("px", "")
    try:
        return float(cleaned)
    except ValueError:
        return None
