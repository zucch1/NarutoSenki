#!/usr/bin/env python3
"""Export candidate text sprites from Cocos2d-x TexturePacker atlases.

Usage:
    python3 -m pip install Pillow
    python3 tools/export_text_sprites.py \
        --resources projects/NarutoSenki/Resources \
        --output /tmp/naruto-english-sprites

Default output contains frames likely to include words. Use --all for every
frame. Source files are read-only; atlas PNGs and plist coordinates are never
modified. Manually confirm the language of each exported image.
"""
from __future__ import annotations

import argparse
import csv
import plistlib
import re
from pathlib import Path

from PIL import Image

ATLAS_NAMES = ("Menu", "Select", "UI", "Result", "Record", "Record2", "Report", "NamePlate")
# Heuristic only: a name implies a *possible* text asset, not proof of Chinese text.
TEXT_MARKERS = ("text", "font", "title", "label", "tips", "notice", "loading",
                "start_btn", "return_btn", "news_btn", "login_btn", "menu0",
                "surrender", "result_defeat", "com_label", "change_btn",
                "yes_btn", "no_btn", "ranking_btn", "skill_btn")


def bounds(value: str) -> tuple[int, int, int, int]:
    numbers = [int(v) for v in re.findall(r"-?\d+", value)]
    if len(numbers) != 4:
        raise ValueError(f"Invalid TexturePacker rectangle: {value!r}")
    return tuple(numbers)


def size(value: str) -> tuple[int, int]:
    numbers = [int(v) for v in re.findall(r"-?\d+", value)]
    if len(numbers) != 2:
        raise ValueError(f"Invalid sourceSize: {value!r}")
    return tuple(numbers)


def export_atlas(resources: Path, name: str, output: Path, include_all: bool) -> list[dict]:
    plist_path = resources / f"{name}.plist"
    png_path = resources / f"{name}.png"
    if not plist_path.is_file() or not png_path.is_file():
        return []

    with plist_path.open("rb") as file:
        data = plistlib.load(file)
    atlas = Image.open(png_path).convert("RGBA")
    rows: list[dict] = []
    for sprite_name, info in data["frames"].items():
        candidate = any(word in sprite_name.lower() for word in TEXT_MARKERS)
        if not (include_all or candidate):
            continue

        x, y, w, h = bounds(info["frame"])
        rotated = bool(info.get("rotated", False))
        # TexturePacker stores 90-degree rotated sprite pixels as h-by-w.
        region_w, region_h = (h, w) if rotated else (w, h)
        if x < 0 or y < 0 or x + region_w > atlas.width or y + region_h > atlas.height:
            raise ValueError(f"{name}/{sprite_name}: rectangle outside atlas")
        sprite = atlas.crop((x, y, x + region_w, y + region_h))
        if rotated:
            sprite = sprite.rotate(90, expand=True)

        source_w, source_h = size(info["sourceSize"])
        color_x, color_y, color_w, color_h = bounds(info["sourceColorRect"])
        if sprite.size != (color_w, color_h):
            raise ValueError(f"{name}/{sprite_name}: trimmed dimensions mismatch")
        if color_x < 0 or color_y < 0 or color_x + color_w > source_w or color_y + color_h > source_h:
            raise ValueError(f"{name}/{sprite_name}: sourceColorRect outside sourceSize")

        full = Image.new("RGBA", (source_w, source_h))
        full.alpha_composite(sprite, (color_x, color_y))
        destination = output / name / sprite_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        full.save(destination)
        rows.append({
            "atlas": name,
            "sprite": sprite_name,
            "source_width": source_w,
            "source_height": source_h,
            "rotated": int(rotated),
            "candidate_text": int(candidate),
            "export_path": str(destination.relative_to(output)),
            "observed_language": "",
            "english_translation": "",
            "review_status": "needs_visual_review",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=Path("projects/NarutoSenki/Resources"))
    parser.add_argument("--output", type=Path, default=Path("english-sprite-audit"))
    parser.add_argument("--all", action="store_true", help="Export every sprite, not only likely text")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for name in ATLAS_NAMES:
        rows.extend(export_atlas(args.resources, name, args.output, args.all))
    manifest = args.output / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "atlas", "sprite", "source_width", "source_height", "rotated",
            "candidate_text", "export_path", "observed_language",
            "english_translation", "review_status",
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} sprites to {args.output}; manifest: {manifest}")


if __name__ == "__main__":
    main()
