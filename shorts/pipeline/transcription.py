"""Étape 4 : horodatage mot à mot de la voix off avec Whisper.

Whisper (faster-whisper) donne le moment où chaque mot est prononcé. On recale ensuite ces temps
sur le texte exact du script : les sous-titres gardent la bonne orthographe, et les temps restent
ceux de la voix réelle.
"""
from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path

from .outils import duree_audio, normaliser_mot


def horodater(audio: Path, texte: str, cfg: dict) -> tuple[list[dict], str]:
    mots_script = texte.split()
    try:
        mots_whisper = _whisper(audio, cfg)
        print(f"[whisper] {len(mots_whisper)} mots reconnus")
        return _aligner(mots_script, mots_whisper), "whisper"
    except Exception as e:
        print(f"[whisper] indisponible ({e.__class__.__name__}: {e}) -> estimation proportionnelle")
        return _estimer(mots_script, duree_audio(audio)), "estimation"


def _whisper(audio: Path, cfg: dict) -> list[dict]:
    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly

    # audio décodé ici (16 kHz mono) : évite le décodeur PyAV, dont les versions récentes
    # sont incompatibles avec faster-whisper
    son, sr = sf.read(str(audio), dtype="float32", always_2d=True)
    son = resample_poly(son.mean(axis=1), 16000, sr).astype(np.float32)

    modele = WhisperModel(cfg["whisper"]["modele"], device="cpu", compute_type="int8")
    segments, _ = modele.transcribe(son, language=cfg["whisper"]["langue"],
                                    word_timestamps=True, vad_filter=False, beam_size=5)
    mots = [{"text": w.word.strip(), "start": float(w.start), "end": float(w.end)}
            for s in segments for w in (s.words or []) if w.word.strip()]
    if not mots:
        raise RuntimeError("aucun mot reconnu")
    return mots


def _aligner(script: list[str], whisper: list[dict]) -> list[dict]:
    a = [normaliser_mot(m) for m in script]
    b = [normaliser_mot(m["text"]) for m in whisper]
    temps: list[tuple[float, float] | None] = [None] * len(script)
    for bloc in SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(bloc.size):
            w = whisper[bloc.b + k]
            temps[bloc.a + k] = (w["start"], w["end"])
    # mots non reconnus : répartis entre les voisins reconnus, au prorata de leur longueur
    fin_audio = whisper[-1]["end"]
    i = 0
    while i < len(script):
        if temps[i] is not None:
            i += 1
            continue
        j = i
        while j < len(script) and temps[j] is None:
            j += 1
        t0 = temps[i - 1][1] if i > 0 else whisper[0]["start"]
        t1 = temps[j][0] if j < len(script) else fin_audio
        _repartir(script, temps, i, j, t0, max(t1, t0 + 0.12 * (j - i)))
        i = j
    return [{"text": m, "start": round(s, 3), "end": round(e, 3)} for m, (s, e) in zip(script, temps)]


def _estimer(script: list[str], duree: float) -> list[dict]:
    temps: list[tuple[float, float] | None] = [None] * len(script)
    _repartir(script, temps, 0, len(script), 0.0, duree)
    return [{"text": m, "start": round(s, 3), "end": round(e, 3)} for m, (s, e) in zip(script, temps)]


def _repartir(script, temps, i, j, t0, t1):
    poids = [len(script[k]) + 2 + (6 if script[k][-1] in ".!?" else 3 if script[k][-1] in ",;:" else 0)
             for k in range(i, j)]
    total, t = sum(poids) or 1, t0
    for k, p in zip(range(i, j), poids):
        d = (t1 - t0) * p / total
        temps[k] = (t, t + d * 0.92)
        t += d
