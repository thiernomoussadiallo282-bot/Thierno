"""Étape 5 : musique de fond libre de droits, générée par le pipeline, puis mixage avec la voix.

La musique est synthétisée note par note (aucun échantillon externe) : elle est donc libre de
droits par construction, et change chaque jour grâce à une graine différente. On peut aussi
déposer ses propres musiques libres (CC0, YouTube Audio Library…) dans shorts/musiques/ :
le pipeline en choisit alors une à tour de rôle.
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import lfilter

from .outils import ffmpeg

SR = 48000
PROGRESSIONS = [  # accords (notes MIDI), ambiance « tech afro-pop » douce
    [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],   # Am F C G
    [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]],   # Dm Bb F C
    [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]],   # Em C G D
    [[45, 48, 52], [52, 55, 59], [50, 53, 57], [53, 57, 60]],   # Am Em Dm F
]


def choisir_musique(dossier_perso: Path, graine: int, duree: float, sortie: Path, bpm: int) -> str:
    perso = sorted(p for p in dossier_perso.glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg"))
    if perso:
        choix = perso[graine % len(perso)]
        ffmpeg(["-stream_loop", "-1", "-i", str(choix), "-t", f"{duree:.2f}", "-ar", str(SR), "-ac", "2",
                "-af", f"afade=t=out:st={duree - 2:.2f}:d=2", str(sortie)])
        return f"musique perso : {choix.name}"
    generer_musique(sortie, duree, graine, bpm)
    return f"musique générée (graine {graine})"


def _lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _f(m):
    return 440 * 2 ** ((m - 69) / 12)


def generer_musique(sortie: Path, duree: float, graine: int, bpm: int) -> None:
    rnd = random.Random(graine)
    bruit = np.random.default_rng(graine)
    n = int(SR * duree)
    out = np.zeros((n, 2))
    temps = 60 / bpm
    prog = rnd.choice(PROGRESSIONS)
    transpo = rnd.choice([-2, 0, 0, 2, 3])

    def ajoute(x, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= n:
            return
        j = min(n, i + len(x))
        out[i:j, 0] += x[: j - i] * g * (1 - pan * 0.6)
        out[i:j, 1] += x[: j - i] * g * (1 + pan * 0.6)

    tk = _t(0.35)
    kick = np.sin(2 * np.pi * np.cumsum(46 + 110 * np.exp(-tk * 40)) / SR) * np.exp(-tk * 9)
    th = _t(0.06)
    shaker = (bruit.standard_normal(len(th)) * np.exp(-th * 70))
    shaker = shaker - _lp(shaker, 5000)
    tc = _t(0.2)
    clap = bruit.standard_normal(len(tc))
    clap = (_lp(clap, 3000) - _lp(clap, 700)) * np.exp(-tc * 22)

    mesures = int(duree / (4 * temps)) + 1
    for m in range(mesures):
        accord = [x + transpo for x in prog[m % 4]]
        t0 = m * 4 * temps
        intro = m < 2
        # nappe
        tp = _t(4 * temps + 0.3)
        nappe = sum(((tp * _f(k) * (1 + dt)) % 1 * 2 - 1) for k in accord for dt in (-0.004, 0.004))
        nappe = _lp(nappe / (2 * len(accord)), 1400) * np.minimum(tp / 0.4, 1) * np.minimum((tp[::-1]) / 0.3, 1)
        ajoute(nappe, t0, 0.16)
        # basse
        for b in (0, 1.5, 2, 3.5):
            tb = _t(temps * 0.45)
            basse = np.sin(2 * np.pi * _f(accord[0] - 12) * tb) * np.exp(-tb * 4)
            ajoute(np.tanh(basse * 1.6), t0 + b * temps, 0.0 if intro else 0.32)
        # arpège pincé
        motif = [0, 2, 1, 2, 0, 1, 2, 1]
        for k, idx in enumerate(motif):
            ta = _t(0.3)
            note = _f(accord[idx] + 12)
            pince = (np.sin(2 * np.pi * note * ta) + 0.3 * np.sin(4 * np.pi * note * ta)) * np.exp(-ta * 11)
            ajoute(pince, t0 + k * temps / 2, 0.11, pan=0.5 if k % 2 else -0.5)
        # batterie
        for temps_i in range(4):
            tt = t0 + temps_i * temps
            if not intro:
                ajoute(kick, tt, 0.55)
                if temps_i in (1, 3):
                    ajoute(clap, tt, 0.22)
            for s in range(4):
                ajoute(shaker, tt + s * temps / 4, 0.09 if s % 2 else 0.05, pan=0.3)

    fondu = np.ones(n)
    k = int(2.0 * SR)
    fondu[-k:] = np.linspace(1, 0, k)
    fondu[: int(0.5 * SR)] = np.linspace(0, 1, int(0.5 * SR))
    out *= fondu[:, None]
    out /= max(1e-6, np.abs(out).max()) / 0.8
    sf.write(sortie, out.astype(np.float32), SR)


def mixer(voix: Path, musique: Path, sortie: Path, debut_voix: float, duree: float, volume_db: float) -> None:
    """Voix + musique baissée automatiquement sous la voix (ducking), puis -14 LUFS (réseaux sociaux)."""
    ms = int(debut_voix * 1000)
    filtre = (
        f"[0:a]aformat=channel_layouts=stereo,adelay={ms}|{ms},apad,asplit[v][cle];"
        f"[1:a]aformat=channel_layouts=stereo,volume={volume_db}dB[m];"
        "[m][cle]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=450[md];"
        f"[v][md]amix=inputs=2:normalize=0:duration=longest,atrim=0:{duree:.3f},"
        "loudnorm=I=-14:TP=-1.5:LRA=11[out]"
    )
    ffmpeg(["-i", str(voix), "-i", str(musique), "-filter_complex", filtre, "-map", "[out]",
            "-ar", str(SR), "-ac", "2", str(sortie)])
