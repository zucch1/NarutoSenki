#!/usr/bin/env python3
"""Repack reviewed English sprite PNGs into existing TexturePacker atlas layout.

Example:
    python3 tools/repack_english_sprites.py \
      --resources projects/NarutoSenki/Resources \
      --replacements english-sprite-audit \
      --output /tmp/english-repacked-atlases

Replace only reviewed sprite PNGs in --replacements/<Atlas>/<Frame>.png.
Every replacement must be a RGBA PNG at the exact *sourceSize* exported by
export_text_sprites.py. The tool refuses lettering that extends outside the
original trimmed sprite rectangle. It never rewrites .plist coordinates and
never modifies the source Resource PNGs in-place.
"""
from __future__ import annotations

import argparse
import plistlib
from pathlib import Path

from PIL import Image

from atlas_layout import parse_frame

ATLAS_NAMES = ("Menu", "Select", "UI", "Result", "Record", "Record2", "Report", "NamePlate")



def process(resources: Path, replacements: Path, output: Path, atlas_name: str) -> int:
    atlas_path = resources / f"{atlas_name}.png"
    metadata_path = resources / f"{atlas_name}.plist"
    replacement_dir = replacements / atlas_name
    if not replacement_dir.is_dir():
        return 0
    with metadata_path.open("rb") as source:
        frames = plistlib.load(source)["frames"]
    atlas = Image.open(atlas_path).convert("RGBA")
    changed = 0
    for replacement in sorted(replacement_dir.glob("*.png")):
        name = replacement.name
        if name not in frames:
            raise ValueError(f"{atlas_name}: unknown frame {name}")
        geom = parse_frame(frames[name])
        geom.validate(atlas.size)
        with Image.open(replacement) as image:
            edited = image.convert("RGBA")
        if edited.size != (geom.source_width, geom.source_height):
            raise ValueError(
                f"{atlas_name}/{name}: expected size "
                f"{(geom.source_width, geom.source_height)}, got {edited.size}"
            )
        bbox = edited.getchannel("A").getbbox()
        if bbox and (bbox[0] < geom.trim_x or bbox[1] < geom.trim_y or
                     bbox[2] > geom.trim_x + geom.trim_width or
                     bbox[3] > geom.trim_y + geom.trim_height):
            raise ValueError(
                f"{atlas_name}/{name}: new text exceeds the original atlas trim region"
            )
        trimmed = edited.crop((
            geom.trim_x, geom.trim_y,
            geom.trim_x + geom.trim_width, geom.trim_y + geom.trim_height
        ))
        pixels = trimmed.rotate(-90, expand=True) if geom.rotated else trimmed
        if pixels.size != geom.packed_size:
            raise ValueError(
                f"{atlas_name}/{name}: packed dimensions "
                f"{pixels.size} != {geom.packed_size}"
            )
        # RGBA paste without a mask replaces the original pixels including alpha.
        atlas.paste(pixels, (geom.x, geom.y))
        changed += 1

    if changed:
        output.mkdir(parents=True, exist_ok=True)
        atlas.save(output / f"{atlas_name}.png")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=Path("projects/NarutoSenki/Resources"))
    parser.add_argument("--replacements", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("english-repacked-atlases"))
    args = parser.parse_args()

    count = 0
    for name in ATLAS_NAMES:
        changed = process(args.resources, args.replacements, args.output, name)
        if changed:
            print(f"{name}: replaced {changed} sprites")
        count += changed
    print(f"Repacked {count} sprites. Original resources remain unchanged.")
    if not count:
        raise SystemExit("No replacement frames found; no atlas files generated.")


if __name__ == "__main__":
    main()
