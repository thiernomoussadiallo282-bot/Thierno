# Short quotidien automatique — Diallo IA

Du lundi au vendredi, ce pipeline transforme une ligne de `idees.csv` en un Short vertical de 60 secondes
(1080×1920), prêt à publier sur YouTube Shorts, TikTok, Facebook et Instagram.

```
idees.csv ─► script (Claude) ─► voix off (Edge TTS) ─► mots horodatés (Whisper)
                         └─► illustrations, style fixe (Pollinations / Flux)
musique libre (générée) ─► mixage + ducking + -14 LUFS ─► montage Remotion ─► short.mp4
                                                                 └─► titre, description, hashtags, SRT, miniature
```

| Étape | Outil | Fichier |
|---|---|---|
| Script, accroche, titre, description, hashtags | Claude (`claude-opus-5-5`) | `pipeline/script.py` |
| Voix off masculine française | Edge TTS (`fr-FR-RemyMultilingualNeural`), traitement « voix radio » | `pipeline/voix.py` |
| Photos réalistes dans un style fixe | Pollinations (Flux), style et graine fixes | `pipeline/images.py` |
| Sous-titres mot à mot | Whisper (faster-whisper `small`), recalé sur le texte exact | `pipeline/transcription.py` |
| Musique libre de droits | synthétisée par le pipeline (ou vos musiques dans `musiques/`) | `pipeline/musique.py` |
| Montage 1080×1920, 30 i/s | Remotion | `remotion/src/Short.tsx` |

## Ce que contient la vidéo

- 0–2,8 s : accroche en gros titre, puis les illustrations s'enchaînent (zoom lent, fondus).
- Sous-titres mot à mot : 3 mots maximum à l'écran, mot prononcé en jaune doré.
- Filigrane « Diallo IA » et barre de progression en haut.
- Fin : dès que la voix lit l'appel à l'action, écran simple bleu nuit avec le logo « Afrique Racontée »,
  « Vous voulez votre propre agent IA ? », le numéro WhatsApp en très grand et le compte à suivre.
  Pour utiliser votre vrai logo, déposez-le dans `shorts/marque/logo.png` (PNG, fond transparent de préférence) ;
  sinon un logo typographique (carte de l'Afrique + nom) est dessiné automatiquement.
- Textes placés hors des zones cachées par l'interface TikTok/YouTube.

## Ce qui est produit chaque jour

Dans `sorties/AAAA-MM-JJ-sujet/` :

- `short.mp4` : la vidéo
- `publication.txt` : titre, description et hashtags à copier-coller
- `sous-titres.srt`, `miniature.jpg`, `metadata.json`
- `script.json`, `mots.json` : le script et les temps de chaque mot

Sur GitHub, chaque Short du jour est aussi publié dans **Releases** : on peut le télécharger
depuis le téléphone, puis le poster.

## Mise en route sur GitHub (exécution automatique chaque jour)

1. Dans le dépôt GitHub : **Settings → Secrets and variables → Actions → New repository secret**.
   Nom : `ANTHROPIC_API_KEY`, valeur : votre clé API Claude (console.anthropic.com).
   Sans clé, le pipeline fonctionne quand même avec un script modèle, moins bon.
2. Le workflow `.github/workflows/short-quotidien.yml` tourne du lundi au vendredi vers 06:47 (heure d'Abidjan), soit 5 vidéos par semaine.
3. Pour lancer un Short tout de suite : onglet **Actions → Short quotidien → Run workflow**.
   Cochez « Essai » pour tester sans consommer d'idée.
4. Chaque exécution réussie passe l'idée à `fait` dans `idees.csv` et crée une release.

## Ajouter des idées

Une ligne par idée dans `idees.csv` :

```
id,idee,angle,statut,date
11,Mon nouveau sujet,Ce que je veux faire ressentir ou montrer,a_faire,
```

Le pipeline prend la première idée `a_faire`. Quand il n'en reste plus, il s'arrête et le dit.

## Lancer sur un ordinateur

Il faut Python 3.10+, Node 18+ et ffmpeg :

```bash
cd shorts
pip install -r requirements.txt
npm ci --prefix remotion
export ANTHROPIC_API_KEY=...          # facultatif
python -m pipeline.main               # prochaine idée
python -m pipeline.main --idee 4 --essai
```

## Réglages (`config.json`)

- `images.style` et `images.graine` : le style visuel fixe de toutes les vidéos (photos réalistes, personnes ivoiriennes, étalonnage bleu-doré). Changez-les pour une nouvelle identité.
- `voix.edge_voix` : la voix. Par défaut Rémy (masculine, expressive), légèrement plus grave (`edge_tonalite`)
  et un peu plus rapide (`vitesse_base`) pour plus d'énergie. Pour comparer les voix masculines :
  **Actions → Short quotidien → Run workflow**, cochez « Seulement écouter les voix », puis téléchargez
  l'artefact `echantillons-voix` (6 voix, même accroche). Recopiez ensuite le nom de la voix choisie
  (par exemple `fr-FR-HenriNeural`, `fr-CA-JeanNeural`) dans `config.json`.
- `voix.traitement_radio` : égalisation + compression pour une voix pleine et claire au téléphone.
- `voix.mots_cibles` : longueur du script. La vitesse de la voix s'ajuste seule pour tenir en 60 s.
- `marque` : nom (filigrane), compte, numéro WhatsApp, `logo_fin` (nom affiché à la fin), `phrase_fin`.
- `musique.volume_db` : volume de la musique sous la voix (−20 dB par défaut).

## Bon à savoir

- **Honnêteté** : la consigne donnée à Claude interdit les chiffres, clients et témoignages inventés.
  Relisez quand même `publication.txt` avant de publier.
- **Remotion** est gratuit pour un particulier ou une entreprise de 3 personnes maximum. Au-delà,
  une licence est nécessaire (remotion.dev/license).
- **Edge TTS** utilise le service de synthèse vocale de Microsoft Edge, sans compte. En cas d'échec il
  est réessayé 4 fois. Kokoro (local) n'a qu'une voix française féminine : il ne sert de secours que si
  vous ajoutez `"kokoro"` dans `voix.secours`.
- **Pollinations** est gratuit et sans clé (une image toutes les 45 s environ, d’où environ 8 minutes par vidéo ; ajoutez un secret `POLLINATIONS_TOKEN`, jeton gratuit sur auth.pollinations.ai, pour aller plus vite). S'il ne répond pas, des illustrations de secours sont
  dessinées localement dans la même palette, pour que la vidéo du jour sorte quand même.
- **Whisper** : si le modèle ne peut pas être chargé, les temps des mots sont estimés
  (`metadata.json` → `"sous_titres": "estimation"`).
- La publication sur YouTube et TikTok reste manuelle : le pipeline prépare tout, vous publiez.
