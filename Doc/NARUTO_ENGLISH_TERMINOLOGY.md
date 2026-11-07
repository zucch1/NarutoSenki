# Naruto Senki — English terminology and localization style guide

**Status:** Active policy for the English-localization branch.  
**Scope:** Every user-facing C++/Lua string, help text, character-form name, skill label, and worded image/sprite.  
**Authority:** The established English names in the officially published *Naruto* manga (VIZ), supplemented by official English Naruto material when needed. Do not translate proper names word-for-word.

## Rules — apply before changing code or artwork

1. **Preserve established names.** Translate 螺旋丸 as **Rasengan**, not "Spiraling Sphere" or "Rotating Ball"; 写輪眼/写轮眼 as **Sharingan**, not "Copy Wheel Eye". Keep Chidori, Amaterasu, Susanoo, Tsukuyomi and similar proper names.
2. **Use the established English technique name**, not necessarily Japanese romanization everywhere: 影分身の術 / 影分身之术 → **Shadow Clone Jutsu**; 口寄せの術 → **Summoning Jutsu**. Avoid inventing "literal but plausible" English names.
3. **Identify the exact technique first.** One character can perform several similar moves. A sprite/filename such as `Naruto_label1.png`, `suiryudan`, or `skill3` does not prove its intended jutsu. Inspect the original image, character, animation and/or behavior before assigning a translation.
4. **Use manga-consistent English wording** when multiple licensed adaptations differ. Prefer VIZ's English manga name where reasonably verifiable. If sources disagree or no reliable rendering can be verified, mark the entry **NEEDS REVIEW** rather than guessing.
5. **Distinguish a character from their form.** Keep the internal hero ID/sprite key unchanged; only alter the displayed label. Do not silently normalize fan-game forms into canon forms when their meaning is unclear.
6. **Generic UI is plain English:** Start, Training, Game Modes, Character Select, Skills, Equipment, Confirm, Cancel, Loading, Results, Victory, Defeat, Exit Game. Keep labels concise enough for small screens.
7. **No romanized identifier substitutions in code paths.** Never rename C++ enums, Lua keys, texture keys, XML keys, animation files or other runtime identifiers as part of translation.
8. **Graphics follow exactly the same dictionary.** Verify original displayed wording; generate/repaint English artwork only after the term is approved. Preserve dimensions, transparencies, atlas packing, and legibility.
9. **Avoid false confidence.** The word "approved" below means the English term itself is established, **not** that a particular uninspected game sprite has been identified or translated.

## Approved Naruto-specific vocabulary

These are canonical **target terms**, not a claim that every term is present in this game.

| Source-language concept / alternate reference | Approved display wording | Category | Notes |
| --- | --- | --- | --- |
| 螺旋丸 / Rasengan | **Rasengan** | Ninjutsu | Do not literally translate as "Rotating Sphere". |
| 写輪眼 / 写轮眼 | **Sharingan** | Dōjutsu | Preserve the proper name. |
| 万華鏡写輪眼 / 万花筒写轮眼 | **Mangekyo Sharingan** | Dōjutsu | ASCII-safe UI spelling; the macronated form is *Mangekyō Sharingan*. |
| 白眼 / Byakugan | **Byakugan** | Dōjutsu | Preserve the proper name. |
| 輪廻眼 / 轮回眼 | **Rinnegan** | Dōjutsu | Preserve the proper name. |
| 千鳥 / 千鸟 | **Chidori** | Ninjutsu | Do not use "One Thousand Birds". Differentiate from Lightning Blade when context requires. |
| 雷切 / Raikiri | **Lightning Blade** | Ninjutsu | Not automatically interchangeable with *Chidori* for a given animation. |
| 影分身の術 / 影分身之术 | **Shadow Clone Jutsu** | Ninjutsu | May shorten to "Shadow Clone" where the context is a UI noun. |
| 多重影分身の術 | **Multi Shadow Clone Jutsu** | Ninjutsu | Do not conflate with the ordinary Shadow Clone Jutsu. |
| 口寄せの術 / 通灵之术 | **Summoning Jutsu** | Ninjutsu | Avoid "Psychic Technique". |
| 天照 / Amaterasu | **Amaterasu** | Ninjutsu | Preserve the proper name. |
| 月読 / 月读 | **Tsukuyomi** | Genjutsu | Preserve the proper name. |
| 須佐能乎 / 须佐能乎 | **Susanoo** | Ninjutsu | Use standard English spelling, not a literal deity paraphrase. |
| 神威 / Kamui | **Kamui** | Dōjutsu technique | Verify the effect when filenames use a non-Japanese romanization. |
| 仙人モード | **Sage Mode** | Form/state | Use "Sage Mode Naruto" only for the appropriate character variant. |
| 六道仙人モード | **Six Paths Sage Mode** | Form/state | Do not automatically apply to every variant with "Rikudo" in its internal name. |
| 火影 | **Hokage** | Title | Keep as a franchise title rather than translating to "Fire Shadow". |
| 暁 / 晓 | **Akatsuki** | Organization | Preserve the established name. |
| 人柱力 | **Jinchuriki** | World terminology | Plain UI spelling; macron optional only when fonts support it. |
| 九尾 | **Nine-Tails** | Tailed beast | Prefer the term appropriate to the actual speaker/context; use "Kurama" when that is the intended name. |

## Generic interface vocabulary

| Context | Target English |
| --- | --- |
| 训练 / training | Training |
| 开始 / start | Start |
| 选择角色 | Character Select |
| 游戏模式 | Game Modes |
| 技能 | Skills |
| 装备 | Equipment |
| 确认 | Confirm |
| 取消 | Cancel |
| 返回 | Back |
| 加载中 | Loading |
| 胜利 | Victory |
| 失败 (battle result) | Defeat |
| 操作失败 (operation status) | Operation failed |
| 即将开放 | Coming soon |
| 开发中 | In development |
| 退出 | Exit Game |

*Context matters:* 失败 in battle is "Defeat", while 操作失败 as a status is "Operation failed"; do not globally replace Chinese characters without identifying their usage.

## Game-specific names to review before normalizing

| Internal identifier / current label | Current proposal | Status | Required check |
| --- | --- | --- | --- |
| `RockLee` | Rock Lee | Approved | Standard character name. |
| `SageNaruto` / "Sage Naruto" | Sage Mode Naruto | **NEEDS REVIEW** | Confirm the specific form represented in the game's portrait and skills. |
| `RikudoNaruto`, `NarutoRikudo` / "Six Paths Naruto" | Six Paths Naruto; more specific only if proven | **NEEDS REVIEW** | Verify which of the Six Paths forms the variant represents. |
| `SageJiraiya` | Sage Mode Jiraiya | **NEEDS REVIEW** | Confirm displayed form. |
| `ImmortalSasuke` | No canonical label assigned yet | **NEEDS REVIEW** | Game-specific nickname; inspect portrait/abilities and original graphic before changing. |
| `HokageMinato` | Hokage Minato | Approved as descriptive title | Keep internal ID unchanged. |
| `Naruto_label1.png` and other `Record2` skill frames | Unknown until inspected | **NEEDS REVIEW** | Inspect full sprite/animation; do not infer names from indices. |
| `GameMode/*.png`, `Menu.png`, `Select.png` text frames | Unknown until inspected | **NEEDS REVIEW** | Read the actual graphic before replacement. |

> Some early English character labels were already committed in `lua/ui/SelectLayer.lua`. They are **provisional** until these game-specific checks and runtime layout verification are complete.

## Translation manifest process

For each discovered worded sprite or source string, record:

- Exact source path, frame key / source-code line, and original visible text.
- Character and skill/animation context, where applicable.
- Approved English term from this document (or a new review entry).
- Evidence used to identify the term: image, in-game behavior, official English manga/name reference.
- Review state: `unreviewed` → `identified` → `terminology-approved` → `art-generated` → `visually-verified` → `runtime-verified`.
- English glyph fit, texture atlas alignment, and screenshot proof at the game’s native resolution.

A visually appealing generated image with unverified spelling **must not** be committed as the final localization. Prefer programmatic text rendering for simple UI labels and image editing for art where typographic treatment is integral.

## Reference hierarchy and evidence

1. VIZ official English *Naruto* manga: https://www.viz.com/naruto
2. Official *Naruto* site English articles/database: https://naruto-official.com/en/
3. Official localization for related Naruto games, if the technique/name is not clarified by the manga; record the game/edition.
4. Fan wikis/transliteration resources only for discovery, **not** sole authority on ambiguous official renderings.

Examples of official English usage:
- VIZ uses "Multi Shadow Clone Jutsu": https://www.viz.com/press-releases/v/1006772
- Official Naruto site uses "Shadow Clone Jutsu", "Chidori", "Rasengan", and "Sharingan": https://naruto-official.com/en/news/01_1429
- Official Naruto site distinguishes "Chidori" from "Lightning Blade": https://naruto-official.com/en/news/01_2453
- Official Naruto site uses "Wind Style: Rasen Shuriken" rather than a literal paraphrase: https://naruto-official.com/en/news/01_1521

**Policy for unresolved names:** Keep existing game code identifiers and leave the visible asset unchanged or clearly provisional until a reliable identification is possible. Never invent a canonical English name from the file's machine identifier.
