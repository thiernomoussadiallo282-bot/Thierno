"""Étape 2 : voix off française (Edge TTS, avec Kokoro local en secours)."""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from .outils import duree_audio, ffmpeg


def generer_voix(texte: str, sortie: Path, cfg: dict, duree_max: float) -> Path:
    """Crée sortie (wav 48 kHz mono) et ajuste le débit pour tenir dans duree_max secondes."""
    moteurs = [cfg["voix"]["moteur"]] + [m for m in ("edge", "kokoro") if m != cfg["voix"]["moteur"]]
    derniere_erreur = None
    for moteur in moteurs:
        try:
            vitesse = 1.0
            for _ in range(3):
                _synthese(moteur, texte, sortie, cfg, vitesse)
                d = duree_audio(sortie)
                print(f"[voix] {moteur} vitesse {vitesse:.2f} -> {d:.1f} s (max {duree_max:.1f} s)")
                if d <= duree_max and d >= duree_max * 0.8:
                    return sortie
                cible = vitesse * d / (duree_max * (0.97 if d > duree_max else 0.9))
                nouvelle = min(1.25, max(0.9, cible))
                if abs(nouvelle - vitesse) < 0.01:
                    break
                vitesse = nouvelle
            if duree_audio(sortie) > duree_max:  # dernier recours : accélération sans changer la hauteur
                _accelerer(sortie, duree_audio(sortie) / duree_max)
            return sortie
        except Exception as e:
            derniere_erreur = e
            for f in sortie.parent.glob(sortie.stem + ".brut.*"):
                f.unlink()
            print(f"[voix] {moteur} indisponible ({e.__class__.__name__}: {e})")
    raise RuntimeError(f"aucun moteur de voix n'a fonctionné : {derniere_erreur}")


def _synthese(moteur: str, texte: str, sortie: Path, cfg: dict, vitesse: float) -> None:
    brut = sortie.with_suffix(".brut" + (".mp3" if moteur == "edge" else ".wav"))
    if moteur == "edge":
        import edge_tts

        taux = f"{round((vitesse - 1) * 100):+d}%"
        asyncio.run(edge_tts.Communicate(texte, cfg["voix"]["edge_voix"], rate=taux).save(str(brut)))
    elif moteur == "kokoro":
        npx = shutil.which("npx")
        if not npx:
            raise RuntimeError("npx introuvable")
        subprocess.run([npx, "-y", "hyperframes@0.8.145", "tts", texte, "-v", cfg["voix"]["kokoro_voix"],
                        "-s", f"{vitesse:.2f}", "-o", str(brut)],
                       check=True, capture_output=True, env=os.environ.copy(), timeout=900)
    else:
        raise ValueError(f"moteur de voix inconnu : {moteur}")
    # silence en tête/queue retiré, puis 48 kHz mono
    ffmpeg(["-i", str(brut), "-af",
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse",
            "-ar", "48000", "-ac", "1", str(sortie)])
    brut.unlink(missing_ok=True)


def _accelerer(fichier: Path, facteur: float) -> None:
    tmp = fichier.with_suffix(".tmp.wav")
    ffmpeg(["-i", str(fichier), "-filter:a", f"atempo={min(facteur, 1.5):.4f}", str(tmp)])
    tmp.replace(fichier)
