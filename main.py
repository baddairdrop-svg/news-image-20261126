"""THE WORLD IN ONE DAY - Thursday 26 November 2026.

A program that draws one 1024x1024 newspaper front page summing up
the world's news of Thursday 26 November 2026, for the make.fun
bounty news-image-20261126, entered by @badd-airdrop2.

Pure Python 3 standard library only: no network, no fonts on disk,
no randomness, no clock. Type is set from glyph bitmaps rasterised
from DejaVu (free licence) and carried in glyphs.py beside this
file; the page is drawn on a 2x supersampled canvas with a
hand-written PNG encoder and written to /output/entry.png.
Running it twice writes the same bytes.

Every story on the page happened or was first reported on Thursday
26 November 2026, as the named outlets reported it. Stories that
look like 26 November news but are not are listed in the DATE CHECK
panel with their real dates. All times are UTC.
"""

import base64
import math
import os
import struct
import zlib

from glyphs import (SERIF, SERIF_ASC, SERIF_DESC, SERIF_EM,
                    SERIFR, SERIFR_ASC, SERIFR_DESC, SERIFR_EM,
                    SANS, SANS_ASC, SANS_DESC, SANS_EM,
                    SANSB, SANSB_ASC, SANSB_DESC, SANSB_EM)

W = 1024
H = 1024
SS = 2                      # supersampling factor (canvas is W*SS)
MX = 24                     # page margin
CW = W - 2 * MX             # content width

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (22, 22, 26)
NAVY = (26, 41, 73)
NAVY2 = (40, 58, 97)
BURGUNDY = (120, 30, 42)
RED = (178, 44, 52)
GOLD = (198, 159, 38)
GOLDD = (146, 114, 24)
GREY = (70, 76, 90)
HAIR = (214, 207, 191)
WHITE = (255, 255, 255)
CREAM2 = (239, 232, 217)
SKY1 = (15, 23, 47)
SKY2 = (54, 46, 80)
DUSK1 = (31, 35, 67)
DUSK2 = (130, 66, 66)
SEA = (31, 49, 85)
GREEN = (45, 92, 60)
ORANGE = (232, 120, 40)
TEAL = (46, 110, 100)

# ---------------------------------------------------------------- glyphs
_GCACHE = {}


def glyph_alpha(font, ch):
    """Decode a glyph's 4-bit alpha map to bytes (cached)."""
    key = (id(font), ch)
    got = _GCACHE.get(key)
    if got is not None:
        return got
    _adv, _bx, _by, w, h, b85 = font[ch]
    if not b85:
        _GCACHE[key] = b""
        return b""
    packed = zlib.decompress(base64.b85decode(b85))
    out = bytearray(w * h)
    for i in range(w * h):
        byte = packed[i // 2]
        out[i] = ((byte >> 4) if i % 2 == 0 else (byte & 15)) * 17
    _GCACHE[key] = bytes(out)
    return _GCACHE[key]


def text_width(s, font, em, size, tracking=0.0):
    """Width in logical px of s set at `size` (logical px em)."""
    scale = size * SS / em
    total = 0.0
    for ch in s:
        g = font.get(ch) or font["?"]
        total += g[0] * scale / SS + tracking
    return total - (tracking if s else 0.0)


def wrap_text(s, font, em, size, max_width, tracking=0.0):
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, font, em, size, tracking) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    """Logical W x H canvas stored at SS supersampling."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.dw = w * SS
        self.dh = h * SS
        self.px = bytearray(bg * self.dw * self.dh)

    def set(self, x, y, color):
        if 0 <= x < self.dw and 0 <= y < self.dh:
            i = (y * self.dw + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def blend(self, x, y, color, a):
        if a <= 0 or not (0 <= x < self.dw and 0 <= y < self.dh):
            return
        if a >= 255:
            self.set(x, y, color)
            return
        i = (y * self.dw + x) * 3
        inv = 255 - a
        self.px[i] = (color[0] * a + self.px[i] * inv) // 255
        self.px[i + 1] = (color[1] * a + self.px[i + 1] * inv) // 255
        self.px[i + 2] = (color[2] * a + self.px[i + 2] * inv) // 255

    def rect(self, x, y, w, h, color):
        x, y, w, h = int(x * SS), int(y * SS), int(w * SS), int(h * SS)
        row = bytes(color) * w
        for yy in range(y, y + h):
            if 0 <= yy < self.dh:
                i = (yy * self.dw + x) * 3
                self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def vgrad(self, x, y, w, h, top, bottom):
        x, y, w, h = int(x * SS), int(y * SS), int(w * SS), int(h * SS)
        for yy in range(y, y + h):
            t = (yy - y) / max(1, h - 1)
            c = (int(top[0] + (bottom[0] - top[0]) * t),
                 int(top[1] + (bottom[1] - top[1]) * t),
                 int(top[2] + (bottom[2] - top[2]) * t))
            row = bytes(c) * w
            i = (yy * self.dw + x) * 3
            self.px[i:i + len(row)] = row

    def line(self, x0, y0, x1, y1, color, t=1):
        x0, y0, x1, y1 = int(x0 * SS), int(y0 * SS), int(x1 * SS), int(y1 * SS)
        t = max(1, int(round(t * SS)))
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for oy in range(t):
                for ox in range(t):
                    self.set(x + ox, y + oy, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        cx, cy, r = int(cx * SS), int(cy * SS), int(r * SS)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        cx, cy, r, t = int(cx * SS), int(cy * SS), int(r * SS), int(t * SS)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, color)

    def polygon(self, pts, color):
        pts = [(x * SS, y * SS) for (x, y) in pts]
        miny = int(min(p[1] for p in pts))
        maxy = int(max(p[1] for p in pts))
        n = len(pts)
        for yy in range(miny, maxy + 1):
            nodes = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (yy >= min(y0, y1)) and (yy < max(y0, y1)):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                xa = int(nodes[i])
                xb = int(nodes[i + 1])
                for xx in range(xa, xb + 1):
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.polygon([(x0, y0), (x1, y1), (x2, y2)], color)

    # ---- text ----
    def text(self, x, y, s, font, em, asc, size, color, tracking=0.0):
        """Draw text with baseline at logical y; returns x after it."""
        scale = size * SS / em
        cx = x * SS
        baseline = y * SS
        for ch in s:
            g = font.get(ch) or font["?"]
            adv, bx, by, w, h, _b85 = g
            if w and h:
                alpha = glyph_alpha(font, ch)
                gx = cx + bx * scale
                gy = baseline - asc * scale + by * scale
                dw = max(1, int(round(w * scale)))
                dh = max(1, int(round(h * scale)))
                for dy in range(dh):
                    sy = dy / scale
                    iy = int(sy)
                    fy = sy - iy
                    for dx in range(dw):
                        sx = dx / scale
                        ix = int(sx)
                        fx = sx - ix
                        a00 = alpha[iy * w + ix] if iy < h and ix < w else 0
                        a10 = alpha[iy * w + ix + 1] if iy < h and ix + 1 < w else 0
                        a01 = alpha[(iy + 1) * w + ix] if iy + 1 < h and ix < w else 0
                        a11 = alpha[(iy + 1) * w + ix + 1] if iy + 1 < h and ix + 1 < w else 0
                        a = int(a00 * (1 - fx) * (1 - fy) + a10 * fx * (1 - fy)
                                + a01 * (1 - fx) * fy + a11 * fx * fy)
                        if a:
                            self.blend(int(gx) + dx, int(gy) + dy, color, a)
            cx += adv * scale + tracking * SS
        return cx / SS

    def text_center(self, cx, y, s, font, em, asc, size, color,
                    tracking=0.0):
        w = text_width(s, font, em, size, tracking)
        return self.text(cx - w / 2, y, s, font, em, asc, size, color,
                         tracking)

    def text_right(self, right, y, s, font, em, asc, size, color,
                   tracking=0.0):
        w = text_width(s, font, em, size, tracking)
        return self.text(right - w, y, s, font, em, asc, size, color,
                         tracking)

    def para(self, x, y, s, font, em, asc, size, color, max_width,
             leading=None, tracking=0.0):
        """Wrapped paragraph; y is the first baseline; returns y after."""
        if leading is None:
            leading = size * 1.35
        for line in wrap_text(s, font, em, size, max_width, tracking):
            self.text(x, y, line, font, em, asc, size, color, tracking)
            y += leading
        return y

    def downsample(self):
        out = bytearray(W * H * 3)
        for y in range(H):
            for x in range(W):
                r = g = b = 0
                for oy in range(SS):
                    base = ((y * SS + oy) * self.dw + x * SS) * 3
                    for ox in range(SS):
                        i = base + ox * 3
                        r += self.px[i]
                        g += self.px[i + 1]
                        b += self.px[i + 2]
                n = SS * SS
                j = (y * W + x) * 3
                out[j] = r // n
                out[j + 1] = g // n
                out[j + 2] = b // n
        return out


# ---------------------------------------------------------------- PNG encoder
def png_bytes(raw):
    rows = bytearray()
    stride = W * 3
    for y in range(H):
        rows.append(0)
        start = y * stride
        rows.extend(raw[start:start + stride])
    data = zlib.compress(bytes(rows), 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- illustrations
# Flat editorial vector style: layered silhouettes, muted palette,
# fine gold detail. All three heroes share the same visual language.

def scene_summit(c, x, y, w, h):
    """Summit table under flags: a long table, chairs, two flag poles."""
    c.vgrad(x, y, w, h, (24, 34, 64), NAVY2)
    # window light bands
    for i in range(5):
        wx = x + 14 + i * (w - 28) / 5
        c.rect(wx, y + 8, (w - 28) / 5 - 8, h * 0.52, (52, 70, 108))
    # flags
    for fx, col in ((x + w * 0.30, (30, 70, 160)), (x + w * 0.62, GOLD)):
        c.vline(fx, y + 10, h * 0.55, (200, 200, 205), 1.6)
        c.rect(fx + 1, y + 11, 26, 16, col)
    # table
    ty = y + h * 0.66
    c.polygon([(x + w * 0.16, ty), (x + w * 0.84, ty),
               (x + w * 0.78, ty + h * 0.16), (x + w * 0.22, ty + h * 0.16)],
              (120, 92, 58))
    c.hline(x + w * 0.16, ty, w * 0.68, (150, 118, 76), 2)
    # seated silhouettes
    for i in range(6):
        sx = x + w * (0.24 + i * 0.105)
        c.circle(sx, ty - 7, 4.6, (18, 22, 38))
        c.rect(sx - 5, ty - 3, 10, 8, (18, 22, 38))
    # papers on the table
    for i in range(4):
        px = x + w * (0.30 + i * 0.13)
        c.rect(px, ty + 3, 14, 6, (238, 234, 222))
    # budget tag on the table
    c.rect(x + w * 0.40, ty + h * 0.20, 74, 13, (238, 234, 222))
    c.text_center(x + w * 0.40 + 37, ty + h * 0.20 + 10, "€1.582TN",
                  SANSB, SANSB_EM, SANSB_ASC, 8, BURGUNDY)


def scene_skyline(c, x, y, w, h):
    """City skyline at dusk with smoke columns."""
    c.vgrad(x, y, w, h, DUSK1, DUSK2)
    c.circle(x + w * 0.78, y + h * 0.30, 13, (238, 196, 120))
    # far buildings
    far = [(0.02, 0.34), (0.14, 0.26), (0.26, 0.40), (0.40, 0.30),
           (0.55, 0.36), (0.70, 0.28), (0.84, 0.38)]
    for fx, fh in far:
        bx = x + w * fx
        bh = h * fh
        c.rect(bx, y + h * 0.92 - bh, w * 0.10, bh, (58, 52, 84))
    # smoke
    for sx, sh in ((0.30, 0.42), (0.62, 0.34)):
        px = x + w * sx
        for i in range(5):
            c.circle(px + i * 3, y + h * (0.52 - i * 0.07), 7 - i * 0.7,
                     (96, 92, 110))
    # near buildings
    near = [(0.06, 0.44), (0.24, 0.34), (0.44, 0.50), (0.66, 0.38),
            (0.82, 0.46)]
    for fx, fh in near:
        bx = x + w * fx
        bh = h * fh
        c.rect(bx, y + h - bh, w * 0.13, bh, (24, 22, 40))
        for wy in range(3):
            for wx in range(2):
                if (int(fx * 100) + wy + wx) % 3:
                    c.rect(bx + 4 + wx * 9, y + h - bh + 6 + wy * 12,
                           4, 6, (240, 205, 120))
    c.hline(x, y + h - 1, w, (16, 14, 28), 2)
    c.rect(x + 4, y + h - 13, 216, 11, (16, 14, 28))
    c.text(x + 8, y + h - 5, "DEIR AL-BALAH · GAZA CITY · BUREIJ",
           SANSB, SANSB_EM, SANSB_ASC, 6.5, (238, 205, 150),
           tracking=0.6)


def scene_rates(c, x, y, w, h):
    """Rising rate chart over a dawn skyline."""
    c.vgrad(x, y, w, h, SKY1, NAVY2)
    for i in range(1, 5):
        gy = y + i * h / 5
        c.hline(x + 8, gy, w - 16, (58, 74, 110), 0.7)
    # skyline silhouette
    towers = [(0.04, 0.30), (0.16, 0.44), (0.30, 0.34), (0.46, 0.52),
              (0.62, 0.40), (0.78, 0.48), (0.90, 0.36)]
    for fx, fh in towers:
        bx = x + w * fx
        bh = h * fh
        c.rect(bx, y + h - bh, w * 0.09, bh, (20, 30, 56))
    # rising line with arrow
    pts = [(x + w * 0.08, y + h * 0.78), (x + w * 0.30, y + h * 0.66),
           (x + w * 0.50, y + h * 0.70), (x + w * 0.70, y + h * 0.44),
           (x + w * 0.88, y + h * 0.24)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
               GOLD, 2.6)
    for px, py in pts:
        c.circle(px, py, 3.2, GOLD)
        c.circle(px, py, 1.4, WHITE)
    ax, ay = pts[-1]
    c.polygon([(ax, ay - 8), (ax + 10, ay + 2), (ax - 4, ay + 4)], GOLD)
    c.text(ax - 46, ay - 6, "3.25%", SANSB, SANSB_EM, SANSB_ASC, 11,
           (238, 196, 120))
    c.text(pts[0][0] - 2, pts[0][1] + 16, "2.75%", SANSB, SANSB_EM,
           SANSB_ASC, 8, (150, 170, 205))
    # percent glyphs as bars of light
    c.text(x + w * 0.10, y + h * 0.34, "%", SERIF, SERIF_EM, SERIF_ASC,
           30, (110, 130, 170))


SCENES = {"summit": scene_summit, "skyline": scene_skyline,
          "rates": scene_rates}


def icon_bank(c, x, y, s):
    c.polygon([(x, y + s * 0.28), (x + s * 0.5, y),
               (x + s, y + s * 0.28)], NAVY)
    for i in range(4):
        c.rect(x + s * (0.08 + i * 0.24), y + s * 0.36, s * 0.12,
               s * 0.44, NAVY)
    c.rect(x, y + s * 0.86, s, s * 0.12, NAVY)


def icon_train(c, x, y, s):
    c.rect(x + s * 0.12, y + s * 0.08, s * 0.76, s * 0.62, NAVY)
    c.rect(x + s * 0.22, y + s * 0.18, s * 0.24, s * 0.2, WHITE)
    c.rect(x + s * 0.54, y + s * 0.18, s * 0.24, s * 0.2, WHITE)
    c.circle(x + s * 0.3, y + s * 0.55, s * 0.07, GOLD)
    c.circle(x + s * 0.7, y + s * 0.55, s * 0.07, GOLD)
    c.line(x + s * 0.3, y + s * 0.7, x + s * 0.12, y + s * 0.98, NAVY, 1.6)
    c.line(x + s * 0.7, y + s * 0.7, x + s * 0.88, y + s * 0.98, NAVY, 1.6)


def icon_chess(c, x, y, s):
    for r in range(4):
        for col in range(4):
            if (r + col) % 2 == 0:
                c.rect(x + col * s / 4, y + r * s / 4, s / 4, s / 4, NAVY)
    c.frame(x, y, s, s, NAVY, 1.2)


def icon_flame(c, x, y, s):
    c.polygon([(x + s * 0.5, y), (x + s * 0.78, y + s * 0.55),
               (x + s * 0.66, y + s * 0.95), (x + s * 0.34, y + s * 0.95),
               (x + s * 0.22, y + s * 0.55)], RED)
    c.polygon([(x + s * 0.5, y + s * 0.38), (x + s * 0.64, y + s * 0.68),
               (x + s * 0.58, y + s * 0.92), (x + s * 0.42, y + s * 0.92),
               (x + s * 0.36, y + s * 0.68)], ORANGE)


def icon_shield(c, x, y, s):
    c.polygon([(x + s * 0.5, y), (x + s * 0.92, y + s * 0.14),
               (x + s * 0.92, y + s * 0.52), (x + s * 0.5, y + s),
               (x + s * 0.08, y + s * 0.52), (x + s * 0.08, y + s * 0.14)],
              NAVY)
    c.polygon([(x + s * 0.5, y + s * 0.16), (x + s * 0.78, y + s * 0.26),
               (x + s * 0.78, y + s * 0.5), (x + s * 0.5, y + s * 0.84),
               (x + s * 0.22, y + s * 0.5), (x + s * 0.22, y + s * 0.26)],
              GOLD)


def icon_ball(c, x, y, s):
    c.circle(x + s * 0.5, y + s * 0.5, s * 0.46, NAVY)
    c.ring(x + s * 0.5, y + s * 0.5, s * 0.46, WHITE, 1.2)
    c.polygon([(x + s * 0.5, y + s * 0.34), (x + s * 0.64, y + s * 0.46),
               (x + s * 0.58, y + s * 0.64), (x + s * 0.42, y + s * 0.64),
               (x + s * 0.36, y + s * 0.46)], WHITE)


def icon_scroll(c, x, y, s):
    c.rect(x + s * 0.16, y + s * 0.06, s * 0.68, s * 0.88, NAVY)
    c.rect(x + s * 0.24, y + s * 0.14, s * 0.52, s * 0.72, WHITE)
    for i in range(4):
        c.hline(x + s * 0.32, y + s * (0.28 + i * 0.14), s * 0.36,
                GREY, 1.4)
    c.circle(x + s * 0.5, y + s * 0.78, s * 0.09, RED)


def icon_rocket(c, x, y, s):
    c.polygon([(x + s * 0.5, y), (x + s * 0.66, y + s * 0.3),
               (x + s * 0.66, y + s * 0.72), (x + s * 0.34, y + s * 0.72),
               (x + s * 0.34, y + s * 0.3)], NAVY)
    c.circle(x + s * 0.5, y + s * 0.38, s * 0.09, WHITE)
    c.polygon([(x + s * 0.34, y + s * 0.6), (x + s * 0.16, y + s * 0.88),
               (x + s * 0.34, y + s * 0.88)], RED)
    c.polygon([(x + s * 0.66, y + s * 0.6), (x + s * 0.84, y + s * 0.88),
               (x + s * 0.66, y + s * 0.88)], RED)
    c.polygon([(x + s * 0.42, y + s * 0.72), (x + s * 0.58, y + s * 0.72),
               (x + s * 0.5, y + s * 0.98)], ORANGE)


def icon_chart(c, x, y, s):
    heights = [0.4, 0.62, 0.52, 0.85]
    for i, hh in enumerate(heights):
        c.rect(x + s * (0.06 + i * 0.24), y + s * (1 - hh), s * 0.17,
               s * hh, NAVY)
    c.hline(x, y + s * 0.98, s, NAVY, 1.6)


def icon_drop(c, x, y, s):
    c.polygon([(x + s * 0.5, y), (x + s * 0.8, y + s * 0.52),
               (x + s * 0.72, y + s * 0.86), (x + s * 0.5, y + s * 0.98),
               (x + s * 0.28, y + s * 0.86), (x + s * 0.2, y + s * 0.52)],
              TEAL)
    c.circle(x + s * 0.42, y + s * 0.62, s * 0.09, WHITE)


def icon_virus(c, x, y, s):
    cx, cy = x + s * 0.5, y + s * 0.5
    for k in range(8):
        ang = k * math.pi / 4
        c.line(cx, cy, cx + math.cos(ang) * s * 0.46,
               cy + math.sin(ang) * s * 0.46, RED, 2.2)
        c.circle(cx + math.cos(ang) * s * 0.46,
                 cy + math.sin(ang) * s * 0.46, s * 0.07, RED)
    c.circle(cx, cy, s * 0.3, RED)
    c.circle(cx - s * 0.09, cy - s * 0.06, s * 0.06, WHITE)
    c.circle(cx + s * 0.1, cy + s * 0.09, s * 0.05, WHITE)


def icon_missile(c, x, y, s):
    # smoke trail first, so the body sits on top of it
    for i, (tx, ty, tr) in enumerate(((0.30, 0.66, 0.09),
                                      (0.20, 0.78, 0.11),
                                      (0.10, 0.90, 0.13))):
        c.circle(x + s * tx, y + s * ty, s * tr, (150, 150, 158))
    c.polygon([(x + s * 0.88, y + s * 0.08), (x + s * 0.62, y + s * 0.18),
               (x + s * 0.36, y + s * 0.46), (x + s * 0.52, y + s * 0.62),
               (x + s * 0.80, y + s * 0.34)], (96, 106, 126))
    c.polygon([(x + s * 0.88, y + s * 0.08), (x + s * 0.74, y + s * 0.14),
               (x + s * 0.80, y + s * 0.34)], RED)
    c.polygon([(x + s * 0.36, y + s * 0.46), (x + s * 0.16, y + s * 0.52),
               (x + s * 0.26, y + s * 0.64), (x + s * 0.52, y + s * 0.62)],
              BURGUNDY)
    c.circle(x + s * 0.66, y + s * 0.28, s * 0.055, WHITE)


ICONS = {"bank": icon_bank, "train": icon_train, "chess": icon_chess,
         "flame": icon_flame, "shield": icon_shield, "ball": icon_ball,
         "scroll": icon_scroll, "rocket": icon_rocket,
         "chart": icon_chart, "drop": icon_drop,
         "virus": icon_virus, "missile": icon_missile}


def draw_banner_scene(c, x, y, w, h, icon, rcol):
    """Pictorial mini-scene for a grid card banner: tinted sky,
    skyline silhouette, sun, and the story's emblem drawn large."""
    light = tuple(int(v + (255 - v) * 0.82) for v in rcol)
    mid = tuple(int(v + (255 - v) * 0.55) for v in rcol)
    c.vgrad(x, y, w, h, light, mid)
    c.circle(x + w - 16, y + 10, 6, (238, 196, 120))
    # skyline silhouette along the bottom of the band
    sil = tuple(int(v * 0.55) for v in rcol)
    towers = [(0.03, 0.30), (0.13, 0.44), (0.24, 0.26), (0.62, 0.38),
              (0.74, 0.28), (0.85, 0.46), (0.94, 0.32)]
    for fx, fh in towers:
        bh = h * fh
        c.rect(x + w * fx, y + h - bh, w * 0.075, bh, sil)
    c.hline(x, y + h - 1, w, sil, 1.6)
    ICONS[icon](c, x + w / 2 - 15, y + 3, 30)


# ---------------------------------------------------------------- stories
# Every item happened or was first reported on Thursday 26 November
# 2026, verified against its named source (event date and first
# publication date checked separately). Kyiv: night of 25-26 Nov,
# 26 Nov Kyiv local time. Bogor mine: 23 Nov collapse, search
# resumed and toll reported 26 Nov. All times UTC.
# Heroes: (scene, place, category, headline, summary, source, chip,
#          hour)
HEROES = [
    ("summit", "BRUSSELS", "DIPLOMACY", "EU leaders end summit "
     "with no budget deal", "No agreement on the €1.582tn budget or "
     "€45bn Ukraine loan; decision pushed to 17–18 Dec.",
     "REUTERS · AP", "NO DEAL", 18.0),
    ("skyline", "GAZA", "WAR", "Israeli strikes kill at least "
     "nine in Gaza", "Overnight strikes hit Deir Al-Balah, Gaza City "
     "and Bureij; a deputy minister among the dead.",
     "REUTERS", "AT LEAST 9 DEAD", 4.0),
    ("rates", "SEOUL", "ECONOMY", "Bank of Korea raises rate "
     "to 3.25%", "Third hike this year, highest since Nov 2024; "
     "2026 growth forecast raised to 3.9%.",
     "REUTERS · BOK", "+25 BP", 1.0),
]

HERO_CONF = ["REPORTED", "REPORTED", "OFFICIAL"]
HERO_WHY = ["Ukraine's 2027 funding gap stays open.",
            "Third night of strikes strains ceasefire.",
            "Asia's rate cycle turns tighter."]

STATS = [("3.25%", "BANK OF KOREA RATE"), ("€1.582TN", "EU BUDGET CEILING"),
         ("12,021", "EBOLA CASES, DR CONGO"), ("39–35", "BEARS BEAT LIONS"),
         ("+12.2%", "AUSTRALIA CAPEX")]

# Grid: (icon, place, category, headline, summary, source)
GRID = [
    ("bank", "BRUSSELS", "ECONOMY", "De Cos picked as next "
     "ECB president", "Spain's ex-central bank chief succeeds "
     "Lagarde in Feb 2027.", "REUTERS"),
    ("train", "LONDON", "LABOUR", "Tube drivers begin eight "
     "24-hour strikes", "Walkout from 12:00 UTC; no Circle or "
     "Piccadilly line.", "REUTERS · TFL"),
    ("chess", "GENEVA", "SPORT", "Chess Game 3 drawn after "
     "60 moves", "Sindarov and Gukesh level 1.5–1.5, third draw.",
     "FIDE · CHESS.COM"),
    ("flame", "KHARKIV", "WAR", "Russian drone kills two in "
     "apartment block", "Shahed struck 15th floor ~03:00 UTC; "
     "three injured.", "KYIV POST · DSNS"),
    ("shield", "KUWAIT", "WAR", "Two Italian technicians killed "
     "in drone attack", "Italy and Kuwait blame Iran; Tehran "
     "denies involvement.", "REUTERS"),
    ("drop", "JAZAN", "ENERGY", "Aramco refinery hit, one "
     "worker killed", "Projectile hit 400,000 bpd refinery; "
     "some ops halted.", "REUTERS"),
    ("ball", "DETROIT", "SPORT", "Bears beat Lions 39–35 on "
     "Thanksgiving", "Williams found Odunze with 3 seconds left.",
     "AP"),
    ("scroll", "NEW DELHI", "POLITICS", "India marks 77th "
     "Constitution Day", "Murmu at Supreme Court; 30,000+ at "
     "Mysuru event.", "PIB"),
    ("rocket", "ORBIT", "SPACE", "Progress MS-36 docks with "
     "the space station", "Reached Rassvet 12:08 UTC with "
     "2,427 kg cargo.", "ROSCOSMOS · INTERFAX"),
    ("chart", "TOKYO", "MARKETS", "Asia shares rebound at "
     "Thursday close", "Nikkei +0.9%, KOSPI +0.3%; US markets shut.",
     "AP"),
]

GRID_CONF = ["OFFICIAL", "REPORTED", "OFFICIAL", "REPORTED",
             "REPORTED", "REPORTED", "OFFICIAL", "OFFICIAL",
             "OFFICIAL", "REPORTED"]
GRID_BANNER = ["FEB 2027", "12:00 UTC", "1.5–1.5", "03:00 UTC",
               "IRAN DENIES", "400K BPD", "3 SEC LEFT", "77TH",
               "12:08 UTC", "+0.9%"]

# Also: (place, headline) - stories 14-78, one line each.
ALSO = [
    ("Tokyo", "BoJ's Tamura signals faster hikes to neutral"),
    ("Xichang", "Long March 2D launches Yaogan-49 satellites"),
    ("Mumbai", "city marks 18 years since 26/11 attacks"),
    ("New Delhi", "look-out circular issued against Saurav Das"),
    ("New Delhi", "court defers Rashid bail verdict to Dec 8"),
    ("Doha", "Sri Lanka A beat India A to reach Rising Stars final"),
    ("New Delhi", "India asks Netflix not to air Pakistani series"),
    ("Shanghai", "Weimob plans GPU cluster with 5,000 Nvidia chips"),
    ("Beijing", "defence ministry tells Japan to stop stirring trouble"),
    ("Beijing", "Asian economies hit back at new US tariff plans"),
    ("Tokyo", "JETRO: Chinese firms a growing threat abroad"),
    ("Beijing", "US chip curbs threaten Chinese AI development"),
    ("China", "researcher names MiniMax in data-access findings"),
    ("Bogor", "search resumes for 13 trapped miners, 13 dead"),
    ("Islamabad", "PIA says UK flights back on own 777 fleet"),
    ("Tokyo", "final September indexes: leading 116.5"),
    ("Canberra", "AIHW releases alcohol-harm data"),
    ("Canberra", "33-point council funding plan unveiled"),
    ("Canberra", "gender-equality report makes 14 recommendations"),
    ("Canberra", "inquiry into online peptide sales"),
    ("Hicks Bay", "M4.8 quake recorded off East Cape"),
    ("Sydney", "Virgin Australia staff strike at four airports"),
    ("Port Vila", "M4.7 quake strikes near Vanuatu capital"),
    ("Wellington", "PILLAR NZ issues statement"),
    ("Sydney", "Wesley Mission backs gambling reform"),
    ("Auckland", "Fisher & Paykel lifts profit guidance 37%"),
    ("Sydney", "Neuren shares halted ahead of FDA update"),
    ("Melbourne", "Coles targets over A$1.1bn in savings"),
    ("Canberra", "Climate Change Statement: emissions -42% by 2030"),
    ("Brisbane", "Queensland ambulance chief Craig Emery resigns"),
    ("Canberra", "private capex jumps 12.2% on data centres"),
    ("Kyiv", "ballistic attack injures seven, two seriously"),
    ("Ryazan", "Ukrainian drones hit oil refinery, one injured"),
    ("Paris", "about 2,000 students march over university funding"),
    ("Paris", "police gather at stations over risk allowance"),
    ("London", "Lord Mann opens BBC antisemitism investigation"),
    ("Frankfurt", "ECB accounts show support for October hike"),
    ("Berlin", "Wadephul urges tariff-deal compliance"),
    ("Berlin", "trial opens of woman accused of spying for Russia"),
    ("Strasbourg", "EU parliament condemns Türkiye–Libya sea pact"),
    ("Athens", "parliament passes digital-consortium bill"),
    ("Bucharest", "prosecutors charge opposition leader Simion"),
    ("Odesa", "Ukraine says Russia hit two grain ships"),
    ("Amsterdam", "groups ask court to halt Meta glasses sales"),
    ("Frankfurt", "European shares close higher, Stoxx +1.8%"),
    ("Montgomery", "Alabama State beat Tuskegee 45–0"),
    ("East Coast", "Thanksgiving storm cuts power, cancels flights"),
    ("Buenos Aires", "CGT marches over health-fund crisis"),
    ("West Palm Beach", "Trump demands probe of GDP figures"),
    ("Buenos Aires", "Congress backs central-bank charter reform"),
    ("New York", "NBC airs 2025 Macy's parade rerun"),
    ("San Diego", "Texas beat Georgetown 92–83"),
    ("Ghubeish", "drone strike on truck kills at least 11"),
    ("Naivasha", "Steinmeier visits Crescent Island"),
    ("Nairobi", "trade roadshow opens, Equity signs MUFG deal"),
    ("Dar es Salaam", "World CEO Summit Africa opens"),
    ("Durban", "water dialogue ends with eight resolutions"),
    ("Kigali", "YouthConnekt hosts UniPods ministerial dialogue"),
    ("Kinshasa", "Ebola cases pass 12,000 in DR Congo"),
    ("Dubai", "DOERS summit closes with Fraunhofer deal"),
    ("Geneva", "UNCTAD: seaborne trade 12.3bn tons in 2025"),
    ("Geneva", "UN minority forum opens 19th session"),
    ("Nairobi", "UN-Habitat talks put homelessness on agenda"),
    ("Global", "WHO backs new oral gonorrhoea drug"),
    ("Port-au-Prince", "WHO chief brings $1m hospital equipment"),
]

# Region per story 1-78: 0 Asia, 1 Oceania, 2 Europe, 3 Americas,
# 4 Africa, 5 Middle East, 6 Global.
REGIONS = [
    2, 5, 0,
    2, 2, 2, 2, 5, 5, 3, 0, 6, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4,
    5,
    6, 6, 6, 6, 6,
]

REGION_NAMES = ["ASIA", "OCEANIA", "EUROPE", "AMERICAS", "AFRICA",
                "MID EAST", "GLOBAL"]
REGION_COLORS = [NAVY, TEAL, BURGUNDY, GOLD, (160, 90, 30),
                 (140, 60, 90), (110, 80, 140)]

FIELDS = [
    "Diplomacy", "War", "Economy",
    "Economy", "Labour", "Sport", "War", "War", "Energy", "Sport",
    "Politics", "Space", "Markets",
    "Economy", "Space", "Society", "Justice", "Justice", "Sport",
    "Culture", "Tech", "Diplomacy", "Trade", "Business", "Tech",
    "Tech", "Disaster", "Transport", "Economy",
    "Health", "Politics", "Rights", "Health", "Disaster", "Labour",
    "Disaster", "Society", "Society", "Business", "Business",
    "Business", "Climate", "Politics", "Economy",
    "War", "War", "Society", "Labour", "Media", "Economy",
    "Diplomacy", "Justice", "Diplomacy", "Tech", "Justice", "War",
    "Tech", "Markets",
    "Sport", "Disaster", "Labour", "Politics", "Economy", "Culture",
    "Sport",
    "War", "Diplomacy", "Business", "Business", "Environment",
    "Society", "Health",
    "Business",
    "Trade", "Rights", "Humanitarian", "Health", "Health",
]

# ALSO items carrying a CLAIM badge (one side's account).
ALSO_CLAIM = {56, 62}

SUBHEAD = ("EU summit ends without a deal · strikes kill nine in "
           "Gaza · Korea raises rates")

DATE_CHECK = ["Macy's postponement decision — 25 Nov",
              "Sudan Blue Nile strikes — 24 Nov",
              "Chen Jining probe — 24 Nov",
              "Real Madrid 5–1 PSV — 24 Nov",
              "US jobless claims release — 25 Nov",
              "Hera Dimorphos images — 25 Nov",
              "India–Nepal package — 23 Nov",
              "Swiss tourist elephant attack — 19 Nov"]

FOOTER = ("Every story above happened or was first reported on "
          "Thursday 26 November 2026. Kyiv: night of 25–26 Nov, "
          "26 Nov Kyiv time. Bogor: 23 Nov collapse, search "
          "resumed 26 Nov.")
FOOTER2 = ("All times UTC. Tolls and claims are attributed where "
           "disputed. Map and drawings are original vector art.")
FOOTER_SOURCES = ("Sources: Reuters · AP · AFP · PIB · ABS · Bank of "
                  "Korea · ECB · TfL · FIDE · Roscosmos · UNCTAD · WHO")

# Pins: (story, lon, lat, pin_dx, pin_dy). Stories 12, 13, 59, 77
# are orbital, multi-market or global and carry no pin.
PINS = [
    (1, 4.4, 50.8, 0, 0), (2, 34.4, 31.4, -6, 8), (3, 127.0, 37.5, 0, 0),
    (4, 4.4, 50.8, 9, -8), (5, -0.12, 51.5, -8, -6), (6, 6.1, 46.2, 0, 6),
    (7, 36.2, 50.0, 0, 0), (8, 47.9, 29.4, 0, 0), (9, 42.6, 16.9, 0, 0),
    (10, -83.0, 42.3, 0, 0), (11, 77.2, 28.6, 0, 0),
    (14, 139.7, 35.7, 0, 0), (15, 102.0, 27.9, 0, 0),
    (16, 72.9, 19.1, 0, 0), (17, 77.2, 28.6, 11, -8),
    (18, 77.2, 28.6, -11, 8), (19, 51.5, 25.3, 0, 0),
    (20, 77.2, 28.6, 11, 9), (21, 120.9, 31.3, 0, 0),
    (22, 116.4, 39.9, 0, 0), (23, 116.4, 39.9, -12, -9),
    (24, 139.7, 35.7, 11, -8), (25, 116.4, 39.9, 12, 9),
    (26, 114.1, 22.5, 0, 0), (27, 106.8, -6.6, 0, 0),
    (28, 73.0, 33.7, 0, 0), (29, 139.7, 35.7, -11, 9),
    (30, 149.1, -35.3, 0, 0), (31, 149.1, -35.3, -13, -9),
    (32, 149.1, -35.3, 13, -9), (33, 149.1, -35.3, -12, 10),
    (34, 178.3, -37.5, 0, 0), (35, 151.2, -33.9, 0, 0),
    (36, 168.3, -17.7, 0, 0), (37, 174.8, -41.3, 0, 0),
    (38, 151.2, -33.9, 12, 10), (39, 174.8, -36.8, 0, 0),
    (40, 151.2, -33.9, -13, 12), (41, 145.0, -37.8, 0, 0),
    (42, 149.1, -35.3, 12, 11), (43, 153.0, -27.5, 0, 0),
    (44, 149.1, -35.3, -13, -2), (45, 30.5, 50.4, 0, 0),
    (46, 39.7, 54.6, 0, 0), (47, 2.35, 48.9, 0, 0),
    (48, 2.35, 48.9, 11, -9), (49, -0.12, 51.5, 9, 8),
    (50, 8.7, 50.1, 0, 0), (51, 13.4, 52.5, 0, 0),
    (52, 13.4, 52.5, 10, -9), (53, 7.8, 48.6, 0, 0),
    (54, 23.7, 38.0, 0, 0), (55, 26.1, 44.4, 0, 0),
    (56, 30.7, 46.5, 0, 0), (57, 4.9, 52.4, 0, 0),
    (58, 8.7, 50.1, 11, 8), (60, -86.3, 32.4, 0, 0),
    (61, -75.0, 38.5, 0, 0), (62, -58.4, -34.6, 0, 0),
    (63, -80.0, 26.8, 0, 0), (64, -58.4, -34.6, 11, 9),
    (65, -74.0, 40.7, 0, 0), (66, -117.2, 32.7, 0, 0),
    (67, 28.5, 11.5, 0, 0), (68, 36.4, -0.8, 0, 0),
    (69, 36.8, -1.3, 0, 0), (70, 39.3, -6.8, 0, 0),
    (71, 31.0, -29.9, 0, 0), (72, 30.1, -1.9, 0, 0),
    (73, 22.0, -3.0, 0, 0), (74, 55.3, 25.3, 0, 0),
    (75, 6.1, 46.2, 11, -8), (76, 6.1, 46.2, -11, 9),
    (78, -72.3, 18.5, 0, 0),
]

# Rebuild v2 (27 Nov): the 60 strongest verified stories across
# 11 fine regions, defined in stories.py beside this file. These
# names override the v1 78-story tables above.
from stories import (STORIES, HEROES as _H, HERO_CONF as _HC,
                     GRID as _G, GRID_CONF as _GC,
                     GRID_BANNER as _GB, ALSO as _A,
                     REGIONS as _R, FIELDS as _F, PINS as _P,
                     ALSO_CLAIM as _AC, NO_PIN,
                     REGION_NAMES as _RN, REGION_SHORT)
HEROES, HERO_CONF = _H, _HC
GRID, GRID_CONF, GRID_BANNER = _G, _GC, _GB
ALSO, REGIONS, FIELDS, PINS, ALSO_CLAIM = _A, _R, _F, _P, _AC
REGION_NAMES = _RN
REGION_COLORS = [NAVY, (90, 140, 60), BURGUNDY, (200, 110, 40),
                 (140, 60, 90), (160, 90, 30), (40, 120, 110),
                 (70, 160, 90), (30, 90, 160), TEAL, (110, 80, 140)]
FOOTER = ("The 60 strongest of 78 verified stories, all first "
          "reported on Thursday 26 November 2026. Kyiv: night of "
          "25–26 Nov, 26 Nov Kyiv time. Bogor: 23 Nov collapse, "
          "search resumed 26 Nov.")


# Coarse land rectangles (lon_min, lon_max, lat_min, lat_max).
LAND = [
    (-168, -140, 60, 71), (-140, -125, 58, 70), (-125, -110, 52, 70),
    (-110, -95, 48, 69), (-95, -82, 46, 68), (-82, -75, 50, 66),
    (-75, -65, 46, 62), (-65, -55, 46, 52), (-80, -70, 40, 47),
    (-76, -70, 36, 41), (-81, -75, 31, 37), (-81, -80, 25, 31),
    (-90, -81, 29, 31), (-97, -90, 26, 30), (-97, -94, 18, 26),
    (-92, -87, 14, 22), (-87, -83, 9, 16), (-83, -78, 8, 10),
    (-105, -97, 16, 24), (-112, -105, 20, 30), (-117, -112, 32, 42),
    (-124, -117, 35, 48), (-130, -124, 48, 56), (-140, -130, 56, 60),
    (-158, -140, 58, 62), (-168, -158, 60, 65),
    (-58, -45, 60, 70), (-45, -32, 68, 76), (-35, -21, 74, 80),
    (-58, -52, 70, 78),
    (-80, -72, 4, 10), (-72, -64, 8, 12), (-64, -55, 5, 9),
    (-55, -50, 0, 6), (-50, -44, -3, 1), (-44, -35, -9, -2),
    (-40, -35, -14, -8), (-41, -39, -22, -14), (-48, -41, -27, -20),
    (-53, -48, -34, -27), (-58, -53, -39, -34), (-64, -58, -42, -38),
    (-67, -64, -50, -42), (-70, -67, -54, -50), (-74, -70, -50, -38),
    (-73, -71, -38, -30), (-71, -69, -30, -19), (-70, -69, -19, -15),
    (-77, -70, -15, -8), (-81, -77, -6, 1), (-78, -75, 1, 7),
    (-17, -10, 15, 28), (-10, -6, 28, 35), (-6, 0, 32, 36),
    (0, 10, 34, 37), (10, 20, 30, 34), (20, 30, 30, 32),
    (30, 34, 22, 31), (34, 38, 15, 22), (38, 43, 11, 15),
    (43, 51, 11, 12), (48, 51, 5, 11), (42, 48, -3, 5),
    (40, 42, -10, -3), (39, 40, -17, -10), (36, 39, -22, -17),
    (34, 36, -27, -22), (31, 34, -29, -26), (27, 31, -34, -29),
    (20, 27, -35, -33), (17, 20, -32, -27), (14, 17, -27, -19),
    (12, 14, -19, -12), (10, 12, -12, -5), (9, 10, -5, 3),
    (6, 9, 3, 5), (1, 6, 5, 6), (-4, 1, 4, 6), (-9, -4, 4, 5),
    (-13, -9, 7, 9), (-17, -13, 9, 15),
    (-10, -2, 37, 44), (-5, 0, 44, 49), (-2, 4, 49, 52),
    (4, 8, 52, 55), (8, 12, 54, 58), (5, 10, 58, 63),
    (10, 18, 63, 69), (18, 28, 69, 71), (24, 32, 64, 70),
    (12, 21, 55, 57), (21, 28, 57, 61), (28, 32, 60, 64),
    (0, 8, 42, 46), (8, 14, 42, 46), (14, 20, 40, 46),
    (20, 28, 39, 46), (23, 28, 36, 40), (19, 23, 40, 43),
    (12, 16, 38, 42), (16, 19, 38, 41),
    (28, 45, 45, 55), (45, 60, 48, 56), (60, 75, 50, 58),
    (75, 90, 50, 60), (90, 105, 48, 58), (105, 120, 45, 55),
    (120, 135, 42, 52), (135, 142, 45, 55), (142, 150, 52, 60),
    (150, 158, 59, 65), (158, 170, 60, 69), (170, 180, 64, 69),
    (35, 50, 55, 68), (50, 68, 58, 69), (68, 85, 62, 73),
    (85, 105, 66, 76), (105, 125, 68, 73), (125, 145, 69, 72),
    (145, 160, 68, 70), (160, 178, 66, 69), (60, 75, 40, 50),
    (75, 90, 42, 50), (90, 105, 40, 48), (105, 120, 38, 45),
    (120, 130, 38, 43), (127, 130, 34, 39), (121, 123, 28, 32),
    (110, 122, 20, 28), (100, 110, 18, 24), (95, 100, 15, 22),
    (92, 95, 16, 22), (88, 92, 21, 26), (80, 88, 15, 22),
    (77, 80, 8, 15), (72, 77, 15, 22), (66, 72, 23, 28),
    (61, 66, 25, 28), (57, 61, 26, 28), (48, 57, 29, 38),
    (44, 48, 29, 38), (36, 44, 31, 37), (34, 36, 28, 32),
    (39, 43, 12, 22), (43, 48, 12, 16), (48, 55, 15, 18),
    (55, 59, 17, 24), (59, 61, 22, 25), (98, 100, 6, 15),
    (100, 103, 2, 7), (103, 107, 5, 12), (107, 110, 11, 18),
    (110, 114, 18, 21), (114, 118, 21, 24), (118, 121, 24, 28),
    (122, 124, 30, 32), (124, 127, 34, 38), (130, 132, 41, 44),
    (132, 136, 43, 46), (136, 139, 45, 48), (139, 141, 48, 52),
    (141, 143, 50, 54), (143, 145, 54, 59), (150, 156, 52, 60),
    (156, 160, 52, 56),
    (130, 132, 31, 34), (132, 135, 33, 35), (135, 138, 34, 36),
    (138, 140, 36, 38), (140, 142, 38, 41), (141, 142, 41, 44),
    (95, 100, 2, 6), (100, 105, -2, 2), (105, 110, -7, -5),
    (110, 114, -8, -6), (109, 113, -1, 2), (113, 117, -3, 1),
    (117, 120, -4, 0), (119, 123, -5, -1), (123, 127, -3, 0),
    (127, 131, -2, 1), (131, 136, -3, -1), (136, 141, -4, -2),
    (141, 146, -5, -3), (146, 150, -7, -5),
    (120, 122, 12, 18), (122, 124, 7, 13), (124, 126, 6, 10),
    (113, 120, -22, -12), (120, 127, -20, -12), (127, 135, -16, -12),
    (135, 142, -15, -11), (142, 146, -11, -15), (146, 150, -19, -15),
    (150, 153, -27, -19), (153, 154, -33, -27), (150, 153, -38, -33),
    (147, 150, -38, -37), (141, 147, -39, -38), (138, 141, -38, -35),
    (135, 138, -35, -33), (129, 135, -32, -31), (124, 129, -34, -32),
    (118, 124, -35, -34), (115, 118, -35, -32), (113, 115, -28, -22),
    (114, 117, -22, -21), (122, 126, -17, -16), (126, 129, -15, -14),
    (130, 133, -13, -12), (136, 139, -12, -11), (141, 143, -13, -12),
    (145, 147, -15, -14), (147, 149, -19, -18), (149, 151, -24, -22),
    (151, 153, -28, -26), (145, 148, -38, -37), (147, 148, -43, -40),
    (167, 169, -46, -44), (169, 172, -44, -42), (172, 174, -42, -40),
    (174, 176, -40, -38), (176, 178, -38, -36), (173, 175, -36, -34),
]


def _is_land(lon, lat):
    for (a, b, c0, d) in LAND:
        if a <= lon <= b and c0 <= lat <= d:
            return True
    return False


def draw_map(c, x, y, w, h, pins):
    """Dotted world map with numbered pins."""
    c.rect(x, y, w, h, (251, 248, 240))
    c.frame(x, y, w, h, HAIR, 1)
    lon0, lon1, lat0, lat1 = -180, 180, 76, -68

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    lon = lon0 + 2
    while lon < lon1:
        lat = lat0 - 2
        while lat > lat1:
            if _is_land(lon, lat):
                px, py = proj(lon, lat)
                c.circle(px, py, 1.25, (96, 112, 138))
            lat -= 4.5
        lon += 4
    # Dense clusters (Europe, SE Australia) would stack pins on top of
    # each other at true positions, so their pins go on a ring around
    # the cluster with a thin leader line back to the true point.
    def cluster_of(plon, plat):
        if -12 <= plon <= 42 and 34 <= plat <= 60:
            return "EU"
        if 112 <= plon <= 156 and -40 <= plat <= -10:
            return "AU"
        return None

    placed = {}
    for name in ("EU", "AU"):
        members = [p for p in pins if cluster_of(p[1], p[2]) == name]
        if not members:
            continue
        pts = [proj(p[1], p[2]) for p in members]
        cx = sum(q[0] for q in pts) / len(pts)
        cy = sum(q[1] for q in pts) / len(pts)
        rx, ry = (58, 34) if name == "EU" else (50, 28)
        members.sort(key=lambda p: math.atan2(proj(p[1], p[2])[1] - cy,
                                              proj(p[1], p[2])[0] - cx))
        for k, p in enumerate(members):
            ang = -math.pi / 2 + 2 * math.pi * k / len(members)
            qx = min(max(cx + rx * math.cos(ang), x + 7), x + w - 7)
            qy = min(max(cy + ry * math.sin(ang), y + 7), y + h - 7)
            placed[p[0]] = (qx, qy)
    for (num, plon, plat, pdx, pdy) in pins:
        tx, ty = proj(plon, plat)
        if num in placed:
            px, py = placed[num]
            c.line(tx, ty, px, py, (150, 140, 120), 0.6)
            c.circle(tx, ty, 1.2, BURGUNDY)
        else:
            px, py = tx + pdx, ty + pdy
        c.circle(px, py, 5, BURGUNDY)
        c.ring(px, py, 5, WHITE, 1)
        c.text_center(px, py + 2.5, str(num), SANSB, SANSB_EM, SANSB_ASC,
                      7, WHITE)


# ---------------------------------------------------------------- layout
def region_counts():
    counts = [0] * len(REGION_NAMES)
    for r in REGIONS:
        counts[r] += 1
    return counts


def draw_top_strip(c):
    c.rect(0, 0, W, 20, NAVY)
    c.text(24, 14, "THE WORLD IN ONE DAY", SANSB, SANSB_EM, SANSB_ASC,
           8, PAPER, tracking=1.2)
    nfields = len(set(FIELDS))
    c.text_right(W - 24, 14,
                 "%d STORIES · %d REGIONS · %d FIELDS · "
                 "THURSDAY 26 NOVEMBER 2026"
                 % (len(FIELDS), len(REGION_NAMES), nfields),
                 SANSB, SANSB_EM, SANSB_ASC, 8, PAPER, tracking=0.8)


def draw_masthead(c):
    c.text_center(W // 2, 68, "Thursday 26 November 2026", SERIF,
                  SERIF_EM, SERIF_ASC, 40, INK)
    c.text_center(W // 2, 88, SUBHEAD, SERIFR, SERIFR_EM, SERIFR_ASC,
                  13, BURGUNDY)


def draw_region_strip(c):
    counts = region_counts()
    total = sum(counts)
    x = 24.0
    y, h = 96, 14
    for i, name in enumerate(REGION_NAMES):
        wseg = (W - 48) * counts[i] / total
        col = REGION_COLORS[i]
        c.rect(x, y, wseg, h, col)
        tc = INK if col == GOLD else WHITE
        label = "%s %d" % (REGION_SHORT[i], counts[i])
        if text_width(label, SANSB, SANSB_EM, 6.2, 0.1) <= wseg - 4:
            c.text_center(x + wseg / 2, y + 10.5, label,
                          SANSB, SANSB_EM, SANSB_ASC, 6.2, tc,
                          tracking=0.1)
        x += wseg
    fcounts = {}
    for f in FIELDS:
        fcounts[f] = fcounts.get(f, 0) + 1
    ranked = sorted(fcounts.items(), key=lambda kv: (-kv[1], kv[0]))
    line = "%d FIELDS · " % len(fcounts) + " · ".join(
        "%s %d" % (name, n) for (name, n) in ranked)
    c.text_center(W // 2, 124, line, SANSB, SANSB_EM, SANSB_ASC, 6.4, INK)


def draw_stats(c):
    y, h = 132, 48
    c.hline(0, y, W, INK, 2)
    c.hline(0, y + 3, W, GOLD, 0.8)
    c.hline(0, y + h - 3, W, GOLD, 0.8)
    c.hline(0, y + h - 2, W, INK, 2)
    cw = W // 5
    for i, (num, label) in enumerate(STATS):
        x0 = i * cw
        if i:
            c.vline(x0, y + 8, h - 16, HAIR, 1)
        c.text_center(x0 + cw // 2, y + 29, num, SERIF, SERIF_EM,
                      SERIF_ASC, 24, NAVY)
        c.text_center(x0 + cw // 2, y + 43, label, SANSB, SANSB_EM,
                      SANSB_ASC, 8.2, GREY, tracking=0.6)


def draw_conf_badge(c, right, y, text):
    col = NAVY if text == "OFFICIAL" else GREY
    w = text_width(text, SANSB, SANSB_EM, 7.5, 0.8) + 12
    c.rect(right - w, y, w, 13, col)
    c.text_center(right - w / 2, y + 10, text, SANSB, SANSB_EM,
                  SANSB_ASC, 7.5, WHITE, tracking=0.8)
    return w


def draw_hero(c, x, y, w, h, num, hero):
    scene, place, cat, headline, summary, source, chip, _hour = hero
    c.rect(x, y, w, h, WHITE)
    c.frame(x, y, w, h, HAIR, 1)
    c.hline(x, y, w, BURGUNDY, 3)
    SCENES[scene](c, x + 2, y + 5, w - 4, 80)
    c.rect(x + 2, y + 5, 26, 26, NAVY)
    c.text_center(x + 15, y + 26, str(num), SERIF, SERIF_EM, SERIF_ASC,
                  17, WHITE)
    cw_ = text_width(chip, SANSB, SANSB_EM, 8.5, 0.6) + 12
    c.rect(x + w - 2 - cw_, y + 5, cw_, 16, BURGUNDY)
    c.text_center(x + w - 2 - cw_ / 2, y + 17, chip, SANSB, SANSB_EM,
                  SANSB_ASC, 8.5, WHITE, tracking=0.6)
    ty = y + 96
    c.text(x + 12, ty, place + " · " + cat, SANSB, SANSB_EM, SANSB_ASC,
           9.5, BURGUNDY, tracking=1.0)
    draw_conf_badge(c, x + w - 12, ty - 9, HERO_CONF[num - 1])
    ty = c.para(x + 12, ty + 17, headline, SERIF, SERIF_EM, SERIF_ASC,
                16, INK, w - 24, leading=18)
    ty = c.para(x + 12, ty + 1, summary, SERIFR, SERIFR_EM, SERIFR_ASC,
                11, INK, w - 24, leading=13)
    wx = c.text(x + 12, ty + 3, "WHY IT MATTERS ", SANSB, SANSB_EM,
                SANSB_ASC, 8, BURGUNDY, tracking=0.4)
    c.text(wx, ty + 3, HERO_WHY[num - 1], SERIFR, SERIFR_EM, SERIFR_ASC,
           10.5, INK)
    c.text(x + 12, y + h - 10, source, SANSB, SANSB_EM, SANSB_ASC, 8.5,
           GREY, tracking=0.8)


def draw_grid_card(c, x, y, w, h, num, item):
    icon, place, cat, headline, summary, source = item
    c.rect(x, y, w, h, WHITE)
    c.frame(x, y, w, h, HAIR, 1)
    # illustrated banner scene in the story's region tint
    rcol = REGION_COLORS[REGIONS[num - 1]]
    draw_banner_scene(c, x + 1, y + 1, w - 2, 33, icon, rcol)
    c.hline(x + 1, y + 34, w - 2, rcol, 1.6)
    c.rect(x + 3, y + 3, 24, 24, NAVY)
    c.text_center(x + 15, y + 20, str(num), SERIF, SERIF_EM, SERIF_ASC,
                  13, WHITE)
    banner = GRID_BANNER[num - 4]
    bw = text_width(banner, SANSB, SANSB_EM, 6.5, 0.4) + 10
    c.rect(x + w - 6 - bw, y + 10, bw, 12, INK)
    c.text_center(x + w - 6 - bw / 2, y + 19, banner, SANSB, SANSB_EM,
                  SANSB_ASC, 6.5, WHITE, tracking=0.4)
    c.text(x + 10, y + 48, place + " · " + cat, SANSB, SANSB_EM,
           SANSB_ASC, 8, BURGUNDY, tracking=0.3)
    ty = c.para(x + 10, y + 62, headline, SERIF, SERIF_EM, SERIF_ASC,
                11.5, INK, w - 20, leading=12.5)
    c.para(x + 10, ty + 1, summary, SERIFR, SERIFR_EM, SERIFR_ASC, 9,
           INK, w - 20, leading=10.5)
    sx = c.text(x + 10, y + h - 6, source, SANSB, SANSB_EM, SANSB_ASC,
                7.5, GREY, tracking=0.4)
    conf = GRID_CONF[num - 4]
    letter = {"OFFICIAL": "C", "REPORTED": "R", "CLAIM": "CL"}[conf]
    ccol = NAVY if conf == "OFFICIAL" else GREY
    lw = text_width(letter, SANSB, SANSB_EM, 7, 0) + 8
    c.rect(sx + 5, y + h - 14, lw, 11, ccol)
    c.text_center(sx + 5 + lw / 2, y + h - 5.5, letter, SANSB,
                  SANSB_EM, SANSB_ASC, 7, WHITE)


def draw_bottom(c):
    counts = region_counts()
    c.text(24, 666, "WHERE IT HAPPENED", SANSB, SANSB_EM, SANSB_ASC, 11,
           INK, tracking=1.2)
    c.text_right(384, 666, "dots = story numbers", SANSB, SANSB_EM,
                 SANSB_ASC, 8.5, GREY)
    draw_map(c, 24, 674, 360, 124, PINS)
    c.text(24, 812, "BY REGION", SANSB, SANSB_EM, SANSB_ASC, 9, NAVY,
           tracking=1.0)
    c.text(96, 812, "Nos. %s no pin"
           % ", ".join(str(n) for n in NO_PIN), SANS, SANS_EM,
           SANS_ASC, 8, GREY)
    for i, name in enumerate(REGION_NAMES):
        lx = 24 if i < 6 else 204
        ry = 824 + (i % 6) * 11
        c.rect(lx, ry - 7, 9, 9, REGION_COLORS[i])
        c.text(lx + 14, ry, "%s — %d" % (name, counts[i]), SANS, SANS_EM,
               SANS_ASC, 8.5, INK)
    c.text(24, 896, "ALL FIRST REPORTED THURSDAY 26 NOVEMBER 2026",
           SANSB, SANSB_EM, SANSB_ASC, 8.5, NAVY, tracking=0.8)
    c.para(24, 910, "%d stories, %d regions, %d fields. Every story "
           "happened or was first reported on Thursday 26 November "
           "2026 (any time zone, shown in UTC)."
           % (len(FIELDS), len(REGION_NAMES), len(set(FIELDS))),
           SANS, SANS_EM, SANS_ASC, 8, INK, 360, leading=10)
    c.text(400, 666, "ALSO ON THURSDAY 26 NOVEMBER", SANSB, SANSB_EM,
           SANSB_ASC, 11, INK, tracking=1.2)
    c.text_right(W - 24, 666, "%d more verified stories" % len(ALSO),
                 SANSB, SANSB_EM, SANSB_ASC, 9, GREY)
    c.hline(400, 672, W - 424, HAIR, 0.8)
    cols = [400, 706]
    rows = [23, 22]
    i = 0
    for ci, nrows in enumerate(rows):
        for r in range(nrows):
            place, head = ALSO[i]
            num = i + 16
            i += 1
            x0 = cols[ci]
            yy = 686 + r * 9.3
            c.text(x0, yy, str(num), SANSB, SANSB_EM, SANSB_ASC, 8.0,
                   BURGUNDY)
            pcol = REGION_COLORS[REGIONS[num - 1]]
            if pcol == GOLD:
                pcol = (150, 115, 20)
            nx = c.text(x0 + 22, yy, place + ": ", SANSB, SANSB_EM,
                        SANSB_ASC, 8.0, pcol)
            hx = c.text(nx, yy, head, SANS, SANS_EM, SANS_ASC, 8.0, INK)
            if num in ALSO_CLAIM:
                c.text(hx + 4, yy, "CLAIM", SANSB, SANSB_EM, SANSB_ASC,
                       7.2, BURGUNDY)


def draw_datecheck(c):
    y, h = 932, 46
    c.rect(24, y, W - 48, h, CREAM2)
    c.frame(24, y, W - 48, h, BURGUNDY, 1.5)
    c.text(36, y + 16, "DATE CHECK", SERIF, SERIF_EM, SERIF_ASC, 13,
           BURGUNDY)
    c.para(36, y + 26, FOOTER, SANS, SANS_EM, SANS_ASC, 7.8, INK, 308,
           leading=8.6)
    colw = 318
    for i, item in enumerate(DATE_CHECK):
        col = i // 4
        row = i % 4
        ix = 362 + col * colw
        iy = y + 11 + row * 10.2
        c.text(ix, iy, "X", SANSB, SANSB_EM, SANSB_ASC, 8.4, BURGUNDY)
        c.text(ix + 12, iy, item, SANS, SANS_EM, SANS_ASC, 8.4, INK)


def draw_footer(c):
    c.text_center(W // 2, 992,
                  "OFFICIAL = official record · REPORTED = wire report "
                  "· CLAIM = one side's statement · C/R on grid cards",
                  SANSB, SANSB_EM, SANSB_ASC, 8.6, GREY)
    c.text_center(W // 2, 1004, FOOTER2, SANS, SANS_EM, SANS_ASC, 9,
                  GREY)
    c.text_center(W // 2, 1016, FOOTER_SOURCES, SANSB, SANSB_EM,
                  SANSB_ASC, 8.2, INK, tracking=0.2)


def _validate():
    """Fail loudly if any rendered character is missing from a font,
    any text would overflow its card, or the story numbering is off.
    Runs before drawing, so a bad string can never reach the image."""
    fonts = [SERIF, SERIFR, SANSB, SANS]
    fcounts = {}
    for _f in FIELDS:
        fcounts[_f] = fcounts.get(_f, 0) + 1
    ranked = sorted(fcounts.items(), key=lambda kv: (-kv[1], kv[0]))
    fields_line = "%d FIELDS · " % len(fcounts) + " · ".join(
        "%s %d" % (name, n) for (name, n) in ranked)
    top_right = ("%d STORIES · %d REGIONS · %d FIELDS · "
                 "THURSDAY 26 NOVEMBER 2026"
                 % (len(FIELDS), len(REGION_NAMES), len(fcounts)))
    strings = ["THE WORLD IN ONE DAY", top_right,
               "Thursday 26 November 2026", SUBHEAD, fields_line,
               "ALSO ON THURSDAY 26 NOVEMBER",
               "%d more verified stories" % len(ALSO),
               "WHERE IT HAPPENED", "dots = story numbers", "BY REGION",
               "Nos. %s no pin" % ", ".join(str(n) for n in NO_PIN),
               "DATE CHECK",
               "ALL FIRST REPORTED THURSDAY 26 NOVEMBER 2026",
               "%d stories, %d regions, %d fields. Every story "
               "happened or was first reported on Thursday 26 "
               "November 2026 (any time zone, shown in UTC)."
               % (len(FIELDS), len(REGION_NAMES), len(fcounts)),
               "X", "WHY IT MATTERS ", "CLAIM", "C", "R", "%",
               "OFFICIAL = official record · REPORTED = wire report "
               "· CLAIM = one side's statement · C/R on grid cards",
               FOOTER, FOOTER2, FOOTER_SOURCES]
    strings += DATE_CHECK + HERO_WHY + GRID_BANNER
    strings += HERO_CONF + GRID_CONF
    strings += [str(n) for n in range(1, 61)]
    for (_sc, place, cat, head, summ, src, chip, _h) in HEROES:
        strings += [place, cat, head, summ, src, chip]
    for (num, label) in STATS:
        strings += [num, label]
    for (_ic, place, cat, head, summ, src) in GRID:
        strings += [place, cat, head, summ, src]
    for (place, head) in ALSO:
        strings += [place + ": ", head]
    for i, name in enumerate(REGION_NAMES):
        strings.append("%s — %d" % (name, region_counts()[i]))
        strings.append("%s %d" % (name, region_counts()[i]))
    for s in strings:
        assert "…" not in s, "ellipsis in %r" % s
        for ch in s:
            for f in fonts:
                assert ch in f, "char %r missing from a font" % ch
    for (_sc, _p, _c, head, summ, _src, _chip, _h) in HEROES:
        assert len(wrap_text(head, SERIF, SERIF_EM, 16, 304)) <= 2, head
        assert len(wrap_text(summ, SERIFR, SERIFR_EM, 10.5, 304)) <= 3, summ
    for why in HERO_WHY:
        assert text_width("WHY IT MATTERS ", SANSB, SANSB_EM, 7.5, 0.4) + \
            text_width(why, SERIFR, SERIFR_EM, 10) <= 304, why
    for gi, (_ic, _p, _c, head, summ, _src) in enumerate(GRID):
        assert len(wrap_text(head, SERIF, SERIF_EM, 11.5, 140)) <= 3, head
        assert text_width(GRID_BANNER[gi], SANSB, SANSB_EM, 6.5, 0.4) \
            <= 70, GRID_BANNER[gi]
        assert len(wrap_text(summ, SERIFR, SERIFR_EM, 9, 140)) <= 2, summ
    for (place, head) in ALSO:
        line = place + ": " + head
        assert text_width(line, SANSB, SANSB_EM, 7.4) <= 272, line
    for (_num, label) in STATS:
        assert text_width(label, SANS, SANS_EM, 7.5, 0.6) <= 204, label
    total = sum(region_counts())
    for i, name in enumerate(REGION_NAMES):
        seg = (W - 48) * region_counts()[i] / total
        label = "%s %d" % (REGION_SHORT[i], region_counts()[i])
        if text_width(label, SANSB, SANSB_EM, 6.2, 0.1) > seg - 4:
            assert seg < 60, name  # tiny segments carry no label
    assert text_width(FOOTER_SOURCES, SANSB, SANSB_EM, 7.5, 0.2) <= CW
    assert text_width(fields_line, SANSB, SANSB_EM, 6.4) <= CW
    assert text_width(top_right, SANSB, SANSB_EM, 8, 0.8) <= 720
    assert text_width("Thursday 26 November 2026", SERIF, SERIF_EM,
                      40) <= CW
    assert text_width(SUBHEAD, SERIFR, SERIFR_EM, 12.5) <= CW
    assert len(wrap_text(FOOTER, SANS, SANS_EM, 7.8, 308)) <= 3
    for item in DATE_CHECK:
        assert text_width(item, SANS, SANS_EM, 8) <= 300, item
    assert len(FIELDS) == 60 and len(REGIONS) == 60
    assert len(HERO_WHY) == 3 and len(GRID_BANNER) == 12
    assert all(v in ("OFFICIAL", "REPORTED", "CLAIM")
               for v in HERO_CONF + GRID_CONF)
    assert len(HEROES) == 3 and len(GRID) == 12 and len(ALSO) == 45
    assert len(PINS) == 57 and len(DATE_CHECK) == 8
    assert sum(region_counts()) == 60
    assert len(REGION_NAMES) == 11 and all(
        n > 0 for n in region_counts())
    assert all(p[0] not in NO_PIN for p in PINS)
    assert len(set(p[0] for p in PINS)) == len(PINS)


def build():
    c = Canvas(W, H, PAPER)
    draw_top_strip(c)
    draw_masthead(c)
    draw_region_strip(c)
    draw_stats(c)
    for i, hero in enumerate(HEROES):
        draw_hero(c, 12 + i * 336, 186, 328, 200, i + 1, hero)
    for i, item in enumerate(GRID):
        gx = 12 + (i % 6) * 168
        gy = 392 + (i // 6) * 134
        draw_grid_card(c, gx, gy, 160, 128, i + 4, item)
    draw_bottom(c)
    draw_datecheck(c)
    draw_footer(c)
    return c


def main():
    _validate()
    canvas = build()
    data = png_bytes(canvas.downsample())
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "entry.png")
        with open(path, "wb") as f:
            f.write(data)
    except OSError:
        os.makedirs("out", exist_ok=True)
        path = os.path.join("out", "entry.png")
        with open(path, "wb") as f:
            f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
