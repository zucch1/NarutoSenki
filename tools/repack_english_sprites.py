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
import re
from pathlib import Path

from PIL import Image

ATLAS_NAMES = ("Menu", "Select", "UI", "Result", "Record", "Record2", "Report", "NamePlate")


def numbers(value: str, count: int) -> tuple[int, ...]:
    match = [int(n) for n in re.findall(r"-?\d+", value)]
    if len(match) != count:
        raise ValueError(f"Invalid TexturePacker size/rectangle: {value!r}")
    return tuple(match)


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
        info = frames[name]
        x, y, w, h = numbers(info["frame"], 4)
        sx, sy, sw, sh = numbers(info["sourceColorRect"], 4)
        source_w, source_h = numbers(info["sourceSize"], 2)
        with Image.open(replacement) as image:
            edited = image.convert("RGBA")
        if edited.size != (source_w, source_h):
            raise ValueError(
                f"{atlas_name}/{name}: expected size {(source_w, source_h)}, got {edited.size}"
            )
        bbox = edited.getchannel("A").getbbox()
        if bbox and (bbox[0] < sx or bbox[1] < sy or
                     bbox[2] > sx + sw or bbox[3] > sy + sh):
            raise ValueError(
                f"{atlas_name}/{name}: new text exceeds the original atlas trim region"
            )
        trimmed = edited.crop((sx, sy, sx + sw, sy + sh))
        rotated = bool(info.get("rotated", False))
        pixels = trimmed.rotate(-90, expand=True) if rotated else trimmed
        expected = (h, w) if rotated else (w, h)
        if pixels.size != expected:
            raise ValueError(
                f"{atlas_name}/{name}: packed dimensions {pixels.size} != {expected}"
            )
        if x < 0 or y < 0 or x + pixels.width > atlas.width or y + pixels.height > atlas.height:
            raise ValueError(f"{atlas_name}/{name}: rectangle exceeds atlas bounds")
        # RGBA paste without a mask replaces the original pixels including alpha.
        atlas.paste(pixels, (x, y))
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
