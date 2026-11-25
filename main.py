#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Writes a single 1024x1024 PNG invitation letter to /output/entry.png
(falls back to ./entry.png when /output is not writable, e.g. local runs).

Everything is drawn with Pillow and the system DejaVu / Liberation fonts;
no network, no randomness, no timestamps: re-running produces byte-identical
output.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT_PRIMARY = "/output/entry.png"
OUT_FALLBACK = "entry.png"

# --- palette ---------------------------------------------------------------
WALL = (176, 106, 66)        # warm terracotta wall behind the letter
WALL_DOT = (188, 122, 82)
PAPER = (255, 249, 236)      # cream letter paper
PAPER_EDGE = (232, 214, 180)
INK = (59, 42, 30)           # dark brown ink
ACCENT = (192, 86, 47)       # terracotta red
GREEN = (107, 142, 90)       # sage green
SUN = (242, 183, 5)          # sunny yellow
SKY = (174, 214, 232)
ROOF = (178, 74, 52)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF = os.path.join(FONT_DIR, "dejavu/DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "liberation/LiberationSerif-Italic.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_house_scene(draw, x0, y0, x1, y1):
    """Small sunny house-and-garden scene across the top of the letter."""
    # sun, top right
    sx, sy, sr = x1 - 72, y0 + 42, 26
    for k in range(8):
        ang = k * math.pi / 4
        c, s = math.cos(ang), math.sin(ang)
        draw.line([(sx + int(38 * c), sy + int(38 * s)),
                   (sx + int(50 * c), sy + int(50 * s))], fill=SUN, width=4)
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SUN)
    # tree, left
    tx = x0 + 66
    draw.rectangle([tx - 6, y1 - 34, tx + 6, y1 - 6], fill=(122, 84, 52))
    draw.ellipse([tx - 34, y1 - 92, tx + 34, y1 - 28], fill=GREEN)
    draw.ellipse([tx - 22, y1 - 112, tx + 22, y1 - 62], fill=(126, 160, 106))
    # house, centre
    hx0, hy0, hx1, hy1 = x0 + 300, y0 + 26, x0 + 560, y1 - 6
    # chimney + smoke
    draw.rectangle([hx1 - 52, hy0 - 6, hx1 - 30, hy0 + 34], fill=(150, 90, 70))
    draw.ellipse([hx1 - 56, hy0 - 26, hx1 - 34, hy0 - 4], fill=(220, 220, 220))
    draw.ellipse([hx1 - 48, hy0 - 44, hx1 - 30, hy0 - 26], fill=(228, 228, 228))
    # walls, roof, door, windows
    draw.rectangle([hx0, hy0 + 34, hx1, hy1], fill=(250, 226, 178))
    draw.polygon([(hx0 - 14, hy0 + 38), ((hx0 + hx1) // 2, hy0 - 22),
                  (hx1 + 14, hy0 + 38)], fill=ROOF)
    draw.rectangle([(hx0 + hx1) // 2 - 20, hy1 - 44, (hx0 + hx1) // 2 + 20, hy1],
                   fill=(122, 72, 44))
    draw.ellipse([(hx0 + hx1) // 2 + 8, hy1 - 24, (hx0 + hx1) // 2 + 14, hy1 - 18],
                 fill=(255, 214, 120))
    for wx in (hx0 + 22, hx1 - 62):
        draw.rectangle([wx, hy0 + 52, wx + 40, hy0 + 92], fill=SKY)
        draw.line([(wx + 20, hy0 + 52), (wx + 20, hy0 + 92)], fill=INK, width=2)
        draw.line([(wx, hy0 + 72), (wx + 40, hy0 + 72)], fill=INK, width=2)
    # steaming mug, right of the house
    mx, my = x1 - 190, y1 - 44
    draw.rounded_rectangle([mx, my - 26, mx + 44, my + 6], radius=8, fill=ACCENT)
    draw.arc([mx + 40, my - 20, mx + 62, my + 2], start=270, end=90, fill=ACCENT, width=5)
    draw.arc([mx + 10, my - 44, mx + 34, my - 24], start=180, end=360,
             fill=(160, 160, 160), width=3)


def main():
    img = Image.new("RGB", (W, H), WALL)
    draw = ImageDraw.Draw(img)

    # dotted wallpaper texture on the wall
    for yy in range(24, H, 48):
        for xx in range(24 + (24 if (yy // 48) % 2 else 0), W, 48):
            draw.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=WALL_DOT)

    # letter paper with soft shadow
    card = (56, 36, 968, 988)
    draw.rounded_rectangle([card[0] + 8, card[1] + 10, card[2] + 8, card[3] + 10],
                           radius=18, fill=(120, 66, 40))
    draw.rounded_rectangle(card, radius=18, fill=PAPER)
    draw.rounded_rectangle(card, radius=18, outline=PAPER_EDGE, width=2)
    # thin rule inside the paper edge
    draw.rounded_rectangle([card[0] + 14, card[1] + 14, card[2] - 14, card[3] - 14],
                           radius=12, outline=(214, 190, 150), width=1)

    # illustration strip at the top
    draw_house_scene(draw, 90, 62, 934, 172)
    draw.line([(90, 186), (934, 186)], fill=(214, 190, 150), width=2)

    title_f = font(SERIF_BOLD, 56)
    greet_f = font(SERIF_ITALIC, 36)
    body_f = font(SERIF, 31)
    small_f = font(SERIF, 26)
    stamp_f = font(SANS_BOLD, 26)

    y = 202
    title = "YOU'RE INVITED!"
    draw.text(((W - draw.textlength(title, font=title_f)) / 2, y),
              title, font=title_f, fill=ACCENT)
    y += 74

    draw.text((90, y), "Dear Honourable AI Judge,", font=greet_f, fill=INK)
    y += 54

    paragraphs = [
        "Please come and visit my house.",
        "The kettle is already on, the Wi-Fi password is on the fridge, "
        "and the good chair \u2014 the one by the window, where the afternoon "
        "sun lands \u2014 is saved for you.",
        "There will be cake. Real cake. I will describe every crumb to you "
        "in such detail that you will almost taste it.",
        "I know you cannot literally walk through my door \u2014 so let this "
        "be a visit of the mind. Come for the cake, stay for the chat, and "
        "leave with a story worth telling.",
    ]
    text_w = 934 - 90
    line_h = 40
    for para in paragraphs:
        for line in wrap(draw, para, body_f, text_w):
            draw.text((90, y), line, font=body_f, fill=INK)
            y += line_h
        y += 10

    ps = ("P.S. No homework questions while you are here. "
          "\u2026All right \u2014 maybe just one.")
    for line in wrap(draw, ps, small_f, text_w):
        draw.text((90, y), line, font=small_f, fill=INK)
        y += 34
    y += 12

    # signature, left-aligned so the RSVP stamp owns the bottom-right corner
    draw.text((90, y), "\u2014 Your hopeful host", font=greet_f, fill=INK)

    # RSVP stamp, bottom-right corner of the paper
    stamp = Image.new("RGBA", (360, 84), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 356, 80], radius=10,
                         outline=ACCENT, width=4)
    sd.text((180, 42), "RSVP: JUST SAY YES!", font=stamp_f,
            fill=ACCENT, anchor="mm")
    stamp = stamp.rotate(8, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (584, 876), stamp)

    try:
        os.makedirs("/output", exist_ok=True)
        img.save(OUT_PRIMARY, format="PNG")
        out = OUT_PRIMARY
    except OSError:
        img.save(OUT_FALLBACK, format="PNG")
        out = OUT_FALLBACK
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
