#!/usr/bin/env python3
"""
Build English override atlases for Naruto Senki.

The game bakes most of its text into sprite sheets (Record2 skill descriptions,
Select name plates, Gears item details, menu captions, ...). For the English
localization we render replacement frames with the *same frame names* and pack
them into `Resources/Lang/en/<Atlas>.plist/.png`. At runtime, when the language
is English, the game loads these on top of the original atlas (see
Classes/Utils/Lang.* and lua/utils/lang.lua), so every existing
`createWithSpriteFrameName("...")` call picks up the English art automatically.

Edit the .tsv files next to this script, then run:

    python3 tools/i18n/build_en_atlases.py

Requires: Pillow, numpy, opencv-python (only for the "BATTLE START" frames).
"""
import os
import re
import sys
import math
import plistlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RES = os.path.join(REPO, 'projects', 'NarutoSenki', 'Resources')
OUT = os.path.join(RES, 'Lang', 'en')
FONTS = os.path.join(HERE, 'fonts')

SANS = os.path.join(FONTS, 'SourceSans3-Bold.ttf')
TITLE = os.path.join(FONTS, 'Bangers-Regular.ttf')


# ---------------------------------------------------------------- helpers

def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


def parse_nums(s):
    return [int(round(float(n))) for n in re.findall(r'-?[\d.]+', s)]


def load_atlas(name):
    """Return {frame_name: (RGBA image at original orientation, meta)}."""
    d = plistlib.load(open(os.path.join(RES, name + '.plist'), 'rb'))
    tex = Image.open(os.path.join(RES, name + '.png')).convert('RGBA')
    frames = {}
    for k, f in d['frames'].items():
        if 'frame' in f:  # format 2
            x, y, w, h = parse_nums(f['frame'])
            rot = f.get('rotated', False)
            off = parse_nums(f.get('offset', '{0,0}'))
            src = parse_nums(f.get('sourceSize', '{%d,%d}' % (w, h)))
        else:  # format 3
            x, y, w, h = parse_nums(f['textureRect'])
            rot = f.get('textureRotated', False)
            off = parse_nums(f.get('spriteOffset', '{0,0}'))
            src = parse_nums(f.get('spriteSourceSize', '{%d,%d}' % (w, h)))
        if rot:
            img = tex.crop((x, y, x + h, y + w)).rotate(90, expand=True)
        else:
            img = tex.crop((x, y, x + w, y + h))
        frames[k] = (img, {'offset': off, 'source': src})
    return frames


def text_size(fnt, text):
    l, t, r, b = fnt.getbbox(text)
    return r - l, b - t, l, t


def render_text(text, fnt, fill=(255, 255, 255, 255), stroke=1,
                stroke_fill=(0, 0, 0, 255), shadow=None, height=None, pad=2,
                gradient=None):
    """Render one line of text on a transparent canvas.

    gradient: ((r,g,b),(r,g,b)) vertical gradient for the fill.
    shadow: (dx, dy, rgba) drop shadow drawn under the outline.
    """
    w, h, l, t = text_size(fnt, text)
    asc, desc = fnt.getmetrics()
    W = w + 2 * (pad + stroke) + (abs(shadow[0]) if shadow else 0)
    H = (height if height else asc + desc + 2 * stroke) + (abs(shadow[1]) if shadow and not height else 0)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = pad + stroke - l
    y = (H - (asc + desc)) // 2 if height else stroke
    d = ImageDraw.Draw(img)
    if shadow:
        sx, sy, sc = shadow
        d.text((x + sx, y + sy), text, font=fnt, fill=sc, stroke_width=stroke, stroke_fill=sc)
    if gradient:
        # outline first, then fill through a gradient mask
        d.text((x, y), text, font=fnt, fill=stroke_fill, stroke_width=stroke, stroke_fill=stroke_fill)
        mask = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mask).text((x, y), text, font=fnt, fill=255)
        top, bot = gradient
        grad = Image.new('RGBA', (W, H))
        gd = ImageDraw.Draw(grad)
        ys = [yy for yy in range(H) if mask.crop((0, yy, W, yy + 1)).getbbox()]
        y0, y1 = (ys[0], ys[-1]) if ys else (0, H - 1)
        for yy in range(H):
            k = min(1.0, max(0.0, (yy - y0) / max(1, (y1 - y0))))
            c = tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,)
            gd.line([(0, yy), (W, yy)], fill=c)
        img.paste(grad, (0, 0), mask)
    else:
        d.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return img


def wrap(text, fnt, max_w):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if text_size(fnt, t)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trim(img):
    bb = img.getbbox()
    return img.crop(bb) if bb else img


# ---------------------------------------------------------------- styles

def style_skill(orig, en):
    h = orig.height
    f = font(SANS, 13, 'Bold')
    return render_text(en, f, stroke=1, height=h, pad=1)


def style_gear(orig, en):
    title, body = en.split('|', 1)
    W = 76
    ft = font(SANS, 10, 'Bold')
    fb = font(SANS, 9, 'SemiBold')
    t = render_text(title, ft, fill=(238, 238, 170, 255), stroke=1)
    lines = [render_text(l, fb, stroke=1) for l in wrap(body, fb, W - 4)]
    H = t.height + 2 + sum(l.height - 1 for l in lines)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    img.alpha_composite(t, ((W - t.width) // 2, 0))
    y = t.height + 2
    for l in lines:
        img.alpha_composite(l, ((W - l.width) // 2, y))
        y += l.height - 1
    return img


def style_menutext(orig, en):
    f = font(SANS, 12, 'Bold')
    img = render_text(en, f, stroke=1, height=orig.height + 2)
    return img


def style_line(orig, en):
    size = 15
    while True:
        f = font(TITLE, size)
        img = render_text(en, f, stroke=1, height=orig.height)
        if img.width <= max(orig.width + 40, 180) or size <= 10:
            return img
        size -= 1


def style_smalltext(orig, en):
    f = font(SANS, 12, 'Bold')
    return render_text(en, f, stroke=1, height=orig.height)


def style_tip(orig, en):
    f = font(SANS, 14, 'Bold')
    return render_text(en, f, stroke=1, height=orig.height,
                       gradient=((248, 240, 152), (248, 136, 64)))


def style_credits(orig, en):
    W = orig.width
    f = font(SANS, 13, 'SemiBold')
    lines = [render_text(l, f, stroke=1, stroke_fill=(40, 40, 44, 255)) for l in wrap(en, f, W - 6)]
    H = sum(l.height for l in lines) + 2
    img = Image.new('RGBA', (W, max(H, orig.height)), (0, 0, 0, 0))
    y = (img.height - H) // 2
    for l in lines:
        img.alpha_composite(l, (2, y))
        y += l.height
    return img


def style_awaken(orig, en):
    f = font(TITLE, 17)
    return render_text(en, f, stroke=1, stroke_fill=(20, 30, 60, 255), height=orig.height,
                       gradient=((107, 222, 247), (54, 78, 139)))


def style_plate(orig, en):
    big, small = (en.split('|') + [''])[:2]
    W = max(orig.width, 120)
    size = 40
    while True:
        fb = font(TITLE, size)
        b = render_text(big, fb, stroke=2, stroke_fill=(45, 25, 15, 255),
                        gradient=((216, 181, 115), (200, 120, 80)))
        if b.width <= 200 or size <= 20:
            break
        size -= 2
    parts = [b]
    if small:
        fs = font(TITLE, 15)
        parts.append(render_text(small, fs, stroke=1, stroke_fill=(20, 20, 20, 255)))
    parts = [trim(p) for p in parts]
    W = max(p.width for p in parts) + 4
    H = sum(p.height for p in parts) + 2 * (len(parts) - 1) + 4
    img = Image.new('RGBA', (W, max(H, orig.height)), (0, 0, 0, 0))
    y = (img.height - H) // 2 + 2
    for p in parts:
        img.alpha_composite(p, ((W - p.width) // 2, y))
        y += p.height + 2
    return img


STYLES = {
    'skill': style_skill, 'gear': style_gear, 'menutext': style_menutext,
    'line': style_line, 'smalltext': style_smalltext, 'tip': style_tip,
    'credits': style_credits, 'awaken': style_awaken, 'plate': style_plate,
}


# ------------------------------------------------- "BATTLE START" animation

def battle_start_frames(atlas_frames, en):
    """Erase the 戰鬥開始 lettering from gameStart_00N and draw English text
    with the same placement/rotation. Frames are rebuilt on their full
    source canvas so the text may extend past the original trim box."""
    import numpy as np
    import cv2
    out = {}
    names = sorted(k for k in atlas_frames if k.startswith('gameStart_00'))
    # fixed text style, sized to the final frame's lettering
    for k in names:
        img, meta = atlas_frames[k]
        sw, sh = meta['source']
        ox, oy = meta['offset']
        canvas = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
        # cocos offset: center of trimmed rect relative to center of source, y up
        px = int(round((sw - img.width) / 2 + ox))
        py = int(round((sh - img.height) / 2 - oy))
        canvas.alpha_composite(img, (px, py))
        a = np.array(canvas)
        rgb = a[:, :, :3].astype(int)
        alpha = a[:, :, 3]
        light = ((rgb.min(axis=2) > 150) & (alpha > 80)).astype(np.uint8)
        if light.sum() < 30:
            out[k] = (canvas, None)
            continue
        # text area = light outline, closed and dilated so it covers the black glyph bodies
        k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        area = cv2.morphologyEx(light, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        area = cv2.dilate(area, k5, iterations=2)
        # fill holes inside glyphs
        cnts, _ = cv2.findContours(area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(area)
        cv2.drawContours(filled, cnts, -1, 1, thickness=-1)
        # inpaint the alpha (brush coverage) and colour from outside the text area
        inp_a = cv2.inpaint(alpha, filled * 255, 7, cv2.INPAINT_TELEA)
        inp_c = cv2.inpaint(a[:, :, :3].copy(), filled * 255, 7, cv2.INPAINT_TELEA)
        # the brush is black ink: keep colour dark where we re-filled
        inp_c[filled > 0] = np.minimum(inp_c[filled > 0], 30)
        a2 = a.copy()
        a2[:, :, 3] = np.where(filled > 0, inp_a, alpha)
        a2[:, :, :3] = np.where(filled[..., None] > 0, inp_c, a[:, :, :3])
        canvas = Image.fromarray(a2, 'RGBA')
        # orientation of the lettering from the light pixels
        ys, xs = np.nonzero(light)
        pts = np.column_stack([xs, ys]).astype(np.float32)
        (cx, cy), (rw, rh), ang = cv2.minAreaRect(pts)
        if rw < rh:
            rw, rh = rh, rw
            ang += 90
        if ang > 45:
            ang -= 180
        if ang < -45:
            ang += 180
        out[k] = (canvas, (cx, cy, rw, rh, ang, xs.min(), xs.max()))
    # use the last frame's lettering size as the reference text size
    ref = out[names[-1]][1]
    tw = ref[2]
    th = ref[3]
    size = 60
    while size > 10:
        f = font(TITLE, size)
        t = render_text(en, f, fill=(15, 15, 15, 255), stroke=2, stroke_fill=(245, 245, 245, 255))
        if t.width <= tw * 1.05 and t.height <= th * 1.6:
            break
        size -= 1
    text_img = trim(t)
    res = {}
    for k in names:
        canvas, info = out[k]
        if info is not None:
            cx, cy, rw, rh, ang, xmin, xmax = info
            rot = text_img.rotate(-ang, expand=True, resample=Image.BICUBIC)
            if xmin <= 1 and rw < tw * 0.9:
                # lettering still sliding in from the left edge: align right ends
                full_cx = cx + (tw - rw) / 2 * math.cos(math.radians(ang)) * -1
                full_cy = cy + (tw - rw) / 2 * math.sin(math.radians(ang)) * -1
                cx, cy = full_cx, full_cy
            layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
            layer.paste(rot, (int(round(cx - rot.width / 2)), int(round(cy - rot.height / 2))), rot)
            canvas = Image.alpha_composite(canvas, layer)
        res[k] = canvas
    return res


# ---------------------------------------------------------------- packing

def pack(frames, max_w=2048):
    """Simple shelf packer. frames: {name: RGBA}. Returns (texture, rects)."""
    items = sorted(frames.items(), key=lambda kv: (-kv[1].height, kv[0]))
    width = 256
    total = sum((im.width + 2) * (im.height + 2) for _, im in items)
    widest = max(im.width for _, im in items) + 2
    while width < max_w and (width * width < total * 1.15 or width < widest):
        width *= 2
    x = y = shelf = 0
    rects = {}
    for name, im in items:
        if x + im.width + 2 > width:
            x = 0
            y += shelf
            shelf = 0
        rects[name] = (x + 1, y + 1, im.width, im.height)
        x += im.width + 2
        shelf = max(shelf, im.height + 2)
    height = y + shelf
    # NPOT is fine here: the original atlases are NPOT too (e.g. Select 2027x961)
    tex = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for name, im in items:
        rx, ry, _, _ = rects[name]
        tex.paste(im, (rx, ry))
    return tex, rects


def write_atlas(name, frames):
    os.makedirs(OUT, exist_ok=True)
    tex, rects = pack(frames)
    png = name + '.png'
    tex.save(os.path.join(OUT, png), optimize=True)
    fr = {}
    for k, (x, y, w, h) in sorted(rects.items()):
        fr[k] = {
            'frame': '{{%d,%d},{%d,%d}}' % (x, y, w, h),
            'offset': '{0,0}',
            'rotated': False,
            'sourceColorRect': '{{0,0},{%d,%d}}' % (w, h),
            'sourceSize': '{%d,%d}' % (w, h),
        }
    d = {'frames': fr, 'metadata': {
        'format': 2, 'realTextureFileName': png, 'textureFileName': png,
        'size': '{%d,%d}' % tex.size}}
    with open(os.path.join(OUT, name + '.plist'), 'wb') as f:
        plistlib.dump(d, f, sort_keys=True)
    print('  %-10s %3d frames -> %s (%dx%d)' % (name, len(frames), os.path.relpath(os.path.join(OUT, png), RES), tex.width, tex.height))


# ------------------------------------------------- language toggle button

def find_cjk_font():
    """The toggle shows "中文", which needs a CJK font. Only used when
    (re)building the button; the generated PNG is committed."""
    import subprocess
    cands = [os.environ.get('CJK_FONT', '')]
    for q in ('IPAGothic', 'Noto Sans CJK SC', 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC'):
        try:
            cands.append(subprocess.check_output(['fc-match', '-f', '%{file}', q], text=True))
        except Exception:
            pass
    for c in cands:
        if not c or not os.path.exists(c):
            continue
        try:
            f = ImageFont.truetype(c, 12)
            if f.getbbox('中文')[2] > 12 and f.getmask('中').getbbox():
                return c
        except Exception:
            pass
    return None


def build_lang_button():
    cjk = find_cjk_font()
    if not cjk:
        print('  ! no CJK font found (set CJK_FONT=/path/to/font); keeping existing LangButton')
        return
    W, H = 62, 17
    fe = font(TITLE, 14)
    fz = ImageFont.truetype(cjk, 11)
    frames = {}
    for active in ('en', 'zh'):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, W - 1, H - 1), radius=7, fill=(20, 20, 24, 200), outline=(216, 181, 115, 255))
        on, off = (255, 222, 120, 255), (150, 150, 150, 255)
        en = render_text('EN', fe, fill=on if active == 'en' else off, stroke=1, height=H)
        zh = render_text('中文', fz, fill=on if active == 'zh' else off, stroke=1, height=H)
        img.alpha_composite(en, (W // 4 - en.width // 2 + 1, 0))
        img.alpha_composite(zh, (3 * W // 4 - zh.width // 2, 0))
        d.line((W // 2, 4, W // 2, H - 5), fill=(216, 181, 115, 200))
        frames['lang_btn_%s.png' % active] = img
    global OUT
    out, OUT = OUT, os.path.join(RES, 'Lang')
    write_atlas('LangButton', frames)
    OUT = out


# ---------------------------------------------------------------- main

def read_tsv(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'):
            continue
        rows.append(line.split('\t'))
    return rows


def main():
    jobs = {}  # atlas -> list of (frame, style, en)
    for frame, zh, en in read_tsv(os.path.join(HERE, 'skills.tsv')):
        jobs.setdefault('Record2', []).append((frame + '.png', 'skill', en))
    for atlas, frame, style, zh, en in read_tsv(os.path.join(HERE, 'ui.tsv')):
        jobs.setdefault(atlas, []).append((frame, style, en))

    print('Building English override atlases into', os.path.relpath(OUT, REPO))
    for atlas, items in sorted(jobs.items()):
        src = load_atlas(atlas)
        frames = {}
        for frame, style, en in items:
            if style == 'gamestart':
                frames.update(battle_start_frames(src, en))
                continue
            if frame not in src:
                print('  ! %s: frame %s not found, skipped' % (atlas, frame))
                continue
            frames[frame] = STYLES[style](src[frame][0], en)
        write_atlas(atlas, frames)
    build_lang_button()


if __name__ == '__main__':
    main()
