#!/usr/bin/env python3
"""World News cover for Saturday 21 November 2026.

Draws a one-page newspaper front cover (1024x1024 PNG) with six verified
stories from 21 November 2026, using only the Python standard library.
Writes to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Deterministic: the same bytes on every run.
"""

import os
import struct
import zlib
import binascii

W, H = 1024, 1024

PAPER = (246, 241, 230)
INK = (22, 22, 22)
NAVY = (22, 38, 63)
GOLD = (201, 162, 39)
RED = (176, 30, 36)
TEAL = (15, 118, 110)
BROWN = (124, 74, 33)
BLUE = (29, 78, 216)
DARK = (35, 42, 53)
GREY = (120, 116, 108)
LIGHT_GREY = (232, 227, 216)

# 5x7 bitmap font, rows top to bottom, '#' = on. All text is uppercased.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "00000", "00000", "01100", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for a in range(360):
            import math
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            self.set(x, y, color)

    def char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT[' '])
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == '1':
                    self.fill_rect(x + c * scale, y + r * scale,
                                   scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        for i, ch in enumerate(s):
            self.char(x + i * 6 * scale, y, ch, scale, color)
        return len(s) * 6 * scale

    def text_width(self, s, scale):
        return len(s.upper()) * 6 * scale

    def wrap(self, s, max_w, scale):
        words = s.upper().split(' ')
        lines, cur = [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, color, max_w, line_h, max_lines=None):
        lines = self.wrap(s, max_w, scale)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * line_h, ln, scale, color)
        return len(lines)


def png_bytes(cv):
    def chunk(kind, data):
        c = struct.pack('>I', len(data)) + kind + data
        return c + struct.pack('>I', binascii.crc32(kind + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = b''.join(b'\x00' + bytes(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
                   for y in range(cv.h))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


# ---- pictograms -----------------------------------------------------------

def burst(cv, cx, cy, color1, color2):
    import math
    for k in range(12):
        ang = math.radians(k * 30)
        r = 95 if k % 2 == 0 else 55
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        cv.line(cx, cy, x, y, color1 if k % 2 == 0 else color2)
    cv.disc(cx, cy, 16, color1)
    cv.disc(cx, cy, 8, color2)


def chart_down(cv, x, y, w, h, color):
    pts = [(x + 8, y + 6), (x + 30, y + 10), (x + 52, y + 8),
           (x + 74, y + 16), (x + 96, y + 24), (x + 118, y + 26)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], color)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, color)
    cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 8, pts[-1][1] - 2, color)
    cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 2, pts[-1][1] + 8, color)


def stars_circle(cv, cx, cy, r, color):
    import math
    for k in range(8):
        ang = math.radians(k * 45)
        cv.disc(cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang)),
                3, color)


def spiral(cv, cx, cy, color):
    import math
    for r in (4, 8, 12, 16):
        for a in range(0, 300, 6):
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            cv.set(x, y, color)


def crack(cv, x, y, w, color):
    pts = [(x + 6, y + 4), (x + 30, y + 12), (x + 48, y + 8),
           (x + 72, y + 18), (x + 96, y + 12), (x + 120, y + 22)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], color)
        cv.line(a[0] + 1, a[1], b[0] + 1, b[1], color)


def binary_blocks(cv, x, y, color):
    for i in range(6):
        xx = x + 8 + i * 18
        cv.fill_rect(xx, y + 6, 12, 8, color)
        cv.fill_rect(xx, y + 18, 12, 4, color)


# ---- layout ---------------------------------------------------------------

def draw():
    cv = Canvas(W, H, PAPER)
    cv.fill_rect(0, 0, W, H, PAPER)
    # thin outer frame
    cv.fill_rect(12, 12, W - 24, 3, INK)
    cv.fill_rect(12, H - 15, W - 24, 3, INK)
    cv.fill_rect(12, 12, 3, H - 24, INK)
    cv.fill_rect(W - 15, 12, 3, H - 24, INK)

    # masthead
    cv.fill_rect(24, 24, 976, 108, NAVY)
    title = "WORLD NEWS"
    tw = cv.text_width(title, 8)
    cv.text((W - tw) // 2, 34, title, 8, (255, 255, 255))
    cv.fill_rect(224, 102, 576, 3, GOLD)
    date = "SATURDAY, 21 NOVEMBER 2026"
    dw = cv.text_width(date, 3)
    cv.text((W - dw) // 2, 110, date, 3, GOLD)

    # lead story
    cv.text(28, 152, "WAR IN EUROPE - KYIV / WARSAW", 2, RED)
    cv.para(28, 178, "RUSSIAN MISSILES LAND IN POLAND IN MASS STRIKE ON UKRAINE",
            4, INK, 592, 36, max_lines=3)
    cv.para(28, 300,
            "Russia fired more than 400 drones and 110 missiles at Ukraine "
            "overnight, killing at least eight in Kyiv. Two missiles and a "
            "suspected drone fell in Poland. PM Tusk called it a deliberate "
            "provocation; NATO called it a grave violation.",
            2, INK, 592, 20, max_lines=5)
    # lead art panel
    cv.fill_rect(636, 148, 360, 264, DARK)
    burst(cv, 816, 280, (255, 176, 66), RED)
    cv.line(660, 380, 760, 320, (255, 255, 255))
    cv.line(760, 320, 860, 350, (255, 255, 255))
    cv.disc(660, 380, 4, (255, 255, 255))
    cv.disc(860, 350, 4, (255, 255, 255))

    cv.hline(28, 424, 968, INK)

    # grid rows: (x, y, strip color, art fn, kicker, kicker color,
    #            headline, summary)
    rows = [
        (28, 436, (176, 30, 36), chart_down,
         "MARKETS - NEW YORK", RED,
         "AI SELL-OFF PUSHES S&P 500 AND DOW INTO CORRECTION",
         "US stocks fell sharply on Friday as AI and chip shares plunged; "
         "the Nasdaq dropped 5.3% toward a bear market."),
        (528, 436, BLUE, stars_circle,
         "POLITICS - BRUSSELS", BLUE,
         "UK AND EU SIGN LANDMARK POST-BREXIT RESET DEALS",
         "Prime Minister Andy Burnham signed deals on food trade, carbon "
         "markets and youth mobility at a Brussels summit."),
        (28, 608, TEAL, spiral,
         "WEATHER - INDIA", TEAL,
         "CYCLONE AKVAN SLAMS INDIA'S EAST COAST",
         "Severe Cyclonic Storm Akvan crossed the Odisha and Andhra Pradesh "
         "coast near Gopalpur, bringing heavy rain."),
        (528, 608, BROWN, crack,
         "DISASTER - PERU", BROWN,
         "MAGNITUDE 6.8 QUAKE SHAKES CENTRAL PERU",
         "A magnitude 6.8 earthquake struck the Junin region in the Andes, "
         "with tremors felt in Lima, 320 km away."),
        (28, 780, DARK, binary_blocks,
         "CYBER - WASHINGTON", DARK,
         "FBI PROBES SUSPECTED HACK OF NATIONAL CRIME DATABASE",
         "The FBI is investigating a suspected hack of a core crime database "
         "shared by law enforcement across the US."),
    ]
    for (x, y, strip, art, kicker, kcolor, head, summ) in rows:
        cv.fill_rect(x, y, 468, 30, strip)
        if art is chart_down:
            chart_down(cv, x + 320, y + 2, 140, 26, (255, 255, 255))
        elif art is stars_circle:
            stars_circle(cv, x + 400, y + 15, 10, GOLD)
        elif art is spiral:
            spiral(cv, x + 400, y + 15, (255, 255, 255))
        elif art is crack:
            crack(cv, x + 320, y + 4, 140, (255, 255, 255))
        elif art is binary_blocks:
            binary_blocks(cv, x + 320, y + 2, (74, 222, 128))
        cv.text(x, y + 40, kicker, 2, kcolor)
        cv.para(x, y + 62, head, 3, INK, 468, 26, max_lines=2)
        cv.para(x, y + 118, summ, 2, INK, 468, 18, max_lines=3)

    # also-today box
    bx, by = 528, 780
    cv.fill_rect(bx, by, 468, 160, LIGHT_GREY)
    cv.fill_rect(bx, by, 468, 3, GOLD)
    cv.text(bx + 12, by + 12, "ALSO TODAY", 2, INK)
    cv.para(bx + 12, by + 36,
            "- Saudi-led coalition intercepts Houthi missiles aimed at Riyadh.",
            2, INK, 444, 18, max_lines=2)
    cv.para(bx + 12, by + 78,
            "- India's NSE overtakes Nasdaq as the world's fifth-largest "
            "listed exchange.",
            2, INK, 444, 18, max_lines=3)

    # footer
    foot = "WORLD NEWS - 21 NOVEMBER 2026 - SIX STORIES FROM AROUND THE GLOBE"
    fw = cv.text_width(foot, 2)
    cv.text((W - fw) // 2, 962, foot, 2, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
