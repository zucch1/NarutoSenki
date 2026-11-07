"""TexturePacker frame normalization for both plist schemas in NarutoSenki.

Supported:
* Legacy: frame/rotated/sourceColorRect/sourceSize
* Current: textureRect/textureRotated/spriteSize/spriteSourceSize/spriteOffset

Coordinates are pixel-aligned and use top-left origins for atlas regions.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


def _numbers(value: str, count: int) -> tuple[int, ...]:
    found = [int(n) for n in re.findall(r"-?\d+", value)]
    if len(found) != count:
        raise ValueError(f"Invalid TexturePacker geometry: {value!r}")
    return tuple(found)


@dataclass(frozen=True)
class AtlasFrame:
    x: int
    y: int
    width: int
    height: int
    source_width: int
    source_height: int
    trim_x: int
    trim_y: int
    trim_width: int
    trim_height: int
    rotated: bool

    @property
    def packed_size(self) -> tuple[int, int]:
        return (self.height, self.width) if self.rotated else (self.width, self.height)

    def validate(self, atlas_size: tuple[int, int]) -> None:
        if min(self.x, self.y, self.trim_x, self.trim_y) < 0:
            raise ValueError(f"Negative atlas/trim coordinates: {self}")
        if min(self.width, self.height, self.source_width, self.source_height) <= 0:
            raise ValueError(f"Invalid nonpositive frame size: {self}")
        if (self.width, self.height) != (self.trim_width, self.trim_height):
            raise ValueError(f"Packed dimensions do not match unrotated trim: {self}")
        if (self.trim_x + self.trim_width > self.source_width or
                self.trim_y + self.trim_height > self.source_height):
            raise ValueError(f"Trim exceeds original sprite size: {self}")
        packed_w, packed_h = self.packed_size
        if self.x + packed_w > atlas_size[0] or self.y + packed_h > atlas_size[1]:
            raise ValueError(f"Packed rectangle exceeds atlas dimensions: {self}")


def parse_frame(info: dict) -> AtlasFrame:
    if "frame" in info:  # Old TexturePacker Cocos2d plist
        x, y, w, h = _numbers(info["frame"], 4)
        sx, sy, sw, sh = _numbers(info["sourceColorRect"], 4)
        source_w, source_h = _numbers(info["sourceSize"], 2)
        rotated = bool(info.get("rotated", False))
    elif "textureRect" in info:  # Newer TexturePacker Cocos2d plist
        x, y, w, h = _numbers(info["textureRect"], 4)
        source_w, source_h = _numbers(info["spriteSourceSize"], 2)
        sw, sh = _numbers(info["spriteSize"], 2)
        offset_x, offset_y = _numbers(info.get("spriteOffset", "{0,0}"), 2)
        rotated = bool(info.get("textureRotated", False))
        # Sprite offsets use upward-positive Y relative to untrimmed center.
        x0 = (source_w - sw) / 2 + offset_x
        y0 = (source_h - sh) / 2 - offset_y
        if not x0.is_integer() or not y0.is_integer():
            raise ValueError(f"Non-pixel-aligned sprite trim: {info!r}")
        sx, sy = int(x0), int(y0)
    else:
        raise ValueError("Unrecognized TexturePacker frame schema")
    return AtlasFrame(x, y, w, h, source_w, source_h,
                      sx, sy, sw, sh, rotated)
