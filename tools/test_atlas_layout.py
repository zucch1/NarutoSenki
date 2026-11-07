"""Regression tests for the two TexturePacker metadata variants.

Run from the repository root:
    python3 -m unittest discover -s tools -p 'test_atlas_*.py' -v
Requires Pillow; tests use synthetic PNGs and do not modify game assets.
"""
from __future__ import annotations

import plistlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from atlas_layout import parse_frame
from export_text_sprites import export_atlas
from repack_english_sprites import process


class AtlasLayoutTests(unittest.TestCase):
    def test_legacy_metadata(self):
        frame = parse_frame({
            "frame": "{{10,20},{20,12}}",
            "sourceColorRect": "{{5,7},{20,12}}",
            "sourceSize": "{30,26}",
            "rotated": True,
        })
        self.assertEqual(frame.packed_size, (12, 20))
        self.assertEqual((frame.trim_x, frame.trim_y), (5, 7))
        frame.validate((128, 128))

    def test_modern_metadata_with_nonzero_offset(self):
        frame = parse_frame({
            "textureRect": "{{10,20},{20,10}}",
            "spriteSize": "{20,10}",
            "spriteSourceSize": "{40,30}",
            "spriteOffset": "{5,5}",
            "textureRotated": False,
        })
        self.assertEqual((frame.trim_x, frame.trim_y), (15, 5))
        self.assertEqual(frame.packed_size, (20, 10))
        frame.validate((128, 128))

    def test_export_and_repack_round_trip(self):
        for modern in (False, True):
            for rotated in (False, True):
                with self.subTest(modern=modern, rotated=rotated):
                    self._check_roundtrip(modern, rotated)

    def _check_roundtrip(self, modern: bool, rotated: bool) -> None:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            resources = root_path / "Resources"
            resources.mkdir()
            name = "Select" if modern else "Menu"
            trim_x, trim_y, trim_w, trim_h = 5, 7, 20, 12
            source = Image.new("RGBA", (30, 26))
            painter = ImageDraw.Draw(source)
            painter.rectangle((trim_x, trim_y,
                               trim_x + trim_w - 1, trim_y + trim_h - 1),
                              fill=(220, 150, 25, 240))
            painter.rectangle((trim_x + 1, trim_y + 2,
                               trim_x + 6, trim_y + 6),
                              fill=(45, 20, 200, 255))
            trimmed = source.crop((trim_x, trim_y,
                                   trim_x + trim_w, trim_y + trim_h))
            pixels = trimmed.rotate(-90, expand=True) if rotated else trimmed
            atlas = Image.new("RGBA", (128, 128))
            atlas.paste(pixels, (10, 20))
            atlas.save(resources / f"{name}.png")

            if modern:
                frame_data = {
                    "textureRect": "{{10,20},{20,12}}",
                    "textureRotated": rotated,
                    "spriteSize": "{20,12}",
                    "spriteSourceSize": "{30,26}",
                    "spriteOffset": "{0,0}",
                }
            else:
                frame_data = {
                    "frame": "{{10,20},{20,12}}",
                    "rotated": rotated,
                    "sourceColorRect": "{{5,7},{20,12}}",
                    "sourceSize": "{30,26}",
                }
            with (resources / f"{name}.plist").open("wb") as file:
                plistlib.dump({"frames": {"test_label.png": frame_data}}, file)

            extracted_dir = root_path / "extracted"
            rows = export_atlas(resources, name, extracted_dir, include_all=True)
            self.assertEqual(len(rows), 1)
            exported = Image.open(extracted_dir / name / "test_label.png").convert("RGBA")
            self.assertEqual(exported.tobytes(), source.tobytes())

            packed_dir = root_path / "packed"
            count = process(resources, extracted_dir, packed_dir, name)
            self.assertEqual(count, 1)
            repacked = Image.open(packed_dir / f"{name}.png").convert("RGBA")
            self.assertEqual(repacked.tobytes(), atlas.tobytes())

            # A replacement outside the frame's original trimmed rect must fail.
            exported.putpixel((0, 0), (255, 0, 0, 255))
            exported.save(extracted_dir / name / "test_label.png")
            with self.assertRaises(ValueError):
                process(resources, extracted_dir, root_path / "invalid", name)


if __name__ == "__main__":
    unittest.main()
