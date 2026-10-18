"""Étape 3 : une illustration verticale par scène, toujours dans le même style.

Fournisseur par défaut : Pollinations (gratuit, sans clé, modèle Flux) avec un style et une graine
fixes. Si le service ne répond pas, une illustration de secours est dessinée localement dans la
même palette, pour que la vidéo du jour soit quand même produite.
"""
from __future__ import annotations

import io
import math
import os
import random
import re
import time
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

L, H = 1080, 1920


# Distribution des personnages d'une scène à l'autre : hommes et femmes, de 20 à 65 ans.
# Utilisée quand la description d'une scène ne précise pas déjà qui on voit.
CASTING = [
    "an Ivorian man in his forties with a short beard",
    "an Ivorian woman in her fifties",
    "a young Ivorian man in his early twenties",
    "an Ivorian woman in her thirties",
    "an older Ivorian man in his sixties with grey hair",
    "a young Ivorian woman in her twenties",
    "an Ivorian man in his thirties",
    "an Ivorian woman in her sixties",
]
_PERSONNE = re.compile(r"\b(man|men|woman|women|boy|girl|guy|lady|grandmother|grandfather|"
                       r"father|mother|husband|wife|businessman|businesswoman|male|female)\b", re.I)


def avec_casting(prompt: str, i: int, decalage: int = 0) -> str:
    if _PERSONNE.search(prompt):
        return prompt
    return f"{prompt}. Main person: {CASTING[(i + decalage) % len(CASTING)]}"


def generer_images(prompts: list[str], dossier: Path, cfg: dict, decalage: int = 0) -> list[Path]:
    dossier.mkdir(parents=True, exist_ok=True)
    c = cfg["images"]
    chemins = []
    distant = c["fournisseur"] == "pollinations"
    for i, p in enumerate(prompts):
        chemin = dossier / f"scene-{i:02d}.jpg"
        ok = False
        if distant:
            ok = _pollinations(f"{avec_casting(p, i, decalage)}. Style: {c['style']}", c["graine"] + i,
                               c.get("modele", "flux"), chemin)
            distant = ok or i > 0  # service injoignable dès la 1re image : on n'insiste pas
        if not ok:
            _illustration_locale(p, c["graine"] + i, chemin)
        chemins.append(chemin)
        print(f"[images] scène {i + 1}/{len(prompts)} {'IA' if ok else 'locale'}")
    return chemins


_dernier_appel = 0.0


def _pollinations(prompt: str, graine: int, modele: str, chemin: Path) -> bool:
    """Sans compte, Pollinations accepte environ une image toutes les 15 s : on espace les appels.
    Avec un jeton gratuit (variable POLLINATIONS_TOKEN, auth.pollinations.ai) la limite est plus haute."""
    global _dernier_appel
    import requests

    jeton = os.environ.get("POLLINATIONS_TOKEN", "")
    entetes = {"Authorization": f"Bearer {jeton}"} if jeton else {}
    attente = 4 if jeton else 16
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) +
           f"?width={L}&height={H}&seed={graine}&model={modele}&nologo=true&enhance=false")
    for essai in range(5):
        time.sleep(max(0.0, _dernier_appel + attente * (essai + 1) - time.time()))
        _dernier_appel = time.time()
        try:
            r = requests.get(url, headers=entetes, timeout=180)
            if r.ok and r.headers.get("content-type", "").startswith("image"):
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
                _cadrer(img).save(chemin, quality=92)
                return True
            print(f"[images] pollinations HTTP {r.status_code} {r.text[:120]!r}")
        except Exception as e:
            print(f"[images] pollinations : {e.__class__.__name__}")
    return False


def _cadrer(img: Image.Image) -> Image.Image:
    """Recadre au centre en 9:16 puis redimensionne en 1080x1920."""
    w, h = img.size
    cible = L / H
    if w / h > cible:
        nw = int(h * cible)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / cible)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return img.resize((L, H), Image.LANCZOS)


PALETTE = [(11, 31, 58), (22, 52, 92), (244, 185, 66), (46, 170, 160), (240, 232, 214)]


def _illustration_locale(prompt: str, graine: int, chemin: Path) -> None:
    """Illustration abstraite « éditoriale » : dégradé marine, formes douces or/turquoise, grain."""
    rnd = random.Random(f"{graine}-{prompt}")
    img = Image.new("RGB", (L, H))
    d = ImageDraw.Draw(img)
    haut, bas = PALETTE[1], PALETTE[0]
    for y in range(H):
        t = y / H
        d.line([(0, y), (L, y)], fill=tuple(int(haut[k] * (1 - t) + bas[k] * t) for k in range(3)))

    calque = Image.new("RGBA", (L, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(calque)
    # soleil / halo
    cx, cy, r = rnd.randint(250, 830), rnd.randint(450, 900), rnd.randint(220, 340)
    dc.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PALETTE[2] + (235,))
    # collines
    for k, couleur in enumerate([PALETTE[3] + (200,), PALETTE[1] + (255,), PALETTE[0] + (255,)]):
        base = 1250 + k * 170
        pts = [(0, H)]
        amp, phase = rnd.randint(60, 140), rnd.random() * 6.28
        for x in range(0, L + 40, 40):
            pts.append((x, base + amp * math.sin(x / rnd.randint(180, 320) + phase)))
        pts.append((L, H))
        dc.polygon(pts, fill=couleur)
    # silhouettes d'immeubles
    x = rnd.randint(-40, 40)
    while x < L:
        w, h = rnd.randint(70, 150), rnd.randint(180, 520)
        dc.rectangle([x, 1330 - h, x + w, 1400], fill=(16, 40, 72, 255))
        for fy in range(1330 - h + 30, 1380, 46):
            for fx in range(x + 16, x + w - 16, 34):
                if rnd.random() < 0.45:
                    dc.rectangle([fx, fy, fx + 14, fy + 20], fill=PALETTE[2] + (210,))
        x += w + rnd.randint(8, 30)
    # bulles de message flottantes
    for _ in range(rnd.randint(3, 5)):
        bx, by, bw = rnd.randint(80, 760), rnd.randint(300, 1000), rnd.randint(150, 260)
        dc.rounded_rectangle([bx, by, bx + bw, by + bw // 2], radius=40, fill=PALETTE[4] + (225,))
        for j in range(3):
            dc.ellipse([bx + 40 + j * 45, by + bw // 4 - 10, bx + 60 + j * 45, by + bw // 4 + 10],
                       fill=PALETTE[0] + (200,))
    img = Image.alpha_composite(img.convert("RGBA"), calque.filter(ImageFilter.GaussianBlur(1.2))).convert("RGB")
    # grain papier
    grain = Image.effect_noise((L, H), 18).convert("RGB")
    Image.blend(img, grain, 0.06).save(chemin, quality=92)
