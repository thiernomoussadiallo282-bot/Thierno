---
workflow: general-video
flow: automation
storyboard: yes
message: "Des agents IA et des automatisations n8n qui travaillent à la place du patron de PME"
destination: shorts-reels-tiktok
aspect: 1080x1920
language: fr
audience: "Patrons de PME"
length: 36s
angle: promo
---

## Intent

Vidéo promo verticale (9:16, 1080x1920), 30-40 s, en français. Montrer à des patrons de PME
que l'auteur crée des agents IA et des automatisations n8n qui travaillent à leur place.
Ton : moderne, dynamique, confiant. Fond sombre, accents cyan, transitions rapides calées
sur la musique, aucun plan de plus de 3 s sans mouvement.

## Assets

- assets/src/4.jpg — agent IA Ventes / Locations / Clients / MAJ / Alerte Gmail (520x390) → scène 4-12 s
- assets/src/3.jpg — agent IA chat Plans / Clients / Alerte Gmail (1080x810) → scène 12-20 s
- assets/src/1.jpg — workflow de tri : RSS → Normalisation → Classification → Garder A et B → Extraction → Sheets → scène 20-28 s
- assets/src/2.jpg — doublon basse résolution de 1.jpg, non utilisé

## Customizations

- Photos d'écran recadrées (sans barre des tâches ni bords), couleurs et contraste corrigés, moiré atténué.
- Jamais en plein écran statique : zooms lents, panoramiques, gros plans sur AI Agent, Gmail, Google Sheets ; surbrillance animée des connexions.
- Voix off française (Kokoro local, faute de compte HeyGen), phrases courtes synchronisées.
- Sous-titres incrustés mot par mot, gros, mots-clés en cyan #22D3EE.
- Musique tech/corporate rythmée libre de droits, ducking sous la voix, montée sur le CTA.
- SFX : whoosh sur transitions, pop sur apparition des nœuds, notification sur alertes email, impact sur l'accroche et le logo final.
- Illustrations ajoutées : onde vocale (message vocal) et carte « 07:00 — Rapport du jour » (absents des captures).

## Script validé

- 0–4 s : « Et si votre entreprise travaillait toute seule ? »
- 4–12 s : « Voici votre agent IA. Il répond à vos clients, jour et nuit… même par message vocal. »
- 12–20 s : « Un nouveau client ? Enregistré automatiquement. Une demande urgente ? Vous recevez une alerte par email. »
- 20–28 s : « Il trie, classe et remplit vos tableaux. Et chaque matin à 7 h, votre rapport vous attend. »
- 28–36 s : « [Nom] : automatisez votre business. Contactez-nous dès aujourd'hui. »

## Notes

- Nom de l'entreprise et contact pas encore fournis : variables `brandName` / `contact`, à remplir avant le rendu final.
- Couleur de marque non fournie : cyan #22D3EE retenu (recommandation acceptée).
