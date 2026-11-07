#pragma once
//
// Lang: English / Chinese localization helpers.
//
// The game bakes most of its text into sprite sheets. English versions of those
// frames live in Resources/Lang/en/<Atlas>.plist (built by tools/i18n/build_en_atlases.py)
// and use the same frame names, so when English is active we simply load them
// over the original frames. Everything that does createWithSpriteFrameName(...)
// then shows English art without further changes.
//
// The choice is stored in UserDefault under "language" ("en" or "zh"). When it is
// unset we follow the device language: Chinese devices get Chinese, everything else English.
// The Lua side (lua/utils/lang.lua) reads and writes the same key.
//
#include "cocos2d.h"
#include <string>

namespace Lang
{
static const char *kKey = "language";
static const char *kEnglish = "en";
static const char *kChinese = "zh";

// Atlases that have English overrides, each with one of its frames. A frame
// still being in the cache tells us the atlas is resident, so a language switch
// only reloads what is actually loaded (the full set is ~50 MiB of textures).
struct OverriddenAtlas
{
	const char *plist;
	const char *probeFrame;
};
static const OverriddenAtlas kOverriddenAtlases[] = {
	{"Menu.plist", "menu02_text.png"},
	{"Result.plist", "surrender_tips.png"},
	{"Select.plist", "tip1.png"},
	{"Gears.plist", "gearDetail_00.png"},
	{"Record.plist", "change_btn.png"},
	{"Record2.plist", "Asuma_label1.png"},
	{"Ougis.plist", "gameStart_001.png"},
};

static inline std::string current()
{
	auto saved = cocos2d::CCUserDefault::sharedUserDefault()->getStringForKey(kKey);
	if (saved == kEnglish || saved == kChinese)
		return saved;
	auto sys = cocos2d::CCApplication::sharedApplication()->getCurrentLanguage();
	return sys == cocos2d::kLanguageChinese ? kChinese : kEnglish;
}

static inline bool isEnglish() { return current() == kEnglish; }
static inline bool isChinese() { return !isEnglish(); }

// Pick the string for the active language.
static inline const char *tr(const char *en, const char *zh) { return isEnglish() ? en : zh; }

// Config/strings.xml holds the Chinese strings; Config/strings_en.xml the English ones.
static inline const char *stringsFile() { return isEnglish() ? "Config/strings_en.xml" : "Config/strings.xml"; }

// Look up a key in the active strings file (falls back to the key itself).
static inline std::string str(const char *key)
{
	auto dict = cocos2d::CCDictionary::createWithContentsOfFile(stringsFile());
	if (dict)
	{
		auto s = dynamic_cast<cocos2d::CCString *>(dict->objectForKey(key));
		if (s)
			return s->m_sString;
	}
	return key;
}

static inline std::string overridePath(const std::string &plist) { return "Lang/en/" + plist; }

static inline bool hasOverride(const std::string &plist)
{
	auto fu = cocos2d::CCFileUtils::sharedFileUtils();
	auto full = fu->fullPathForFilename(overridePath(plist).c_str());
	return fu->isFileExist(full);
}

// Call right after loading `plist` into the frame cache.
static inline void applyOverride(const std::string &plist)
{
	if (!isEnglish() || !hasOverride(plist))
		return;
	auto cache = cocos2d::CCSpriteFrameCache::sharedSpriteFrameCache();
	auto en = overridePath(plist);
	// Drop the original frames with these names, then load the English ones.
	cache->removeSpriteFramesFromFile(en.c_str());
	cache->addSpriteFramesWithFile(en.c_str());
}

// Call when unloading `plist`, so the English copies go too.
static inline void removeOverride(const std::string &plist)
{
	if (!hasOverride(plist))
		return;
	cocos2d::CCSpriteFrameCache::sharedSpriteFrameCache()->removeSpriteFramesFromFile(overridePath(plist).c_str());
}

// Switch language. Atlases currently in the frame cache are reloaded so the
// change shows at once (callers should rebuild their scene afterwards); the
// rest are only unregistered, so their next addSprites() loads the right
// language. Nothing that isn't already loaded gets loaded here.
static inline void set(const std::string &lang)
{
	auto ud = cocos2d::CCUserDefault::sharedUserDefault();
	ud->setStringForKey(kKey, lang);
	ud->flush();

	auto cache = cocos2d::CCSpriteFrameCache::sharedSpriteFrameCache();
	for (const auto &atlas : kOverriddenAtlases)
	{
		bool resident = cache->spriteFrameByName(atlas.probeFrame) != nullptr;
		// Drop both versions of the frames and forget both plists, so
		// addSpriteFramesWithFile() won't skip them as already loaded.
		removeOverride(atlas.plist);
		cache->removeSpriteFramesFromFile(atlas.plist);
		if (resident)
		{
			cache->addSpriteFramesWithFile(atlas.plist);
			applyOverride(atlas.plist);
		}
	}
}

static inline void toggle() { set(isEnglish() ? kChinese : kEnglish); }

} // namespace Lang
