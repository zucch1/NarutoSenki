#!/usr/bin/env python3
"""Render checked English translations as frame-exact transparent text sprites.

This does NOT translate Chinese: only records explicitly marked
`approved_for_rendering` in the reviewed CSV manifest are rendered.

Example:
    python3 tools/render_english_sprite_text.py \
      --manifest Doc/ENGLISH_SPRITE_AUDIT.csv \
      --output english-generated-sprites
    python3 tools/repack_english_sprites.py \
      --replacements english-generated-sprites \
      --output english-repacked-atlases

Approve a record only after identifying its specific original text and
checking the manga-consistent English expression against
Doc/NARUTO_ENGLISH_TERMINOLOGY.md.

Only use this for text-only frames. If a frame includes icons or complex
background art, edit the original sprite instead of replacing it with text.
"""
from __future__ import annotations

import argparse
import csv
import plistlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from atlas_layout import parse_frame

APPROVED = "approved_for_rendering"
DEFAULT_FONTS = (
    "DejaVuSansCondensed-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "LiberationSans-Bold.ttf",
)


def get_font(size: int, preferred: str | None) -> ImageFont.FreeTypeFont:
    for name in ([preferred] if preferred else []) + list(DEFAULT_FONTS):
        if not name:
            continue
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise FileNotFoundError(
        "No suitable TrueType font found; specify an installed font via --font"
    )


def generate_sprite(
    info: dict,
    translation: str,
    font_name: str | None,
    palette: str = "white",
) -> Image.Image:
    if not translation or not translation.strip():
        raise ValueError("An approved translation cannot be empty")
    if "\n" in translation or "\r" in translation:
        raise ValueError("Single-line atlas frames require single-line text")
    geom = parse_frame(info)
    # Text is restricted to the original trimmed rectangle so plist positions
    # and dimensions can remain byte-for-byte unchanged after repacking.
    tw, th = geom.trim_width, geom.trim_height
    if tw < 8 or th < 8:
        raise ValueError("Frame is too small to contain readable English text")
    outline = 1 if th >= 18 else 0
    fill = (255, 245, 223, 255) if palette == "gold" else (255, 255, 255, 255)
    stroke = (39, 22, 14, 255) if palette == "gold" else (15, 15, 15, 255)
    # Render at 2x resolution, then downscale for legible small UI glyphs.
    scale = 2
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    found = None
    for size in range(min(18, th - 2), 7, -1):
        font = get_font(size * scale, font_name)
        bbox = probe.textbbox((0, 0), translation, font=font, stroke_width=outline * scale)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if width <= (tw - 2) * scale and height <= (th - 2) * scale:
            found = (font, bbox)
            break
    if found is None:
        raise ValueError(
            f"Cannot fit {translation!r} into sprite trim {(tw, th)} "
            "without illegibly small text"
        )
    font, bbox = found
    expanded = Image.new("RGBA", (tw * scale, th * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(expanded)
    x = ((tw * scale - (bbox[2] - bbox[0])) // 2) - bbox[0]
    y = ((th * scale - (bbox[3] - bbox[1])) // 2) - bbox[1]
    draw.text((x, y), translation, font=font, fill=fill,
              stroke_width=outline * scale, stroke_fill=stroke)
    trimmed = expanded.resize((tw, th), Image.Resampling.LANCZOS)
    full = Image.new("RGBA", (geom.source_width, geom.source_height), (0, 0, 0, 0))
    full.paste(trimmed, (geom.trim_x, geom.trim_y))
    return full


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=Path("Doc/ENGLISH_SPRITE_AUDIT.csv"))
    p.add_argument("--resources", type=Path, default=Path("projects/NarutoSenki/Resources"))
    p.add_argument("--output", type=Path, default=Path("english-generated-sprites"))
    p.add_argument("--font", help="Path or family name of a locally installed TrueType font")
    args = p.parse_args()

    if not args.manifest.is_file():
        raise SystemExit(f"Missing translation manifest: {args.manifest}")
    with args.manifest.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    atlas_cache: dict[str, dict] = {}
    count = 0
    for row in rows:
        if row["translation_status"] != APPROVED:
            continue
        name, key = row["atlas"], row["sprite"]
        target = row.get("approved_english", "").strip()
        if not target:
            raise ValueError(f"Approved sprite {name}/{key} has no English text")
        if name not in atlas_cache:
            with (args.resources / f"{name}.plist").open("rb") as file:
                atlas_cache[name] = plistlib.load(file)["frames"]
        frames = atlas_cache[name]
        if key not in frames:
            raise ValueError(f"Unknown sprite frame {name}/{key}")
        if Path(key).name != key or not key.endswith(".png"):
            raise ValueError(f"Unsafe/invalid sprite name: {key}")
        color = "white" if name == "Record2" else "gold"
        sprite = generate_sprite(frames[key], target, args.font, color)
        target_file = args.output / name / key
        target_file.parent.mkdir(parents=True, exist_ok=True)
        sprite.save(target_file)
        print(f"Rendered {name}/{key}: {target}")
        count += 1
    print(f"Rendered {count} approved English text sprites to {args.output}")
    if count == 0:
        raise SystemExit(
            "No verified translations were marked approved_for_rendering; "
            "see Doc/NARUTO_ENGLISH_TERMINOLOGY.md"
        )


if __name__ == "__main__":
    main()
