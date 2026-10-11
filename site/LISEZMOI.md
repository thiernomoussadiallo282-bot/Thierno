# Site Diallo IA — guide rapide

Site statique (HTML, CSS, JavaScript) : aucun serveur, aucune base de données, aucun traceur.

## Fichiers

```
index.html                  page d'accueil
mentions-legales.html       mentions légales
confidentialite.html        politique de confidentialité
assets/css/style.css        styles
assets/js/main.js           menu, onglets des démos, animations, liens WhatsApp
assets/fonts/               police Inter (hébergée avec le site)
assets/img/thierno.webp     photo du fondateur (480 × 480)
assets/img/og-image.png     image d'aperçu pour WhatsApp / Facebook (1200 × 630)
assets/icons/               logo, favicons
```

## Ouvrir le site sur votre ordinateur

Double-cliquez sur `index.html` : il s'ouvre dans votre navigateur.

## Mettre en ligne gratuitement sur Netlify

1. Allez sur https://app.netlify.com/signup et créez un compte gratuit (avec votre e-mail ou votre compte GitHub).
2. Une fois connecté, ouvrez https://app.netlify.com/drop
3. Glissez-déposez **le dossier `site` entier** (celui qui contient `index.html`) dans la zone indiquée.
4. Après quelques secondes, Netlify affiche l'adresse de votre site, du type `https://nom-au-hasard.netlify.app`.
5. Pour une adresse plus jolie : **Site configuration → Change site name**, puis tapez par exemple `diallo-ia`. L'adresse devient `https://diallo-ia.netlify.app` (si le nom est libre).
6. **Important pour l'aperçu sur WhatsApp et Facebook** : ouvrez `index.html` avec un éditeur de texte (Bloc-notes, VS Code…), faites « Rechercher / Remplacer » de `ADRESSE-DU-SITE` par votre adresse sans `https://` (exemple : `diallo-ia.netlify.app`), enregistrez, puis redéposez le dossier dans Netlify (**Deploys → glisser-déposer**).
7. Dans `mentions-legales.html`, complétez la ligne « Hébergeur » (un exemple pour Netlify est déjà écrit en commentaire juste au-dessus).

Pour vérifier l'aperçu du lien : https://developers.facebook.com/tools/debug/ (collez votre adresse).

## Remplacer la photo

Remplacez `assets/img/thierno.webp` par votre photo, au format **carré** (480 × 480 px conseillé, moins de 200 Ko). Pour convertir une photo en WebP gratuitement : https://squoosh.app
Gardez exactement le même nom de fichier. Si le fichier est absent, le monogramme « TD » s'affiche automatiquement.

## Activer la section Témoignages (quand vous aurez de vrais avis)

Dans `index.html`, cherchez `TÉMOIGNAGES-DÉBUT` :

1. Supprimez la ligne `TÉMOIGNAGES-DÉBUT` et la ligne `TÉMOIGNAGES-FIN`.
2. Remplacez chaque texte entre crochets par un vrai avis (avec l'accord écrit du client) : texte, nom, fonction, entreprise, ville.
3. Supprimez les cartes en trop si vous avez moins de trois avis.

N'ajoutez jamais d'avis inventé ni de note étoilée non vérifiable.

## Modifier un message WhatsApp pré-rempli

Chaque bouton WhatsApp a un attribut `data-wa="…"` qui contient le message. Modifiez le texte de `data-wa` : le script du site l'encode automatiquement au chargement de la page.
