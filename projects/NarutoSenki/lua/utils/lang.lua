--
-- Language (English / Chinese)
--
-- Mirrors Classes/Utils/Lang.hpp. English versions of the text baked into the
-- sprite sheets live in Resources/Lang/en/<Atlas>.plist with the same frame
-- names; in English mode we load them over the originals right after the
-- original atlas is loaded (see tools.addSprites).
--
lang = {}

local KEY = 'language'
local fileUtils = CCFileUtils:sharedFileUtils()
local frameCache = CCSpriteFrameCache:sharedSpriteFrameCache()

function lang.current()
    local saved = CCUserDefault:sharedUserDefault():getStringForKey(KEY)
    if saved == 'en' or saved == 'zh' then return saved end
    local sys = CCApplication:sharedApplication():getCurrentLanguage()
    if sys == kLanguageChinese then return 'zh' end
    return 'en'
end

function lang.isEnglish() return lang.current() == 'en' end

-- Pick the string for the active language.
function lang.tr(en, zh)
    if lang.isEnglish() then return en end
    return zh
end

local function overridePath(plist) return 'Lang/en/' .. plist end

-- CCFileUtils:isFileExist isn't bound to Lua; fullPathForFilename returns the
-- name unchanged when nothing is found on the search paths, so compare.
local overrideCache = {}
local function hasOverride(plist)
    local cached = overrideCache[plist]
    if cached ~= nil then return cached end
    local rel = overridePath(plist)
    local found = fileUtils:fullPathForFilename(rel) ~= rel
    overrideCache[plist] = found
    return found
end

function lang.applyOverride(plist)
    if not lang.isEnglish() or not hasOverride(plist) then return end
    local en = overridePath(plist)
    frameCache:removeSpriteFramesFromFile(en)
    frameCache:addSpriteFramesWithFile(en)
end

function lang.removeOverride(plist)
    if hasOverride(plist) then
        frameCache:removeSpriteFramesFromFile(overridePath(plist))
    end
end
