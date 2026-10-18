from __future__ import annotations

import re
import subprocess
import unicodedata
from pathlib import Path


def ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def duree_audio(fichier: Path) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(fichier)])
    return float(out.decode().strip())


def slug(texte: str, n: int = 40) -> str:
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:n].rstrip("-") or "short"


def normaliser_mot(mot: str) -> str:
    t = unicodedata.normalize("NFKD", mot.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t)
