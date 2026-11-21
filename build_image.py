#!/usr/bin/env python3
"""Render entry.png — an open passport spread of the Republic of Tidemark.

All text is drawn with real fonts (DejaVu family) via PIL. No model draws
any lettering. The render is fully deterministic: two runs are byte-identical.

Country design (kept plausible, not whimsical):
  REPUBLIC OF TIDEMAR — a small tidal-island republic.
  Capital LOWATER. Language: English with a Tidemaric second column
  (invented but internally consistent field labels).
  Holder: MARIS VELL, born 12 JUN 1988 in LOWATER.
  Passport TDM048271, issued 14 MAR 2021 at LOWATER, expires 14 MAR 2031.
  Travel: Ostrevia (2022, 2025) and the Keldan Union (2023) — every stamp
  falls strictly between issue and expiry, in chronological order.
  Telling detail: the Keldan admission stamp carries the condition
  "MUST DEPART BEFORE THE TIDE".
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 768
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = f"{FD}/DejaVuSerif.ttf"
SERIF_B = f"{FD}/DejaVuSerif-Bold.ttf"
SANS = f"{FD}/DejaVuSans.ttf"
SANS_B = f"{FD}/DejaVuSans-Bold.ttf"
MONO = f"{FD}/DejaVuSansMono.ttf"
MONO_B = f"{FD}/DejaVuSansMono-Bold.ttf"

# Palette — restrained navy / burgundy on warm paper.
PAPER = (246, 240, 224)
PAPER_EDGE = (238, 229, 205)
NAVY = (27, 42, 74)
NAVY_SOFT = (52, 68, 102)
BURGUNDY = (107, 31, 42)
INK = (38, 36, 32)
GREY = (110, 104, 92)
RULE = (150, 140, 118)
BLUE_INK = (43, 74, 138)
RED_INK = (150, 44, 52)
GUIL = (196, 200, 178)


def F(path, size):
    return ImageFont.truetype(path, size)


def centred(draw, cx, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return w


# ---------------------------------------------------------------- MRZ helpers
def _mrz_val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 .. Z=35


def mrz_check(data):
    weights = (7, 3, 1)
    total = sum(_mrz_val(c) * weights[i % 3] for i, c in enumerate(data))
    return str(total % 10)


def build_mrz():
    line1 = "P<TDM" + "VELL<<MARIS"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "TDM048271"
    dob, exp = "880612", "310314"
    personal = "<" * 14
    body = (
        doc + mrz_check(doc)
        + "TDM"
        + dob + mrz_check(dob)
        + "F"
        + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    composite_src = body[0:10] + body[13:20] + body[21:43]
    line2 = body + mrz_check(composite_src)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ------------------------------------------------------------------- portrait
def draw_portrait(base, box):
    """Duotone engraved-style portrait, drawn only with PIL shapes/patterns."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    tile = Image.new("RGB", (w, h), (233, 226, 205))
    d = ImageDraw.Draw(tile)
    # fine horizontal engraving lines over the whole photo ground
    for yy in range(0, h, 4):
        d.line([(0, yy), (w, yy)], fill=(214, 205, 178), width=1)
    cx = w // 2
    skin = (206, 178, 138)
    skin_sh = (172, 140, 98)
    hair = (74, 58, 44)
    jacket = (38, 52, 84)
    # shoulders / jacket
    d.polygon([(cx - 52, h), (cx - 40, h - 52), (cx - 14, h - 66),
               (cx + 14, h - 66), (cx + 40, h - 52), (cx + 52, h)],
              fill=jacket)
    # shirt V and collar
    d.polygon([(cx - 13, h - 64), (cx + 13, h - 64), (cx, h - 30)], fill=(240, 236, 224))
    d.polygon([(cx - 13, h - 64), (cx, h - 44), (cx - 20, h - 58)], fill=(226, 220, 200))
    d.polygon([(cx + 13, h - 64), (cx, h - 44), (cx + 20, h - 58)], fill=(226, 220, 200))
    # neck
    d.rectangle([cx - 10, h - 84, cx + 10, h - 60], fill=skin_sh)
    # head
    d.ellipse([cx - 30, 26, cx + 30, 108], fill=skin)
    # jaw shading (engraved arcs on the right side)
    for r in range(6, 26, 5):
        d.arc([cx - 30 + r // 2, 30 + r // 3, cx + 30, 108], start=300, end=60,
              fill=skin_sh, width=1)
    # hair — side-parted, swept, following the skull rather than a cap
    d.pieslice([cx - 31, 13, cx + 31, 76], start=180, end=360, fill=hair)
    d.pieslice([cx - 31, 22, cx + 20, 64], start=185, end=345, fill=hair)
    d.polygon([(cx - 31, 44), (cx - 31, 30), (cx - 12, 40), (cx - 20, 52)],
              fill=skin)  # forehead opening at the parting side
    for i in range(6):  # hair strand lines, combed diagonally
        d.line([(cx - 24 + i * 4, 30 - i), (cx + 6 + i * 3, 20 + i * 2)],
               fill=(98, 80, 60), width=1)
    d.line([(cx - 13, 26), (cx - 11, 44)], fill=(98, 80, 60), width=1)
    # ears
    d.ellipse([cx - 34, 62, cx - 27, 80], fill=skin)
    d.ellipse([cx + 27, 62, cx + 34, 80], fill=skin)
    # brows, eyes, nose, mouth — quiet, dignified, front-facing
    d.line([(cx - 19, 62), (cx - 6, 60)], fill=hair, width=3)
    d.line([(cx + 6, 60), (cx + 19, 62)], fill=hair, width=3)
    d.ellipse([cx - 16, 68, cx - 9, 73], fill=(40, 34, 28))
    d.ellipse([cx + 9, 68, cx + 16, 73], fill=(40, 34, 28))
    d.line([(cx, 72), (cx - 3, 86), (cx + 3, 88)], fill=skin_sh, width=2)
    d.line([(cx - 10, 96), (cx + 10, 96)], fill=(146, 92, 84), width=3)
    d.line([(cx - 9, 100), (cx + 9, 100)], fill=skin_sh, width=1)
    # engraving hatch clipped to the jacket's trapezoid (narrows upward)
    for yy in range(h - 62, h, 5):
        frac = (yy - (h - 66)) / 66.0
        half = 14 + frac * 38
        d.line([(cx - half, yy), (cx + half, yy)], fill=(56, 72, 108), width=1)
    base.paste(tile, (x0, y0))
    # guilloche-ish frame: double border + corner ticks + wavy inner line
    d2 = ImageDraw.Draw(base)
    d2.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], outline=NAVY, width=2)
    d2.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=BURGUNDY, width=1)
    pts = []
    for xx in range(x0 - 3, x1 + 4, 4):
        pts.append((xx, y0 - 3 + 2 * math.sin(xx / 9.0)))
    d2.line(pts, fill=NAVY_SOFT, width=1)
    pts = []
    for xx in range(x0 - 3, x1 + 4, 4):
        pts.append((xx, y1 + 3 + 2 * math.sin(xx / 9.0)))
    d2.line(pts, fill=NAVY_SOFT, width=1)


# --------------------------------------------------------------------- stamps
def make_stamp(w, h, shape, colour, lines, fonts):
    """One faded-ink stamp on its own transparent tile (unrotated)."""
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    c = colour + (205,)
    if shape == "circle":
        d.ellipse([3, 3, w - 4, h - 4], outline=c, width=3)
        d.ellipse([10, 10, w - 11, h - 11], outline=c, width=1)
    else:
        d.rounded_rectangle([3, 3, w - 4, h - 4], radius=10, outline=c, width=3)
        d.rounded_rectangle([9, 9, w - 10, h - 10], radius=7, outline=c, width=1)
    total = sum(f.size + 5 for _, f in zip(lines, fonts))
    y = (h - total) / 2 + 2
    for text, fnt in zip(lines, fonts):
        tw = d.textlength(text, font=fnt)
        d.text(((w - tw) / 2, y), text, font=fnt, fill=colour + (225,))
        y += fnt.size + 5
    # ink wear: knock out a sparse deterministic speckle
    px = tile.load()
    for yy in range(h):
        for xx in range(w):
            if (xx * 7 + yy * 13) % 29 == 0 and px[xx, yy][3] > 0:
                px[xx, yy] = (0, 0, 0, 0)
    return tile


def paste_stamp(base, tile, cx, cy, angle):
    rot = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


# ----------------------------------------------------------------------- main
def main():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- paper: subtle guilloche curves across the whole spread.
    # Kept faint and fine — a security texture, never a squared grid.
    for k in range(34):
        pts = []
        for xx in range(0, W + 1, 8):
            yy = 26 + k * 22 + 7 * math.sin(xx / 150.0 + k * 0.85)
            pts.append((xx, yy))
        d.line(pts, fill=GUIL + (27,), width=1)
    for k in range(22):
        pts = []
        for yy in range(0, H + 1, 8):
            xx = 40 + k * 47 + 6 * math.sin(yy / 130.0 + k * 1.1)
            pts.append((xx, yy))
        d.line(pts, fill=GUIL + (11,), width=1)
    # page tint: right page a touch cooler
    d.rectangle([512, 0, W, H], fill=(238, 234, 214, 90))
    # outer edge shading — a whisper, not a frame
    for i in range(6):
        a = 15 - i * 2
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(120, 110, 88, a), width=1)

    # per-page inner rules
    d.rectangle([18, 18, 494, H - 19], outline=NAVY + (150,), width=1)
    d.rectangle([530, 18, W - 19, H - 19], outline=NAVY + (150,), width=1)

    # centre seam shadow
    for i in range(22):
        a = int(95 * (1 - i / 22))
        d.line([(512 - i, 0), (512 - i, H)], fill=(96, 86, 64, a))
        d.line([(512 + i, 0), (512 + i, H)], fill=(96, 86, 64, a))
    d.line([(512, 0), (512, H)], fill=(90, 80, 58, 160), width=1)

    # perforated passport number along the top of both pages
    f_perf = F(MONO, 11)
    for x0 in (44, 556):
        txt = "TDM048271"
        for i, ch in enumerate(txt):
            d.text((x0 + i * 13, 26), ch, font=f_perf, fill=(120, 112, 94))

    # ============================================================ LEFT PAGE
    LC = 256  # left page centre x
    # emblem: shield with three tide-waves and a beacon dot
    ex, ey = LC, 66
    d.ellipse([ex - 21, ey - 21, ex + 21, ey + 21], outline=NAVY, width=2)
    d.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], outline=BURGUNDY, width=1)
    for j, wy in enumerate((ey - 4, ey + 3, ey + 10)):
        pts = [(ex - 11 + t, wy + 2.4 * math.sin(t / 4.2 + j)) for t in range(23)]
        d.line(pts, fill=NAVY, width=2)
    d.ellipse([ex - 3, ey - 14, ex + 3, ey - 8], fill=BURGUNDY)

    centred(d, LC, 94, "REPUBLIC OF TIDEMAR", F(SERIF_B, 23), NAVY)
    centred(d, LC, 122, "RESPUBLIK  ·  TIDEMAR", F(SERIF, 12), BURGUNDY)
    d.line([(52, 146), (460, 146)], fill=NAVY, width=2)
    d.line([(52, 150), (460, 150)], fill=BURGUNDY, width=1)
    centred(d, LC, 158, "PASSPORT", F(SERIF_B, 19), NAVY)
    centred(d, LC, 184, "PASPORT", F(SERIF, 11), GREY)

    # portrait
    draw_portrait(img, (44, 224, 186, 414))
    d = ImageDraw.Draw(img, "RGBA")
    centred(d, 115, 424, "MARIS VELL", F(SANS_B, 10), NAVY)

    # ---- data fields. One label style, one value style, shared left edge.
    f_lab = F(SANS, 9)
    f_val = F(SANS_B, 14)
    f_val_s = F(SANS_B, 12)

    def field(x, y, label_en, label_td, value, vfont=None, w_rule=250):
        d.text((x, y), label_en, font=f_lab, fill=GREY)
        lw = d.textlength(label_en, font=f_lab)
        d.text((x + lw + 6, y + 1), "/ " + label_td, font=F(SANS, 8), fill=(150, 142, 124))
        d.text((x, y + 13), value, font=vfont or f_val, fill=INK)
        d.line([(x, y + 36), (x + w_rule, y + 36)], fill=RULE + (160,), width=1)

    FX = 206  # fields column beside the portrait
    field(FX, 218, "TYPE", "TIP", "P", w_rule=56)
    field(FX + 72, 218, "CODE", "KOD", "TDM", w_rule=64)
    field(FX + 152, 218, "PASSPORT No.", "PAS", "TDM048271", f_val_s, w_rule=124)
    field(FX, 268, "SURNAME", "NAM FAMIL", "VELL", w_rule=276)
    field(FX, 318, "GIVEN NAMES", "NAM GIV", "MARIS", w_rule=276)
    field(FX, 368, "NATIONALITY", "NASIONALITET", "TIDEMARIC", w_rule=276)

    FY = 452  # full-width rows under the portrait
    field(44, FY, "DATE OF BIRTH", "DAT NAIS", "12 JUN 1988", w_rule=200)
    field(268, FY, "SEX", "SEK", "F", w_rule=60)
    field(352, FY, "PLACE OF BIRTH", "PLAS NAIS", "LOWATER", f_val_s, w_rule=130)
    field(44, FY + 50, "DATE OF ISSUE", "DAT EMIS", "14 MAR 2021", w_rule=200)
    field(268, FY + 50, "DATE OF EXPIRY", "DAT EXPIR", "14 MAR 2031", w_rule=214)
    field(44, FY + 100, "PLACE OF ISSUE", "PLAS EMIS", "LOWATER", w_rule=200)

    # holder's signature — smooth Catmull-Rom strokes through hand-set
    # control points: loops and swells like a real pen flourish.
    sx, sy = 268, FY + 100
    d.text((sx, sy), "SIGNATURE OF HOLDER / SIGNATUR", font=f_lab, fill=GREY)

    def smooth(pts, steps=9):
        ext = [pts[0]] + pts + [pts[-1]]
        out = []
        for i in range(len(ext) - 3):
            p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
            for s in range(steps):
                t = s / steps
                t2, t3 = t * t, t * t * t
                out.append((
                    0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                           + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                           + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                    0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                           + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                           + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3),
                ))
        out.append(pts[-1])
        return [(sx + px, sy + py) for px, py in out]

    strokes = [
        [(2, 28), (10, 12), (18, 24), (24, 30), (34, 16), (44, 27), (52, 29)],
        [(50, 22), (66, 13), (84, 25), (100, 18), (118, 28), (136, 21), (152, 27)],
        [(146, 29), (168, 20), (190, 27), (208, 23)],
        [(36, 34), (92, 30), (150, 34), (204, 31)],  # underline sweep
    ]
    for st in strokes:
        d.line(smooth(st), fill=(30, 30, 60, 220), width=2)
    d.line([(sx, sy + 36), (sx + 214, sy + 36)], fill=RULE + (160,), width=1)

    d.text((44, 640), "This passport contains 32 pages  ·  Pas isi 32 blad",
           font=F(SANS, 9), fill=GREY)

    # ---- machine-readable zone
    d.rectangle([30, 656, 482, 732], fill=(252, 249, 240), outline=RULE, width=1)
    f_mrz = F(MONO_B, 15)
    line1, line2 = build_mrz()
    for i, line in enumerate((line1, line2)):
        tw = d.textlength(line, font=f_mrz)
        d.text(((256 - tw / 2), 670 + i * 30), line, font=f_mrz, fill=(30, 30, 30))

    # =========================================================== RIGHT PAGE
    RC = 768
    centred(d, RC, 40, "VISAS", F(SERIF_B, 19), NAVY)
    centred(d, RC, 68, "VISA  ·  STEMPLAR", F(SERIF, 11), GREY)
    d.line([(556, 92), (980, 92)], fill=NAVY, width=2)
    d.line([(556, 96), (980, 96)], fill=BURGUNDY, width=1)
    d.text((556, 106), "Endorsements and stamps of foreign authorities",
           font=F(SANS, 9), fill=GREY)
    d.text((556, 120), "Noteringar av framande autoritetar",
           font=F(SANS, 9), fill=(150, 142, 124))

    f_st1 = F(SANS_B, 13)
    f_st2 = F(SANS_B, 11)
    f_st3 = F(SANS, 10)

    s = make_stamp(238, 92, "rect", BLUE_INK,
                   ["OSTREVIA", "ADMITTED · KELVAR PORT", "03 MAY 2022"],
                   [f_st1, f_st3, f_st2])
    paste_stamp(img, s, 660, 190, -6)
    s = make_stamp(238, 92, "rect", BLUE_INK,
                   ["OSTREVIA", "DEPARTED · KELVAR PORT", "17 MAY 2022"],
                   [f_st1, f_st3, f_st2])
    paste_stamp(img, s, 878, 178, 4)
    s = make_stamp(196, 196, "circle", RED_INK,
                   ["KELDAN UNION", "ENTERED", "BRACKENHOLT", "09 SEP 2023"],
                   [f_st2, f_st1, f_st3, f_st2])
    paste_stamp(img, s, 668, 372, 9)
    s = make_stamp(196, 196, "circle", RED_INK,
                   ["KELDAN UNION", "DEPARTED", "BRACKENHOLT", "28 SEP 2023"],
                   [f_st2, f_st1, f_st3, f_st2])
    paste_stamp(img, s, 884, 384, -11)
    s = make_stamp(238, 92, "rect", BLUE_INK,
                   ["OSTREVIA", "ADMITTED · KELVAR PORT", "22 JAN 2025"],
                   [f_st1, f_st3, f_st2])
    paste_stamp(img, s, 664, 540, 3)
    s = make_stamp(238, 92, "rect", BLUE_INK,
                   ["OSTREVIA", "DEPARTED · KELVAR PORT", "02 FEB 2025"],
                   [f_st1, f_st3, f_st2])
    paste_stamp(img, s, 884, 556, -4)

    # ---- THE telling detail: the tide condition, a visa-condition stamp
    # in burgundy, placed as the Keldan officer's condition of admission.
    d = ImageDraw.Draw(img, "RGBA")
    tide = make_stamp(430, 96, "rect", BURGUNDY,
                      ["KELDAN UNION — CONDITION OF ADMISSION",
                       "MUST DEPART BEFORE THE TIDE"],
                      [F(SANS_B, 12), F(SANS_B, 15)])
    paste_stamp(img, tide, RC, 668, -2)

    d = ImageDraw.Draw(img, "RGBA")
    d.text((936, 738), "7", font=F(SERIF, 11), fill=GREY)
    d.text((44, 738), "6", font=F(SERIF, 11), fill=GREY)

    img.convert("RGB").save(OUT, optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
