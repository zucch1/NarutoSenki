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
from pathlib import Path

from PIL import Image

from atlas_layout import parse_frame

ATLAS_NAMES = ("Menu", "Select", "UI", "Result", "Record", "Record2", "Report", "NamePlate")
# Heuristic only: a name implies a *possible* text asset, not proof of Chinese text.
TEXT_MARKERS = ("text", "font", "title", "label", "tips", "notice", "loading",
                "start_btn", "return_btn", "news_btn", "login_btn", "menu0",
                "surrender", "result_defeat", "com_label", "change_btn",
                "yes_btn", "no_btn", "ranking_btn", "skill_btn")



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

        geom = parse_frame(info)
        geom.validate(atlas.size)
        region_w, region_h = geom.packed_size
        sprite = atlas.crop((geom.x, geom.y,
                             geom.x + region_w, geom.y + region_h))
        if geom.rotated:
            sprite = sprite.rotate(90, expand=True)

        if sprite.size != (geom.trim_width, geom.trim_height):
            raise ValueError(f"{name}/{sprite_name}: trimmed dimensions mismatch")

        full = Image.new("RGBA", (geom.source_width, geom.source_height))
        full.alpha_composite(sprite, (geom.trim_x, geom.trim_y))
        destination = output / name / sprite_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        full.save(destination)
        rows.append({
            "atlas": name,
            "sprite": sprite_name,
            "source_width": geom.source_width,
            "source_height": geom.source_height,
            "rotated": int(geom.rotated),
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
