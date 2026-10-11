---
format: 1080x1920
duration: 36s
message: "Des agents IA et des automatisations n8n qui travaillent à la place du patron de PME"
arc: Accroche → Agent qui répond → Agent qui enregistre et alerte → Workflow qui trie et rapporte → CTA
audience: Patrons de PME
mode: collaborative
---

# Storyboard v1 — Promo agents IA (9:16)

## Décisions

- **Message** : votre entreprise peut tourner toute seule — des agents IA n8n font le travail à votre place.
- **Format** : 1080×1920, 36 s, voix off FR (Kokoro `ff_siwis`), musique 120 BPM (une mesure = 2 s, coupes sur les temps forts 4 / 12 / 20 / 28 s), sous-titres mot à mot.
- **Zone sous-titres** : bande y 1330–1530 px ; le contenu vit au-dessus (y 140–1260) ; rien d'important sous 1580 px (interface TikTok / Reels).
- **Fil conducteur** : la « carte écran » — chaque capture vit dans la même carte arrondie à bord cyan ; une caméra virtuelle se déplace dedans ; un point lumineux cyan voyage le long des connexions et passe d'une scène à l'autre.
- **Marque** : fond #0B1016 (noir teinté cyan), texte #EAF6FA, accent unique #22D3EE. Display : Montserrat 900. Données / étiquettes : JetBrains Mono 700.
- **À éviter** : aucune capture en plein écran statique ; pas de faux écran n8n reconstruit (les captures sont réelles) ; pas de diaporama (chaque plan bouge) ; pas d'écran de fin statique.
- **Plan tenu** : 33,5–36 s, le logo/nom tient pendant que la musique conclut — seul plan quasi immobile (respiration lente du halo).
- **Vérité** : les nœuds montrés sont les vrais workflows de l'auteur. « Message vocal » et « rapport à 7 h » ne figurent sur aucune capture : ils sont illustrés par des incrustations (onde vocale, carte 07:00), pas par un faux nœud n8n.

## Frame 1 — Accroche

- status: animated
- src: compositions/01-hook.html
- duration: 4s
- transition_in: cut
- scene: « Et si votre entreprise / travaillait / TOUTE SEULE ? » claque en gros texte
- voiceover: "Et si votre entreprise travaillait toute seule ?"
- poster: 3.2
- rules: kinetic-beat-slam, ambient-glow-bloom
- audio: impact 2.4 s (sur « toute seule »), riser 2.1–4.0 s, whoosh 3.8 s

0,0–0,6 s : grille et halo cyan s'allument. 0,6 s « Et si votre entreprise » glisse depuis la gauche ; 1,6 s « travaillait » monte en rotation ; 2,4 s « TOUTE SEULE ? » (cyan, 190 px) claque en scale-slam avec secousse de caméra. 3,7 s sortie en whip vers la gauche (flou de mouvement). Contrainte : pas de fondu mou — tout est percussif.

## Frame 2 — L'agent répond (4.jpg)

- status: animated
- src: compositions/02-agent.html
- duration: 8s
- transition_in: whip-left
- scene: carte écran inclinée en 3D, zoom sur AI Agent, bulle de chat + onde vocale, puis Ventes / Locations s'allument
- voiceover: "Voici votre agent IA. Il répond à vos clients, jour et nuit… même par message vocal."
- poster: 3.6
- rules: 3d-camera-flight, viewport-change, ai-tracking-box, spring-pop-entrance, svg-path-draw
- audio: whoosh 4.0 s, pop 6.2 s (bulle), pop 8.4 s (onde vocale), pops 9.6 / 10.0 / 10.4 s (nœuds)

4,0–6,4 s : la carte arrive inclinée (rotateX 18°) et s'aplatit en zoomant lentement sur le workflow complet. 4,3 s étiquette « AGENT IA · n8n ». 6,0–8,8 s : poussée sur le nœud **AI Agent**, cadre de suivi cyan qui se verrouille ; bulle « Bonjour, une location pour samedi ? » surgit au-dessus de la carte, réponse « C'est réservé ✓ ». 8,2 s onde vocale animée (« message vocal »). 8,8–12 s : panoramique vers le bas-droite le long des pointillés ; **Ventes** et **Locations** reçoivent un anneau cyan au rythme des pops, les connexions se dessinent en cyan. Contrainte : jamais plus de 2,5 s sans mouvement de caméra.

## Frame 3 — Il enregistre et vous alerte (3.jpg)

- status: animated
- src: compositions/03-clients.html
- duration: 8s
- transition_in: whip-up
- scene: zoom sur Clients (Sheets) + ligne « Nouveau client ✓ », panoramique vers Alerte (Gmail) + notification email
- voiceover: "Un nouveau client ? Enregistré automatiquement. Une demande urgente ? Vous recevez une alerte par email."
- poster: 4.5
- rules: viewport-change, spring-pop-entrance, svg-path-draw, depth-of-field-blur
- audio: whoosh 12.0 s, pop 13.4 s (ligne), notification 16.6 s, pop 17.4 s

12,0–14,6 s : entrée en whip, caméra sur **Clients (Google Sheets)** ; un mini-tableau cyan glisse sous la carte, la ligne « Nouveau client · Mme Diallo · ✓ » s'écrit. 14,6–17,2 s : panoramique vers **Alerte (Gmail)**, flou de profondeur sur le reste ; notification « 📩 Nouvelle demande urgente » tombe du haut avec rebond sur « alerte ». 17,2–20 s : recul vers le plan large ; impulsions lumineuses de l'agent vers Plans, Clients, Alerte. Contrainte : la notification ne masque jamais le nœud Gmail.

## Frame 4 — Il trie, classe, rapporte (1.jpg)

- status: animated
- src: compositions/04-tri.html
- duration: 8s
- transition_in: whip-left
- scene: travelling gauche→droite le long du flux, compteur 8 → 6 items, zoom sur Google Sheets, carte « 07:00 — Rapport du jour »
- voiceover: "Il trie, classe et remplit vos tableaux. Et chaque matin à sept heures, votre rapport vous attend."
- poster: 6.0
- rules: viewport-change, svg-path-draw, counting-dynamic-scale, spring-pop-entrance
- audio: whoosh 20.0 s, pops 20.6 / 21.0 / 21.5 s (Normalisation, Classification, Garder A et B), chime 24.4 s

20,0–22,4 s : travelling le long de RSS → Normalisation → Classification ; un point cyan voyage sur la connexion, chaque nœud traversé pulse (pops). Étiquettes mono « TRIE » « CLASSE » « REMPLIT » calées sur les mots. 22,4–24,2 s : gros plan **Garder A et B → Extraction**, badge compteur 8 → 6 items. 24,2–28 s : zoom sur **Google Sheets** ; sur « sept heures » la carte « 07:00 · Rapport du jour » (horloge + 3 lignes) monte depuis le bas avec chime. Contrainte : le compteur montre les vrais nombres de la capture (8 et 6 items).

## Frame 5 — Appel à l'action

- status: animated
- src: compositions/05-cta.html
- duration: 8s
- transition_in: zoom-through
- scene: nom de l'entreprise claque, « Automatisez votre business », pastille contact
- voiceover: "[Nom] : automatisez votre business. Contactez-nous dès aujourd'hui."
- poster: 5.5
- rules: kinetic-beat-slam, ambient-glow-bloom, particle-burst
- audio: impact 28.0 s (logo), montée musique 26–28 s, pop 31.9 s (contact)

28,0 s : zoom-through hors de la carte écran ; nom de l'entreprise (variable `brandName`) claque au centre avec impact et éclat de particules cyan. 29,6 s « AUTOMATISEZ VOTRE BUSINESS » monte mot à mot. 31,9 s pastille contact (variable `contact`) surgit avec flèche. 33,5–36 s plan tenu : halo qui respire, la musique conclut. Contrainte : la pastille contact reste lisible au moins 3 s.
