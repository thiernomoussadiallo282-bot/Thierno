# Montage viral — talking-head Thierno #2 « IA qui travaille pendant que vous dormez » (9:16, 38 s)

- Source : filmage 34,8 s (464x832, 60 fps), voix d'origine conservée, upscalé en 1080x1920 30 fps
  (lanczos + léger contraste/saturation/netteté) → `assets/input-video.mp4`.
- Habillage : punch-ins rythmés, cartes animées synchronisées (accroche nuit, système IA en construction,
  « simple chatbot » barré, Observer/Analyser/Exécuter, alerte DANGER + flash rouge, IA → STOP → Humain,
  question + choix en commentaire), sous-titres viraux mot à mot (or = mot actif).
- Outro 3,4 s : « Vous voulez votre propre agent IA ? » + WhatsApp 07 77 56 15 66 + @thierno.agents.ia.
- Audio : voix d'origine + musique discrète + SFX.
- Transcription : Whisper small hors ligne (sherpa-onnx) corrigée à la main, timings par phrase
  ancrés sur les pauses — `transcript.json`. Mots incertains : « Et si des [?] entreprises »,
  « j'veux votre avis », « à la place du propriétaire ».
- Rebuild : `python3 build.py .` génère index.html depuis index.src.tmpl, puis `npx hyperframes render`.
