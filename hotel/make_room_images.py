"""
make_room_images.py — draws one DIFFERENT illustrated picture for each of the 13 rooms into ./images/<room>.jpg.

Run it once:   python make_room_images.py
The app always prefers a local file in ./images over the web photo, so these pictures replace the repeated
Unsplash photos. To use a real photo for a room, just overwrite images/<room name in lowercase>.jpg.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
W, H, S = 800, 500, 2          # final size and supersampling factor
FLOOR_Y = 330                  # where the wall ends and the floor starts (in final pixels)

# name: dict(wall=(top, bottom), floor, bed=(blanket, headboard), window=(x, w, scene), beds, extras)
ROOMS = {
    "luxe":      dict(wall=((226, 208, 178), (208, 186, 152)), floor=(120, 84, 56), bed=((176, 58, 58), (92, 60, 40)),
                      window=(520, 190, "city"), beds="king", extras=["tv", "lamp", "plant"]),
    "elysian":   dict(wall=((176, 192, 208), (150, 168, 188)), floor=(96, 84, 74), bed=((52, 92, 140), (60, 66, 78)),
                      window=(500, 220, "city"), beds="queen", extras=["desk", "lamp", "coffee"]),
    "velvet":    dict(wall=((196, 150, 150), (172, 120, 124)), floor=(88, 62, 52), bed=((120, 28, 56), (70, 30, 40)),
                      window=(560, 150, "dusk"), beds="twin", extras=["tub", "painting"]),
    "emerald":   dict(wall=((176, 206, 184), (146, 184, 158)), floor=(130, 104, 74), bed=((30, 110, 84), (76, 60, 44)),
                      window=(420, 300, "garden"), beds="king", extras=["plant", "lamp"]),
    "silk":      dict(wall=((238, 226, 204), (222, 206, 178)), floor=(150, 124, 96), bed=((214, 178, 120), (140, 106, 70)),
                      window=(560, 150, "city"), beds="queen", extras=["minibar", "painting", "speaker"]),
    "elite":     dict(wall=((92, 100, 120), (68, 76, 96)), floor=(52, 48, 50), bed=((200, 168, 76), (36, 40, 56)),
                      window=(520, 190, "night"), beds="king", extras=["desk", "armchair", "lamp"]),
    "grand":     dict(wall=((214, 200, 182), (194, 178, 158)), floor=(112, 90, 70), bed=((84, 120, 150), (96, 76, 58)),
                      window=(560, 170, "city"), beds="double", extras=["sofa", "tv"]),
    "prestige":  dict(wall=((236, 230, 216), (218, 208, 188)), floor=(142, 116, 90), bed=((70, 100, 130), (110, 88, 66)),
                      window=(480, 240, "city"), beds="king", extras=["sofa", "plant"]),
    "imperial":  dict(wall=((60, 56, 84), (40, 38, 62)), floor=(36, 32, 40), bed=((150, 40, 70), (28, 26, 40)),
                      window=(300, 480, "night"), beds="king", extras=["jacuzzi", "wine", "lamp"]),
    "opulent":   dict(wall=((228, 212, 190), (206, 188, 162)), floor=(128, 98, 70), bed=((60, 84, 70), (92, 70, 50)),
                      window=(560, 160, "garden"), beds="queen", extras=["dining", "plant", "chandelier"]),
    "serene":    dict(wall=((252, 190, 120), (236, 142, 104)), floor=(188, 158, 130), bed=((246, 240, 230), (130, 96, 70)),
                      window=(300, 480, "terrace"), beds="king", extras=["plant", "lamp"]),
    "sapphire":  dict(wall=((30, 48, 96), (20, 32, 74)), floor=(24, 24, 40), bed=((20, 20, 30), (40, 60, 120)),
                      window=None, beds=None, extras=["cinema", "wine"]),
    "celestial": dict(wall=((22, 24, 52), (14, 14, 36)), floor=(30, 26, 34), bed=((232, 214, 170), (60, 52, 80)),
                      window=(60, 680, "skyline"), beds="king", extras=["chandelier", "sofa", "lamp"]),
}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, H * S))
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x, y, w, h, fill, r=0, outline=None):
        box = [x * S, y * S, (x + w) * S, (y + h) * S]
        if r:
            self.d.rounded_rectangle(box, r * S, fill=fill, outline=outline)
        else:
            self.d.rectangle(box, fill=fill, outline=outline)

    def ellipse(self, x, y, w, h, fill):
        self.d.ellipse([x * S, y * S, (x + w) * S, (y + h) * S], fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def vgrad(self, x, y, w, h, top, bottom):
        for i in range(h * S):
            self.d.line([(x * S, y * S + i), ((x + w) * S, y * S + i)], fill=lerp(top, bottom, i / max(1, h * S - 1)))


# ---------- window scenes ----------
def window(cv, x, w, scene, rng):
    y, h = 40, 230 if scene != "skyline" else 250
    if scene == "skyline":
        y, h = 30, 270
    cv.rect(x - 8, y - 8, w + 16, h + 16, (70, 56, 44), 3)
    skies = {"city": ((150, 200, 240), (222, 238, 250)), "garden": ((140, 200, 240), (214, 236, 250)),
             "night": ((14, 20, 50), (50, 60, 110)), "dusk": ((90, 70, 130), (250, 170, 120)),
             "terrace": ((255, 170, 100), (255, 224, 160)), "skyline": ((10, 12, 40), (60, 40, 90))}
    cv.vgrad(x, y, w, h, *skies[scene])
    if scene in ("night", "skyline", "dusk"):
        for _ in range(26 if scene != "dusk" else 8):
            sx, sy = x + rng.randint(4, w - 4), y + rng.randint(4, h // 2)
            cv.ellipse(sx, sy, 2, 2, (255, 255, 230))
    if scene == "terrace":
        cv.ellipse(x + w // 2 - 36, y + h - 130, 72, 72, (255, 238, 190))
        cv.rect(x, y + h - 62, w, 62, (70, 170, 190))                  # plunge pool
        cv.rect(x, y + h - 62, w, 6, (210, 200, 180))
    if scene in ("city", "night", "skyline", "dusk"):
        bx, base = x, y + h
        while bx < x + w:
            bw, bh = rng.randint(24, 48), rng.randint(40, int(h * 0.62))
            bw = min(bw, x + w - bx)
            col = (46, 52, 74) if scene != "city" else (110, 130, 158)
            cv.rect(bx, base - bh, bw, bh, col)
            for wy in range(base - bh + 6, base - 6, 12):
                for wx in range(bx + 4, bx + bw - 6, 9):
                    if scene != "city" and rng.random() < 0.55:
                        cv.rect(wx, wy, 4, 6, (255, 220, 120))
            bx += bw + 2
    if scene == "garden":
        cv.rect(x, y + h - 70, w, 70, (84, 150, 84))
        for tx in range(x + 20, x + w - 10, 54):
            cv.rect(tx + 8, y + h - 110, 6, 40, (96, 70, 44))
            cv.ellipse(tx - 6, y + h - 160, 36, 56, (44, 120, 62))
    cv.rect(x + w // 2 - 2, y, 4, h, (70, 56, 44))                      # window frame cross
    if scene != "skyline":
        cv.rect(x, y + h // 2, w, 3, (70, 56, 44))


# ---------- beds ----------
def bed(cv, x, y, w, blanket, head):
    cv.rect(x - 6, y - 70, w + 12, 100, head, 6)                       # headboard
    cv.rect(x, y - 6, w, 62, (240, 238, 232), 8)                        # mattress / sheet
    cv.rect(x, y + 14, w, 46, blanket, 8)                               # blanket
    cv.rect(x, y + 14, w, 8, shade(blanket, 1.25), 4)
    pw = w // 2 - 14
    for px in (x + 8, x + w - pw - 8):
        cv.rect(px, y - 22, pw, 30, (250, 249, 245), 10)
    cv.rect(x, y + 56, w, 12, shade(head, 0.8))                         # bed base


def beds(cv, kind, blanket, head):
    if kind == "king":
        bed(cv, 200, 300, 230, blanket, head)
    elif kind == "queen":
        bed(cv, 220, 300, 190, blanket, head)
    elif kind == "twin":
        bed(cv, 120, 300, 130, blanket, head)
        bed(cv, 290, 300, 130, shade(blanket, 1.15), head)
    elif kind == "double":
        bed(cv, 70, 300, 170, blanket, head)
        bed(cv, 270, 300, 170, shade(blanket, 1.15), head)


# ---------- extras ----------
def lamp(cv, x, y=270):
    cv.rect(x, y + 10, 6, 40, (90, 70, 50))
    cv.poly([(x - 14, y + 12), (x + 20, y + 12), (x + 12, y - 12), (x - 6, y - 12)], (255, 224, 150))


def extras(cv, names, floor):
    for n in names:
        if n == "lamp":
            lamp(cv, 150)
            lamp(cv, 470)
        elif n == "tv":
            cv.rect(60, 90, 150, 86, (18, 18, 22), 4)
            cv.rect(66, 96, 138, 74, (46, 84, 130), 2)
        elif n == "desk":
            cv.rect(560, 300, 190, 10, (110, 80, 54))
            cv.rect(566, 310, 8, 56, (80, 56, 40))
            cv.rect(736, 310, 8, 56, (80, 56, 40))
            cv.rect(620, 262, 56, 38, (30, 30, 34), 3)                   # laptop screen
            cv.rect(676, 340, 34, 54, (60, 56, 60), 6)                   # chair back
        elif n == "coffee":
            cv.rect(700, 276, 26, 24, (60, 60, 64), 3)
            cv.rect(706, 270, 14, 6, (180, 60, 50))
        elif n == "plant":
            cv.rect(724, 340, 28, 34, (150, 100, 70), 4)
            for ang in range(-3, 4):
                cv.ellipse(738 + ang * 10 - 8, 280 + abs(ang) * 8, 18, 60 - abs(ang) * 6, (52, 130, 70))
        elif n == "tub":
            cv.rect(580, 336, 190, 60, (246, 246, 244), 26)
            cv.rect(592, 346, 166, 38, (190, 224, 236), 18)
            cv.rect(748, 312, 6, 28, (190, 190, 196))
        elif n == "painting":
            cv.rect(80, 70, 90, 70, (86, 66, 48), 3)
            cv.rect(86, 76, 78, 58, (214, 168, 90), 2)
            cv.ellipse(100, 92, 36, 36, (200, 90, 70))
        elif n == "minibar":
            cv.rect(600, 290, 110, 100, (70, 54, 44), 4)
            cv.rect(608, 298, 94, 40, (44, 36, 32), 2)
            cv.rect(660, 344, 30, 40, (190, 210, 220), 2)
        elif n == "speaker":
            cv.rect(720, 258, 22, 34, (28, 28, 32), 6)
        elif n == "armchair":
            cv.rect(580, 320, 80, 70, (150, 52, 52), 14)
            cv.rect(572, 340, 20, 50, (130, 40, 40), 8)
            cv.rect(648, 340, 20, 50, (130, 40, 40), 8)
        elif n == "sofa":
            cv.rect(520, 330, 240, 64, (122, 100, 84), 16)
            cv.rect(520, 306, 240, 34, (140, 116, 98), 12)
            for sx in (540, 640):
                cv.rect(sx, 340, 100, 34, (150, 126, 108), 10)
        elif n == "jacuzzi":
            cv.ellipse(540, 360, 220, 90, (230, 232, 238))
            cv.ellipse(556, 370, 188, 66, (80, 180, 210))
            for bx, by in ((600, 380), (640, 392), (690, 376)):
                cv.ellipse(bx, by, 8, 8, (210, 240, 250))
        elif n == "wine":
            cv.rect(40, 250, 50, 150, (70, 44, 36), 4)
            for r in range(5):
                for c in range(2):
                    cv.ellipse(48 + c * 20, 262 + r * 26, 14, 14, (130, 40, 56))
        elif n == "dining":
            cv.ellipse(500, 360, 220, 56, (96, 66, 44))
            cv.rect(600, 380, 10, 38, (70, 50, 36))
            for cx in (500, 560, 650, 700):
                cv.rect(cx, 340, 30, 40, (150, 120, 90), 6)
        elif n == "chandelier":
            cv.rect(398, 0, 4, 40, (210, 190, 120))
            cv.ellipse(350, 36, 100, 18, (230, 200, 120))
            for cx in range(356, 440, 18):
                cv.ellipse(cx, 52, 8, 22, (255, 240, 190))
        elif n == "cinema":
            cv.rect(100, 40, 600, 220, (10, 10, 16), 6)
            cv.vgrad(110, 50, 580, 200, (60, 110, 190), (230, 140, 90))
            for row, y0 in enumerate((350, 410)):
                for col in range(5):
                    cv.rect(150 + col * 110 + row * 20, y0, 84, 52, (120, 28, 40), 16)
                    cv.rect(156 + col * 110 + row * 20, y0 - 24, 72, 30, (140, 38, 52), 12)


def draw_room(name, p):
    rng = random.Random(name)
    cv = Canvas()
    cv.vgrad(0, 0, W, FLOOR_Y, *p["wall"])
    cv.vgrad(0, FLOOR_Y, W, H - FLOOR_Y, p["floor"], shade(p["floor"], 0.65))
    for i in range(0, W, 80):                                             # floor planks
        cv.poly([(i, FLOOR_Y), (i + 2, FLOOR_Y), (i - 40 + (i - 400) // 4, H), (i - 42 + (i - 400) // 4, H)], shade(p["floor"], 0.8))
    cv.rect(0, FLOOR_Y - 6, W, 6, shade(p["wall"][1], 0.8))                # skirting
    if p["window"]:
        window(cv, *p["window"], rng)
    if p["beds"]:
        beds(cv, p["beds"], *p["bed"])
    extras(cv, p["extras"], p["floor"])
    cv.rect(0, 0, W, 4, (0, 0, 0))
    img = cv.img.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.4))
    # soft vignette so the picture sits nicely under the card fade
    shade_layer = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade_layer).ellipse([-W // 3, -H // 2, W + W // 3, H + H // 2], fill=255)
    shade_layer = shade_layer.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(img, img.point(lambda v: int(v * 0.72)), shade_layer)
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for room_name, params in ROOMS.items():
        draw_room(room_name, params).save(os.path.join(OUT, room_name + ".jpg"), quality=92)
        print("saved", room_name + ".jpg")
