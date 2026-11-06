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

## Implementation order

### Phase 1: source-controlled text (initial work)

- [x] Inventory the principal C++, Lua, and config string sources.
- [ ] Translate `Config/strings.xml` Chinese values into concise English with unchanged keys.
- [ ] Make mode names and descriptions English-first and fix inconsistencies; preserve game-mode enumeration and selection logic.
- [ ] Document exact first-pass translations and remaining work in this file.

### Phase 2: image-bearing UI assets

- [ ] Inspect actual rendered contents of `Menu.png`, `Select.png`, `UI.png`, `Result.png`, `NamePlate.png`, and `GameMode/*.png` to distinguish pictograms from Chinese text.
- [ ] Create an asset inventory: atlas file, sprite-frame key, original text, proposed English, rendered dimensions, usage site.
- [ ] Produce matching English text artwork. Image generation is allowed for replacements, but output must be manually checked for **correct wording, original dimensions, alpha transparency, legibility at in-game scale, and visual compatibility**.
- [ ] Prefer replacing text-only sprite graphics where practicable. If editing existing atlases, leave unrelated art untouched and preserve every `.plist` frame name and rectangle. Never merely resize/shift an atlas without updating its frame metadata.
- [ ] Where text ought to be dynamically localized, use font-rendered labels rather than regenerating many almost-identical sprites.
- [ ] Preserve Naruto character names and established proper nouns; translate the surrounding interface rather than renaming game identifiers.

### Phase 3: verification

- [ ] Source inspection: search gameplay code/config for remaining Chinese user-facing literals.
- [ ] Source inspection: confirm every visible Chinese graphic has an English counterpart or documented exception.
- [ ] Build and smoke-test on an available target, following `Doc/SMOKE_TEST_BASELINE.md` (boot → mode menu → select → battle → game over → menu).
- [ ] Test on a device configured to Chinese: English-first UI should stay English.
- [ ] Verify small-screen text clipping, bitmap font glyph support, tap targets, sprites, and gameplay regressions.
- [ ] Review screenshot diffs and only then mark localization ready to merge.

## Constraints and definition of done

- No changes to gameplay logic, network behavior, user data, or save formats.
- No generated text image is accepted merely because it looks convincing: spelling and layout must be checked.
- Existing animated/sliced atlas coordinates must remain valid.
- Translation is **not complete** until code strings *and* baked-in graphics are English and verified in a running build.

## Initial known English strings

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
