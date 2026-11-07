# Localization (English / Chinese)

The game ships in two languages. Players switch with the **EN | 中文** button
in the top-right corner of the main menu. The choice is saved under the
`language` key in UserDefault. On first launch the game follows the device
language: Chinese devices start in Chinese, all others in English.

## How it works

Almost all of the game's text is drawn into the sprite sheets, not stored as
strings. Examples are skill descriptions (`Record2`), character name plates
(`Select`), gear details (`Gears`), menu captions (`Menu`), loading tips, the
pause screen and the "BATTLE START" banner (`Ougis`).

For English, `build_en_atlases.py` draws replacement frames with **the same
frame names** and packs them into `Resources/Lang/en/<Atlas>.plist/.png`.
When English is active, `addSprites()` (C++, `Classes/Utils/Cocos2dxHelper.hpp`)
and `tools.addSprites()` (Lua, `lua/utils/utils.lua`) load the override atlas
right after the original one. Every existing `createWithSpriteFrameName(...)`
then shows the English frame, so none of the screen code had to change.
The original Chinese art is never modified.

The few real strings live in:

| What | Chinese | English |
|---|---|---|
| Tips and notices | `Resources/Config/strings.xml` | `Resources/Config/strings_en.xml` |
| Game mode labels | `Classes/UI/GameModeLayer.cpp` | same file |
| Anything new | `Lang::tr("English", "中文")` in C++ / `lang.tr(...)` in Lua | |

## Editing translations

* `skills.tsv`: one row per skill. Columns are frame name, Chinese source text
  (transcribed from the original image, for reference) and English.
* `ui.tsv`: everything else. Columns are atlas, frame, render style, Chinese
  source and English. For name plates, `BIG|small` puts two lines on the plate.
  For gear, `Title|Description` does the same.

Then rebuild:

```bash
pip install pillow numpy opencv-python   # once
python3 tools/i18n/build_en_atlases.py
```

Commit the regenerated files in `projects/NarutoSenki/Resources/Lang/`.

The language button includes "中文", so rebuilding it needs a CJK font. The
script looks for IPAGothic, Noto Sans CJK and similar fonts via `fc-match`, or
uses `CJK_FONT=/path/to/font.ttf`. If none is found, it keeps the existing button.

## Adding a third language

1. Copy the TSVs, translate them, and point `OUT` at `Resources/Lang/<code>/`.
2. In `Classes/Utils/Lang.hpp` and `lua/utils/lang.lua`, make `current()`
   accept the new code and use `Lang/<code>/` in `overridePath()`.
3. Add a `strings_<code>.xml`.

## Translation notes

Jutsu names follow the English anime/manga (Viz) terms where one exists,
for example *Kishō Tensei → One's Own Life Reincarnation* and *Shiki Fūjin →
Reaper Death Seal*. Some moves are made up for this game and have no
canon name. Their English names are literal translations:

* Chiyo 2, 傀儡术·操术琥珀 → *Puppet Technique: Amber Puppetry*
* Hinata 4, 白胧天舞 → *White Haze Heavenly Dance*
* Ino 4, 蝶燐 → *Butterfly Glimmer*
* Jugo 1, 铜腕缚 → *Bronze Arm Bind*
* Shikamaru 1, 军师演法 → *Strategist's Gambit*
* Minato 1, 忍爱之剑 → *Marked Kunai* (the source's wording is a pun; this name describes what the skill does)

Not translated, on purpose:

* Frames the code never displays (`Ranking.plist` text, `quit_title`,
  `warning_title`, `createGroup_tip`).
* Buttons whose kanji is decoration next to English (`Return 返`, `Skill 術`,
  the `名人堂 Hall of Fame` badge).

## Fonts

* `fonts/Bangers-Regular.ttf`: SIL Open Font License (`OFL-Bangers.txt`)
* `fonts/SourceSans3-Bold.ttf`: SIL Open Font License (`LICENSE-SourceSans3.md`)

The fonts are only used to build the PNGs. The game doesn't load them.
