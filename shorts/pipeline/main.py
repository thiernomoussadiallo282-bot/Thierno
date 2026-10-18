"""Pipeline quotidien : idees.csv -> Short vertical 60 s (1080x1920) prêt à publier.

Usage :
    python -m pipeline.main                 # prochaine idée « a_faire » du CSV
    python -m pipeline.main --idee 4        # une idée précise
    python -m pipeline.main --essai         # ne marque pas l'idée comme faite
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .images import generer_images
from .musique import choisir_musique, mixer
from .outils import duree_audio, ffmpeg, slug
from .script import ecrire_script, nettoyer_hashtags, texte_complet
from .transcription import horodater
from .voix import generer_voix

RACINE = Path(__file__).resolve().parent.parent
FPS = 30
DEBUT_VOIX = 0.4


def main() -> int:
    ap = argparse.ArgumentParser(description="Produit le Short du jour")
    ap.add_argument("--idee", help="id de l'idée à produire (sinon la prochaine « a_faire »)")
    ap.add_argument("--essai", action="store_true", help="ne pas marquer l'idée comme faite")
    ap.add_argument("--csv", default=str(RACINE / "idees.csv"))
    ap.add_argument("--sorties", default=str(RACINE / "sorties"))
    args = ap.parse_args()

    cfg = json.loads((RACINE / "config.json").read_text(encoding="utf-8"))
    lignes, champs = _lire_csv(Path(args.csv))
    idee = _choisir_idee(lignes, args.idee)
    if idee is None:
        print("Aucune idée « a_faire » dans idees.csv : ajoutez-en de nouvelles.")
        return 2

    aujourd_hui = dt.date.today().isoformat()
    dossier = Path(args.sorties) / f"{aujourd_hui}-{slug(idee['idee'])}"
    dossier.mkdir(parents=True, exist_ok=True)
    print(f"== Idée {idee['id']} : {idee['idee']}\n== Dossier : {dossier}")

    total = float(cfg["duree_totale_s"])
    outro = float(cfg["duree_outro_s"])

    # 1. script
    script = ecrire_script(idee, cfg)
    (dossier / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")
    texte = texte_complet(script)

    # 2. voix off
    voix = generer_voix(texte, dossier / "voix.wav", cfg, duree_max=total - outro - DEBUT_VOIX - 0.4)
    d_voix = duree_audio(voix)

    # 3. horodatage mot à mot (Whisper)
    mots, methode = horodater(voix, texte, cfg)
    for m in mots:
        m["start"] = round(m["start"] + DEBUT_VOIX, 3)
        m["end"] = round(m["end"] + DEBUT_VOIX, 3)
    (dossier / "mots.json").write_text(json.dumps(mots, ensure_ascii=False, indent=1), encoding="utf-8")

    # 4. découpage en scènes (chaque scène commence à son premier mot prononcé).
    # La dernière scène (l'appel à l'action) n'a pas d'image : la carte de fin (logo + WhatsApp)
    # s'affiche dès qu'elle commence, pendant que la voix lit l'appel à l'action.
    debut_outro = min(total - outro, max(DEBUT_VOIX + d_voix + 0.5, total - outro - 6))
    debut_outro = max(debut_outro, DEBUT_VOIX + d_voix + 0.3)
    scenes, k = [], 0
    for i, s in enumerate(script.scenes):
        n = len(s.texte.split())
        debut = 0.0 if i == 0 else mots[k]["start"] - 0.15
        scenes.append({"debut": round(debut, 3), "image": f"images/scene-{i:02d}.jpg"})
        k += n
    if len(scenes) > 2:
        debut_outro = min(debut_outro, scenes.pop()["debut"])
    for i, s in enumerate(scenes):
        s["fin"] = scenes[i + 1]["debut"] if i + 1 < len(scenes) else debut_outro

    # 5. images (sans la scène de fin)
    generer_images([s.image for s in script.scenes[:len(scenes)]], dossier / "images", cfg,
                   decalage=dt.date.today().toordinal())
    marque = dict(cfg["marque"])
    logo = RACINE / marque.get("logo_fichier", "")
    if marque.get("logo_fichier") and logo.is_file():
        (dossier / "marque").mkdir(exist_ok=True)
        shutil.copy(logo, dossier / "marque" / logo.name)
        marque["logo_fichier"] = f"marque/{logo.name}"
    else:
        marque["logo_fichier"] = ""

    # 6. musique libre + mixage
    graine = int(dt.date.today().strftime("%Y%m%d"))
    origine_musique = choisir_musique(RACINE / "musiques", graine, total, dossier / "musique.wav",
                                      cfg["musique"]["bpm"])
    mixer(voix, dossier / "musique.wav", dossier / "mix.wav", DEBUT_VOIX, total, cfg["musique"]["volume_db"])

    # 7. montage Remotion
    props = {
        "fps": FPS,
        "dureeFrames": int(round(total * FPS)),
        "accroche": script.accroche,
        "scenes": scenes,
        "mots": [{**m, "text": _affichage(m["text"])} for m in mots],
        "debutOutro": round(debut_outro, 3),
        "audio": "mix.wav",
        "marque": marque,
    }
    (dossier / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding="utf-8")
    video = dossier / "short.mp4"
    _rendre(dossier, video)

    # 8. titre, description, hashtags, sous-titres, miniature
    hashtags = nettoyer_hashtags(script.hashtags)
    script.titre, script.description = _affichage(script.titre), _affichage(script.description)
    meta = {
        "date": aujourd_hui, "idee_id": idee["id"], "titre": script.titre,
        "description": script.description, "hashtags": hashtags,
        "duree_s": round(duree_audio(video), 2), "voix_s": round(d_voix, 2),
        "sous_titres": methode, "musique": origine_musique,
    }
    (dossier / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (dossier / "publication.txt").write_text(
        f"TITRE\n{script.titre}\n\nDESCRIPTION\n{script.description}\n\n"
        f"Agents I.A. sur mesure : WhatsApp {cfg['marque']['whatsapp']} · {cfg['marque']['compte']}\n\n"
        f"{' '.join(hashtags)}\n", encoding="utf-8")
    _srt(mots, dossier / "sous-titres.srt")
    ffmpeg(["-ss", "1.5", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(dossier / "miniature.jpg")])

    # 9. idée marquée comme faite
    if not args.essai:
        idee["statut"], idee["date"] = "fait", aujourd_hui
        _ecrire_csv(Path(args.csv), lignes, champs)

    print(f"\nOK -> {video}\nTitre : {script.titre}\n{' '.join(hashtags)}")
    _sortie_github(dossier, script.titre)
    return 0


def _rendre(dossier: Path, video: Path) -> None:
    remotion = RACINE / "remotion"
    if not (remotion / "node_modules").exists():
        subprocess.run(["npm", "ci" if (remotion / "package-lock.json").exists() else "install"],
                       cwd=remotion, check=True)
    cmd = ["npx", "remotion", "render", "src/index.ts", "Short", str(video),
           f"--props={dossier / 'props.json'}", f"--public-dir={dossier}",
           "--codec=h264", "--crf=18", "--audio-bitrate=192k", "--log=warn"]
    if os.environ.get("REMOTION_BROWSER_EXECUTABLE"):
        cmd.append(f"--browser-executable={os.environ['REMOTION_BROWSER_EXECUTABLE']}")
    if os.environ.get("REMOTION_CONCURRENCY"):
        cmd.append(f"--concurrency={os.environ['REMOTION_CONCURRENCY']}")
    print("[remotion] rendu en cours…")
    subprocess.run(cmd, cwd=remotion, check=True)


def _affichage(texte: str) -> str:
    return re.sub(r"\bI\.A\.?", "IA", texte)


def _srt(mots: list[dict], chemin: Path) -> None:
    def ts(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    blocs, cour = [], []
    for m in mots:
        cour.append(m)
        if m["text"][-1] in ".!?,;:" or len(cour) >= 7:
            blocs.append(cour)
            cour = []
    if cour:
        blocs.append(cour)
    chemin.write_text("".join(
        f"{i}\n{ts(b[0]['start'])} --> {ts(b[-1]['end'])}\n{' '.join(_affichage(x['text']) for x in b)}\n\n"
        for i, b in enumerate(blocs, 1)), encoding="utf-8")


def _lire_csv(chemin: Path):
    with chemin.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames


def _ecrire_csv(chemin: Path, lignes, champs) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)


def _choisir_idee(lignes, ident):
    if ident:
        return next((l for l in lignes if l["id"] == str(ident)), None)
    return next((l for l in lignes if (l.get("statut") or "a_faire").strip() in ("", "a_faire")), None)


def _sortie_github(dossier: Path, titre: str) -> None:
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"dossier={dossier}\nnom={dossier.name}\n")
            f.write(f"titre={titre.replace(chr(10), ' ')}\n")


if __name__ == "__main__":
    sys.exit(main())
