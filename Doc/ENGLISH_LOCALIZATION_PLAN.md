# English localization: audit and implementation plan

**Repository:** `zucch1/NarutoSenki`  
**Working branch:** `i18n/english-first-pass-20261106`  
**Created:** 2026-11-06  
**Objective:** Make the playable game interface consistently **English**, without changing gameplay, saves, input handling, or scene transitions.

## Audit: where visible text comes from

| Source | Current behavior | English work |
| --- | --- | --- |
| `projects/NarutoSenki/Resources/Config/strings.xml` | Dictionary contains Chinese notices/errors, read by C++ | Translate values, preserve keys and parsing |
| `projects/NarutoSenki/Classes/UI/GameModeLayer.cpp` | Has Chinese/English branches based on device language; English has a mistaken Boss match size | Choose English strings consistently and correct labels |
| `projects/NarutoSenki/Classes/StartMenu.cpp` | Builds menu from images including `menu02_text.png`, `startmenu_title.png`, `news_btn.png` | Translate artwork or replace text layers with font-rendered English |
| `projects/NarutoSenki/lua/ui/SelectLayer.lua` | Uses buttons and character-title image frames such as `*_font.png` | Localize visibly Chinese selection graphics |
| `projects/NarutoSenki/Classes/GameOver.cpp`, `LoadLayer.cpp`, `GearLayer.cpp` | Titles/buttons and result labels are frequently sprite frames | Inventory and translate visible labels |
| `projects/NarutoSenki/Resources/GameMode/*.png` | Individual game-mode image buttons | Inspect each for baked-in Chinese text; regenerate where needed |
| `projects/NarutoSenki/Resources/{Menu,Select,UI,Result,NamePlate,Record,Record2,Report}.png` plus matching `.plist` | Texture atlases with tightly defined frame rectangles | Preserve atlas geometry and frame keys during graphic replacement |
| Android `res/values-{en,ja-rJP,zh-rCN}/strings.xml` | Mostly app-name resources | Not a substitute for in-game UI localization |

The README is already available in English. This is a game UI localization project, not a source-code-language rewrite.

## Mandatory English terminology policy

**Source of truth:** [NARUTO_ENGLISH_TERMINOLOGY.md](NARUTO_ENGLISH_TERMINOLOGY.md). This applies to **every** translated source string, C++/Lua label, skill name, character form, texture atlas, and newly generated English graphic.

- Use established English Naruto **manga terminology**, preferring the licensed VIZ English manga and cross-checking official English Naruto material. Examples: **Rasengan**, **Sharingan**, **Chidori**, **Shadow Clone Jutsu**, **Summoning Jutsu**, **Amaterasu**, **Susanoo**, and **Tsukuyomi**. Never replace these with literal phrases such as "Rotating Sphere" or "Copy Wheel Eye".
- Use concise, natural English for generic interface text. Keep game identifiers, XML keys, sprite-frame names, and gameplay semantics unchanged.
- **Identify the move before translating it**: a skill index, romanized filename, or character association alone is not evidence of a specific jutsu.
- If a game-specific label is not a confirmed canonical form (for example, `ImmortalSasuke`), mark it **NEEDS REVIEW** in the glossary and do not present a guessed replacement as official.
- Apply an English term consistently to text and graphic assets; generated image text is only accepted after verifying the translated wording, original sprite geometry/transparency, and in-game legibility.
- Do not treat source-string translation as completion of UI localization while baked-in Chinese text remains visible.

## Implementation order

### Phase 1: source-controlled text (initial work)

- [x] Inventory the principal C++, Lua, and config string sources.
- [x] Translate `Config/strings.xml` Chinese values into concise English with unchanged keys.
- [x] Make mode names and descriptions English-first and fix inconsistencies; preserve game-mode enumeration and selection logic.
- [x] Document exact first-pass translations and remaining work in this file.
- [x] Record canonical Naruto manga terminology as a binding rule in the glossary and plan.

### Recorded implementation progress (2026-11-06)

- Source strings: translated six Chinese values in `Config/strings.xml` while preserving the dictionary keys and original English news notice.
- Mode selector: removed locale-based Chinese names, corrected Boss mode to `3 VS 1`, and fixed `In development` wording.
- Start menu: the selection-description text now uses `CCLabelTTF` with English strings rather than `menu0*_text.png` frames. Other graphic text remains untouched.
- Character select: the selected hero's name is now rendered as English TTF text via `ui.newTTFLabel`, with explicit readable names for selected special forms and camel-case fallback. **Some game-specific labels are provisional pending glossary review**; positioning/font sizing also require runtime inspection.
- Atlas metadata audit: `Menu` has 49 frames, `Select` 143, `UI` 276, `Result` 77, and `Record2` 208. Not all frames contain text.
- Sprite review tooling: `tools/export_text_sprites.py` exports possible text sprites from TexturePacker PNG/plist pairs with original dimensions and a CSV manifest for human translation review. `tools/repack_english_sprites.py` can inject reviewed replacement PNGs into the *same original fixed atlas rectangles*, refusing oversized artwork and leaving the original files untouched. Both require Python 3 and Pillow. Use:

```bash
python3 -m pip install Pillow
python3 tools/export_text_sprites.py --output english-sprite-audit
# Edit only reviewed frames under english-sprite-audit/<Atlas>/<Frame>.png.
python3 tools/repack_english_sprites.py --replacements english-sprite-audit \
    --output english-repacked-atlases
```

**Blocker for image translation:** The connected repository reader exposed text and atlas metadata, but not binary PNG contents. The sprite art has **not** been visually inspected or replaced in the checked-in game resources. The export utility can run in a checkout with the assets; generated English artwork must be verified and imported separately. No game build or smoke test has run.

### Phase 2: image-bearing UI assets

- [ ] Inspect actual rendered contents of `Menu.png`, `Select.png`, `UI.png`, `Result.png`, `NamePlate.png`, and `GameMode/*.png` to distinguish pictograms from Chinese text.
- [ ] Create an asset inventory: atlas file, sprite-frame key, original text, **canon-checked English term**, evidence, rendered dimensions, usage site.
- [ ] Produce matching English text artwork **only after identifying and checking each Naruto technique against the terminology glossary**. Image generation is allowed for replacements, but output must be manually checked for **canonical wording, original dimensions, alpha transparency, legibility at in-game scale, and visual compatibility**.
- [ ] Prefer replacing text-only sprite graphics where practicable. If editing existing atlases, leave unrelated art untouched and preserve every `.plist` frame name and rectangle. Never merely resize/shift an atlas without updating its frame metadata.
- [ ] Where text ought to be dynamically localized, use font-rendered labels rather than regenerating many almost-identical sprites.
- [ ] Preserve Naruto character names and established proper nouns; translate the surrounding interface rather than renaming game identifiers.

### Phase 3: verification

- [ ] Source inspection: search gameplay code/config for remaining Chinese user-facing literals and invented noncanonical jutsu translations.
- [ ] Source inspection: confirm every visible Chinese graphic has a canon-checked English counterpart or documented exception.
- [ ] Build and smoke-test on an available target, following `Doc/SMOKE_TEST_BASELINE.md` (boot → mode menu → select → battle → game over → menu).
- [ ] Test on a device configured to Chinese: English-first UI should stay English.
- [ ] Verify small-screen text clipping, bitmap font glyph support, tap targets, sprites, and gameplay regressions.
- [ ] Review screenshot diffs and only then mark localization ready to merge.

## Constraints and definition of done

- No changes to gameplay logic, network behavior, user data, or save formats.
- No generated text image is accepted merely because it looks convincing: canonical Naruto English terminology, spelling and layout must all be checked.
- Existing animated/sliced atlas coordinates must remain valid.
- Translation is **not complete** until code strings *and* baked-in graphics are English and verified in a running build.

## Initial known English UI strings

| Key/context | English |
| --- | --- |
| `UpdateNotice` | Update announcement |
| `Failed` | Operation failed |
| `Successed` | Operation successful |
| `ComingSoon` | Coming soon |
| `LimitedChar` | This character cannot be selected |
| `ServerMainten` | The server is undergoing maintenance. Please try again later. |
| Classic mode | Classic Mode |
| Hardcore mode | Hardcore (4 vs. 4); Equipment disabled |
| Boss mode | Boss (3 vs. 1) |
| Clone | Clone (3 vs. 3) |
| Deathmatch | Deathmatch (3 vs. 3) |
| Random Deathmatch | Random Deathmatch (3 vs. 3) |

**Known limitation:** Inspection and source edits do not establish a successful build or prove that the raster UI is localized.
