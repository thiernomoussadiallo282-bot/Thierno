"""Étape 1 : écrire le script du Short (Claude), avec titre, description et hashtags."""
from __future__ import annotations

import os
import re

from pydantic import BaseModel, Field


class Scene(BaseModel):
    texte: str = Field(description="Phrase(s) lue(s) en voix off pendant cette scène, en français")
    image: str = Field(description="Description visuelle de l'illustration, en anglais, sans texte à l'image")


class ScriptShort(BaseModel):
    accroche: str = Field(description="Titre très court affiché à l'écran pendant les 2 premières secondes (max 6 mots)")
    scenes: list[Scene]
    titre: str = Field(description="Titre viral pour YouTube/TikTok, max 70 caractères, avec un emoji")
    description: str = Field(description="Description de 2-3 phrases pour la publication")
    hashtags: list[str] = Field(description="6 à 8 hashtags, chacun commençant par #")


CONSIGNES = """Tu écris des scripts de YouTube Shorts / TikTok verticaux de 60 secondes, en français,
pour {nom} ({compte}), une entreprise qui crée des agents IA et des automatisations pour les
entreprises en Côte d'Ivoire et en Afrique de l'Ouest. Le texte sera lu par une voix masculine
énergique : écris pour l'oreille, pas pour l'œil.

Accroche (première scène, 3 premières secondes) :
- Une seule phrase de 12 mots maximum qui arrête le pouce : question qui touche une douleur,
  contraste surprenant ou promesse concrète. Jamais « Bonjour », jamais « Dans cette vidéo ».
- Exemples de formes : « Vous perdez des clients… pendant que vous dormez. » /
  « Arrêtez de répondre à la main à vos clients. »

Style oral :
- Environ {mots} mots au total. Phrases courtes (souvent moins de 12 mots), une idée par phrase.
- Parle directement au spectateur avec « vous ». Rythme varié : une phrase longue, puis deux très courtes.
- Utilise la ponctuation pour l'intonation : « ? » pour les questions, « ! » pour l'énergie (avec mesure),
  « … » pour une pause de suspense avant une révélation.
- Relance l'attention au milieu (« Et c'est là que ça devient intéressant. », « Mais attendez. »).
- Pas de listes lues à plat, pas de jargon, pas de parenthèses, pas d'abréviations (écris les nombres en lettres).

Structure : accroche → problème vécu → solution (l'agent I.A.) → exemple concret → bénéfice → appel à l'action.
- 7 à 9 scènes, chaque scène = 1 ou 2 phrases.
- La dernière scène invite à s'abonner à {compte} et à écrire sur WhatsApp au {whatsapp} pour avoir son propre agent I.A.
- Écris « I.A. » pour que la voix prononce bien « I-A ».
- Honnêteté : aucun chiffre, client, témoignage ou résultat inventé. Si tu donnes un exemple, présente-le comme un exemple.
- Pour chaque scène, décris une illustration (en anglais) qui montre concrètement l'idée : personnages, lieu, objets.
  Pas de texte, pas d'écran lisible, pas de logo dans l'image."""


def ecrire_script(idee: dict, cfg: dict) -> ScriptShort:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        try:
            return _script_claude(idee, cfg)
        except Exception as e:  # le pipeline quotidien ne doit pas s'arrêter pour ça
            print(f"[script] Claude indisponible ({e.__class__.__name__}: {e}) -> script modèle")
    else:
        print("[script] pas de clé ANTHROPIC_API_KEY -> script modèle")
    return _script_modele(idee, cfg)


def _script_claude(idee: dict, cfg: dict) -> ScriptShort:
    import anthropic

    m = cfg["marque"]
    systeme = CONSIGNES.format(nom=m["nom"], compte=m["compte"], whatsapp=m["whatsapp"],
                               mots=cfg["voix"]["mots_cibles"])
    demande = f"Idée du jour : {idee['idee']}\nAngle : {idee.get('angle') or 'libre'}"

    client = anthropic.Anthropic()
    reponse = client.beta.messages.parse(
        model=cfg["claude"]["modele"],
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": cfg["claude"].get("effort", "medium")},
        system=systeme,
        messages=[{"role": "user", "content": demande}],
        output_format=ScriptShort,
    )
    if reponse.stop_reason == "refusal":
        raise RuntimeError("requête refusée par le modèle")
    script = reponse.parsed_output
    if script is None or len(script.scenes) < 3:
        raise RuntimeError("réponse incomplète")
    print(f"[script] écrit par {reponse.model}")
    return script


def _script_modele(idee: dict, cfg: dict) -> ScriptShort:
    """Script de secours sans IA : structure fixe remplie avec l'idée du CSV."""
    m = cfg["marque"]
    sujet = idee["idee"].rstrip(".")
    angle = (idee.get("angle") or "").rstrip(".")
    textes = [
        ("Vous perdez du temps… et des clients. Chaque jour.",
         "a curious West African entrepreneur looking at a glowing smartphone in a small shop at dusk"),
        (f"{sujet} ? Oui, c'est possible. Parce que chaque jour, des heures partent dans les mêmes tâches : répondre, relancer, trier.",
         "a tired shop owner surrounded by floating paper notes and chat bubbles"),
        (f"{angle}." if angle else "Pourtant, une grande partie de ce travail suit toujours les mêmes règles.",
         "a calm desk with a notebook and a laptop, warm morning light, organised workspace"),
        ("C'est exactement ce qu'un agent I.A. sait faire : appliquer vos règles, sans se fatiguer, à toute heure.",
         "a friendly abstract robot assistant made of soft geometric shapes helping a business owner"),
        ("Prenons un exemple simple : un client écrit le soir pour demander un prix. L'agent répond tout de suite, poliment, avec les bonnes informations.",
         "a smartphone glowing in a dark room at night, a chat conversation shown as abstract bubbles"),
        ("Le lendemain matin, vous trouvez la conversation résumée, prête à être conclue.",
         "a business owner drinking coffee in the morning reading a tablet with a satisfied smile"),
        ("Vous gardez le contrôle : l'agent prépare, propose, et vous validez ce qui compte.",
         "a business owner approving a task on a tablet while a small robot assistant waits"),
        ("Résultat : moins d'oublis, des clients qui ont une réponse rapide, et du temps pour développer votre activité.",
         "happy customers receiving messages on their phones in a lively Abidjan street"),
        ("Pas besoin d'être expert en technologie. On part de votre façon de travailler, et on l'automatise étape par étape.",
         "two people drawing a simple workflow with arrows on a whiteboard"),
        (f"Abonnez-vous à {m['compte']} pour la suite, et écrivez-moi sur WhatsApp au {m['whatsapp']} pour avoir votre propre agent I.A.",
         "a smartphone with a green chat bubble icon floating above an open hand, golden light"),
    ]
    return ScriptShort(
        accroche=_raccourcir(sujet, 6),
        scenes=[Scene(texte=t, image=i) for t, i in textes],
        titre=f"{_raccourcir(sujet, 9)} 🤖",
        description=f"{sujet}. Voici comment un agent I.A. peut vous faire gagner du temps, sans perdre le contrôle.",
        hashtags=["#IA", "#intelligenceartificielle", "#automatisation", "#entrepreneur",
                  "#business", "#côtedivoire", "#agentIA"],
    )


def _raccourcir(texte: str, n: int) -> str:
    mots = texte.split()
    return " ".join(mots[:n]) + ("…" if len(mots) > n else "")


def texte_complet(script: ScriptShort) -> str:
    return " ".join(s.texte.strip() for s in script.scenes)


def nettoyer_hashtags(tags: list[str]) -> list[str]:
    propres = []
    for t in tags:
        t = "#" + re.sub(r"[^\w]", "", t.lstrip("#"))
        if len(t) > 1 and t.lower() not in [p.lower() for p in propres]:
            propres.append(t)
    if "#shorts" not in [p.lower() for p in propres]:
        propres.insert(0, "#Shorts")
    return propres[:9]
