"""Échantillons de voix masculines : la même accroche lue par chaque voix, pour choisir à l'oreille.

    python -m pipeline.echantillons
Résultat : sorties/echantillons-voix/*.mp3 (avec le traitement « voix radio » du pipeline).
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from .outils import ffmpeg
from .voix import VOIX_RADIO

RACINE = Path(__file__).resolve().parent.parent
VOIX = [
    ("1-remy-france-expressive", "fr-FR-RemyMultilingualNeural", "-3Hz"),
    ("2-henri-france-posee", "fr-FR-HenriNeural", "+0Hz"),
    ("3-antoine-quebec", "fr-CA-AntoineNeural", "+0Hz"),
    ("4-jean-quebec-grave", "fr-CA-JeanNeural", "+0Hz"),
    ("5-gerard-belgique", "fr-BE-GerardNeural", "+0Hz"),
    ("6-fabrice-suisse", "fr-CH-FabriceNeural", "+0Hz"),
]
TEXTE = ("Vous perdez des clients… pendant que vous dormez. Un message arrive à vingt-deux heures, "
         "personne ne répond, et le client part chez le concurrent. Et si un agent I.A. répondait "
         "à votre place, tout de suite, avec vos règles ? Abonnez-vous, je vous montre comment.")


def main() -> None:
    import edge_tts

    cfg = json.loads((RACINE / "config.json").read_text(encoding="utf-8"))
    taux = f"{round((cfg['voix'].get('vitesse_base', 1.0) - 1) * 100):+d}%"
    dossier = RACINE / "sorties" / "echantillons-voix"
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, voix, tonalite in VOIX:
        brut = dossier / f"{nom}.brut.mp3"
        try:
            asyncio.run(edge_tts.Communicate(TEXTE, voix, rate=taux, pitch=tonalite).save(str(brut)))
            ffmpeg(["-i", str(brut), "-af", VOIX_RADIO + ",loudnorm=I=-16:TP=-1.5", "-ar", "48000",
                    "-b:a", "160k", str(dossier / f"{nom}.mp3")])
            print(f"[échantillon] {nom} ({voix})")
        except Exception as e:
            print(f"[échantillon] {nom} indisponible : {e.__class__.__name__}")
        finally:
            brut.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
