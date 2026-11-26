#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Writes a single 1024x1024 PNG invitation letter to /output/entry.png
(falls back to ./entry.png when /output is not writable, e.g. local runs).

STDLIB ONLY: no Pillow, no external dependencies, no system fonts.
The PNG is encoded with zlib + struct, and every glyph comes from a
tiny 5x7 bitmap font defined in this file, so the entry runs in any
sandbox that has a plain Python 3 interpreter (the previous version
failed its runs because the grader sandbox has no Pillow).

Deterministic: no network, no randomness, no timestamps.
"""

import math
import os
import struct
import zlib

W = H = 1024
OUT_PRIMARY = "/output/entry.png"
OUT_FALLBACK = "entry.png"

# --- palette ---------------------------------------------------------------
WALL = (176, 106, 66)        # warm terracotta wall behind the letter
WALL_DOT = (190, 124, 84)
PAPER = (255, 249, 236)      # cream letter paper
PAPER_EDGE = (228, 210, 176)
PAPER_SHADOW = (110, 62, 34)
INK = (59, 42, 30)           # dark brown ink
ACCENT = (192, 86, 47)       # terracotta red
GREEN = (107, 142, 90)       # sage green
TREE_DARK = (84, 118, 70)
SUN = (242, 183, 5)          # sunny yellow
SKY = (174, 214, 232)
ROOF = (178, 74, 52)
DOOR = (96, 58, 32)
TRUNK = (101, 67, 33)
MUG = (70, 110, 140)
SMOKE = (200, 190, 175)

# --- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows of 5 bits ("#" = on, "." = off).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}


class Canvas:
    """A plain RGB pixel buffer with tiny shape helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg[0] for _ in range(w * h * 3))
        # bytearray(bg[0] ...) only sets red; fill properly below.
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def rect_outline(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, t=3):
        self.circle(cx, cy, r, color)
        self.circle(cx, cy, max(0, r - t), PAPER)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via scanlines."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for yy in range(ay, cy + 1):
            if yy < by:
                xa = ax + (bx - ax) * (yy - ay) / max(1, by - ay)
                xb = ax + (cx - ax) * (yy - ay) / max(1, cy - ay)
            else:
                xa = bx + (cx - bx) * (yy - by) / max(1, cy - by)
                xb = ax + (cx - ax) * (yy - ay) / max(1, cy - ay)
            self.fill_rect(int(min(xa, xb)), yy, int(abs(xb - xa)) + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, t = thickness in px."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per glyph)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, text, x, y, scale, color, angle=0):
    """Draw text with the 5x7 bitmap font. Optional rotation (degrees)
    about the (x, y) anchor, used for the tilted RSVP stamp."""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    cx = 0
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    px = cx + col * scale
                    py = row * scale
                    # rotate the scaled pixel block about the anchor
                    for sy in range(scale):
                        for sx in range(scale):
                            rx = px + sx
                            ry = py + sy
                            rxx = int(round(rx * cos_a - ry * sin_a)) + x
                            ryy = int(round(rx * sin_a + ry * cos_a)) + y
                            cv.set(rxx, ryy, color)
        cx += 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def write_png(path, cv):
    """Encode the canvas as a PNG (color type 2, 8-bit) with zlib."""
    raw = bytearray()
    row_len = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * row_len:(y + 1) * row_len]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def draw_scene(cv):
    """A small sunny house scene across the top of the letter paper."""
    # Ground line first, so the house/tree/mug sit on top of it.
    cv.fill_rect(140, 316, 744, 4, PAPER_EDGE)
    # Sun with rays, top-left.
    cv.circle(168, 208, 34, SUN)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x0 = 168 + int(44 * math.cos(rad))
        y0 = 208 + int(44 * math.sin(rad))
        x1 = 168 + int(56 * math.cos(rad))
        y1 = 208 + int(56 * math.sin(rad))
        cv.line(x0, y0, x1, y1, SUN, 5)
    # Tree, left of the house.
    cv.fill_rect(268, 252, 16, 62, TRUNK)
    cv.circle(276, 232, 36, GREEN)
    cv.circle(248, 256, 26, TREE_DARK)
    cv.circle(304, 256, 26, TREE_DARK)
    # House, centre-right.
    cv.fill_rect(560, 236, 210, 104, (232, 196, 150))   # walls
    cv.triangle(540, 238, 780, 238, 660, 168, ROOF)     # roof
    cv.fill_rect(716, 182, 26, 46, (150, 90, 70))        # chimney
    cv.circle(729, 172, 9, SMOKE)                       # smoke puffs
    cv.circle(736, 156, 12, SMOKE)
    cv.circle(744, 140, 13, SMOKE)
    cv.fill_rect(640, 278, 42, 62, DOOR)                 # door
    cv.circle(674, 312, 3, SUN)                          # doorknob
    for wx in (580, 716):
        cv.fill_rect(wx, 256, 36, 36, SKY)               # windows
        cv.fill_rect(wx + 16, 256, 4, 36, PAPER_EDGE)
        cv.fill_rect(wx, 272, 36, 4, PAPER_EDGE)
    # Steaming mug, right.
    cv.fill_rect(838, 272, 56, 44, MUG)
    cv.ring(902, 294, 14, MUG, 5)
    cv.line(852, 258, 848, 240, SMOKE, 4)
    cv.line(866, 258, 870, 240, SMOKE, 4)
    cv.line(880, 258, 876, 240, SMOKE, 4)
    # (ground line drawn first, at the top of this function)


TITLE = "YOU'RE INVITED!"
GREETING = "Dear Honourable AI Judge,"
PARAGRAPHS = [
    "Please come and visit my house. The kettle is already on, the "
    "Wi-Fi password is on the fridge, and the good chair - the one by "
    "the window, where the afternoon sun lands - is saved for you.",
    "There will be cake. Real cake. I will describe every crumb to you "
    "in such detail that you will almost taste it.",
    "I know you cannot literally walk through my door - so let this be "
    "a visit of the mind. Come for the cake, stay for the chat, and "
    "leave with a story worth telling.",
    "P.S. No homework questions while you are here. ... All right - "
    "maybe just one.",
]
SIGNATURE = "- Your hopeful host"
STAMP_LINE1 = "RSVP:"
STAMP_LINE2 = "JUST SAY YES!"


def main():
    cv = Canvas(W, H, WALL)
    # Dotted wallpaper.
    for yy in range(24, H, 48):
        for xx in range(24, W, 48):
            cv.circle(xx, yy, 5, WALL_DOT)

    # Letter paper with a soft shadow.
    cv.fill_rect(78, 128, 884, 835, PAPER_SHADOW)
    cv.fill_rect(70, 120, 884, 835, PAPER)
    cv.rect_outline(70, 120, 884, 835, PAPER_EDGE, 3)

    draw_scene(cv)

    # Title.
    tw = text_width(TITLE, 7)
    draw_text(cv, TITLE, (W - tw) // 2, 336, 7, ACCENT)
    cv.fill_rect(212, 402, 600, 4, ACCENT)

    # Greeting.
    draw_text(cv, GREETING, 110, 424, 4, INK)

    # Body paragraphs, scale 3, wrapped to the paper's inner width.
    y = 470
    for i, para in enumerate(PARAGRAPHS):
        for line in wrap_text(para, 3, 804):
            draw_text(cv, line, 110, y, 3, INK)
            y += 27
        y += 10  # gap between paragraphs

    # Signature, bottom-left.
    draw_text(cv, SIGNATURE, 110, 892, 4, INK)

    # RSVP stamp, bottom-right (double red border, red text, one line).
    sx, sy = 648, 898
    cv.rect_outline(sx, sy, 268, 44, ACCENT, 4)
    cv.rect_outline(sx + 8, sy + 8, 252, 28, ACCENT, 2)
    stamp = "RSVP: JUST SAY YES!"
    sw = text_width(stamp, 2)
    draw_text(cv, stamp, sx + (268 - sw) // 2, sy + 15, 2, ACCENT)

    try:
        out = OUT_PRIMARY
        os.makedirs(os.path.dirname(OUT_PRIMARY), exist_ok=True)
        size = write_png(out, cv)
    except OSError:
        out = OUT_FALLBACK
        size = write_png(out, cv)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, W, H))


if __name__ == "__main__":
    main()

