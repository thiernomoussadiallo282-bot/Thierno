import "@fontsource/montserrat/700.css";
import "@fontsource/montserrat/900.css";
import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { Mot, Scene, ShortProps } from "./types";

const NAVY = "#0b1f3a";
const OR = "#f4b942";
const POLICE = "Montserrat, sans-serif";
const FONDU = 0.35; // secondes de fondu enchaîné entre deux images

export const Short: React.FC<ShortProps> = (p) => {
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, fontFamily: POLICE }}>
      {p.scenes.map((s, i) => (
        <Sequence key={i} from={f(s.debut)} durationInFrames={Math.max(1, f(s.fin - s.debut + FONDU))}>
          <ImageAnimee scene={s} index={i} premier={i === 0} />
        </Sequence>
      ))}
      <Voiles />
      <Sequence from={0} durationInFrames={f(p.debutOutro)}>
        <SousTitres mots={p.mots} />
      </Sequence>
      <Sequence from={0} durationInFrames={f(2.8)}>
        <Accroche texte={p.accroche} />
      </Sequence>
      <Filigrane nom={p.marque.nom} />
      <BarreProgression debutOutro={p.debutOutro} />
      <Sequence from={f(p.debutOutro)}>
        <Outro marque={p.marque} />
      </Sequence>
      <Audio src={staticFile(p.audio)} />
    </AbsoluteFill>
  );
};

const ImageAnimee: React.FC<{ scene: Scene; index: number; premier: boolean }> = ({ scene, index, premier }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const duree = (scene.fin - scene.debut + FONDU) * fps;
  const opacite = premier ? 1 : interpolate(frame, [0, FONDU * fps], [0, 1], { extrapolateRight: "clamp" });
  const t = interpolate(frame, [0, duree], [0, 1], { extrapolateRight: "clamp" });
  const zoomAvant = index % 2 === 0;
  const echelle = zoomAvant ? 1.06 + 0.12 * t : 1.18 - 0.12 * t;
  const dx = (index % 3 - 1) * 40 * (t - 0.5);
  // petit « punch » à l'entrée de chaque image
  const punch = premier ? 0 : interpolate(frame, [0, 8], [0.06, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ opacity: opacite, overflow: "hidden" }}>
      <Img
        src={staticFile(scene.image)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `translateX(${dx}px) scale(${echelle + punch})` }}
      />
    </AbsoluteFill>
  );
};

const Voiles: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "linear-gradient(180deg, rgba(11,31,58,0.55) 0%, rgba(11,31,58,0) 22%, rgba(11,31,58,0) 52%, rgba(11,31,58,0.75) 78%, rgba(11,31,58,0.9) 100%)",
    }}
  />
);

/** Sous-titres mot à mot : groupes de 3 mots maximum, mot prononcé en or. */
const SousTitres: React.FC<{ mots: Mot[] }> = ({ mots }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const groupes = React.useMemo(() => grouper(mots), [mots]);
  const g = groupes.find((x, i) => t >= x[0].start - 0.05 && t < (groupes[i + 1]?.[0].start ?? x[x.length - 1].end + 0.6) - 0.05);
  if (!g) return null;
  // un mot très long (ex. @compte) réduit la taille pour rester dans le cadre
  const plusLong = Math.max(...g.map((m) => m.text.length));
  const taille = Math.min(86, Math.floor(860 / (plusLong * 0.74)));
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center" }}>
      <div style={{ position: "absolute", top: 1180, left: 70, right: 150, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0 24px" }}>
        {g.map((m, i) => {
          const actif = t >= m.start - 0.04 && t < m.end + 0.05;
          const vu = t >= m.start - 0.04;
          const s = spring({ frame: frame - Math.round((m.start - 0.04) * fps), fps, config: { damping: 12, stiffness: 220 } });
          return (
            <span
              key={i}
              style={{
                fontWeight: 900,
                fontSize: taille,
                lineHeight: 1.12,
                textTransform: "uppercase",
                letterSpacing: "-0.02em",
                color: actif ? OR : "#ffffff",
                WebkitTextStroke: "14px #000",
                paintOrder: "stroke fill",
                textShadow: "0 10px 28px rgba(0,0,0,0.55)",
                opacity: vu ? 1 : 0,
                transform: `scale(${vu ? 0.7 + 0.3 * s : 0.7})`,
                display: "inline-block",
              }}
            >
              {m.text.replace(/[.,;:]$/, "")}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

function grouper(mots: Mot[]): Mot[][] {
  const out: Mot[][] = [];
  let cour: Mot[] = [];
  mots.forEach((m, i) => {
    const prec = mots[i - 1];
    const coupe = cour.length >= 3 || (prec && /[.,!?;:]$/.test(prec.text)) || (prec && m.start - prec.end > 0.45);
    if (coupe && cour.length) {
      out.push(cour);
      cour = [];
    }
    cour.push(m);
  });
  if (cour.length) out.push(cour);
  return out;
}

const Accroche: React.FC<{ texte: string }> = ({ texte }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 14 } });
  const sortie = interpolate(frame, [2.4 * fps, 2.8 * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const souligne = interpolate(frame, [8, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", top: 330, left: 70, right: 150, opacity: sortie, transform: `translateY(${(1 - s) * 60}px) scale(${0.9 + 0.1 * s})` }}>
      <div
        style={{
          display: "inline",
          fontWeight: 900,
          fontSize: 92,
          lineHeight: 1.08,
          color: "#fff",
          letterSpacing: "-0.03em",
          WebkitTextStroke: "12px " + NAVY,
          paintOrder: "stroke fill",
          textShadow: "0 12px 30px rgba(0,0,0,0.5)",
        }}
      >
        {texte}
      </div>
      <div style={{ marginTop: 22, height: 14, width: `${souligne * 62}%`, background: OR, borderRadius: 8 }} />
    </div>
  );
};

const Logo: React.FC<{ taille: number }> = ({ taille }) => (
  <svg width={taille} height={taille} viewBox="0 0 40 40">
    <rect width="40" height="40" rx="11" fill="#1d4373" />
    <path d="M13 11.5h6.2a8.5 8.5 0 0 1 0 17H13z" fill="none" stroke="#fff" strokeWidth="3.2" strokeLinejoin="round" />
    <circle cx="29.2" cy="11.2" r="3.3" fill={OR} />
  </svg>
);

const Filigrane: React.FC<{ nom: string }> = ({ nom }) => {
  const [a, b] = [nom.replace(/\s*IA$/, ""), /IA$/.test(nom) ? "IA" : ""];
  return (
    <div
      style={{
        position: "absolute", left: 60, top: 236, display: "flex", alignItems: "center", gap: 12,
        padding: "8px 20px 8px 10px", borderRadius: 999, background: "rgba(11,31,58,0.82)",
        color: "#fff", fontWeight: 900, fontSize: 30,
      }}
    >
      <Logo taille={40} />
      {a} <span style={{ color: OR }}>{b}</span>
    </div>
  );
};

const BarreProgression: React.FC<{ debutOutro: number }> = ({ debutOutro }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const v = interpolate(frame, [0, debutOutro * fps], [0, 1], { extrapolateRight: "clamp" });
  return <div style={{ position: "absolute", left: 0, top: 0, height: 10, width: `${v * 100}%`, background: OR }} />;
};

const Outro: React.FC<{ marque: ShortProps["marque"] }> = ({ marque }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entree = spring({ frame, fps, config: { damping: 16 } });
  const el = (delai: number) => {
    const s = spring({ frame: frame - delai, fps, config: { damping: 13 } });
    return { opacity: Math.min(1, s * 1.4), transform: `translateY(${(1 - s) * 50}px)` };
  };
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 30%, #1d4373 0%, ${NAVY} 70%)`,
        transform: `translateY(${(1 - entree) * 1920}px)`,
        alignItems: "center",
        paddingTop: 330,
        color: "#fff",
        textAlign: "center",
      }}
    >
      <div style={{ ...el(4), display: "flex", alignItems: "center", gap: 20, fontWeight: 900, fontSize: 64 }}>
        <Logo taille={90} /> {marque.nom.replace(/\s*IA$/, "")} <span style={{ color: OR }}>IA</span>
      </div>
      <div style={{ ...el(10), marginTop: 70, fontWeight: 900, fontSize: 70, lineHeight: 1.1, padding: "0 90px" }}>
        Vous voulez votre <span style={{ color: OR }}>propre agent IA</span> ?
      </div>
      <div style={{ ...el(18), marginTop: 70, background: "#25d366", color: "#062b14", borderRadius: 36, padding: "26px 60px", boxShadow: "0 20px 60px rgba(37,211,102,0.35)" }}>
        <div style={{ fontWeight: 800, fontSize: 38 }}>WhatsApp</div>
        <div style={{ fontWeight: 900, fontSize: 84, letterSpacing: "0.02em" }}>{marque.whatsapp}</div>
      </div>
      <div style={{ ...el(26), marginTop: 60, fontWeight: 800, fontSize: 44 }}>
        {marque.appel_action} : <span style={{ color: OR }}>{marque.compte}</span>
      </div>
    </AbsoluteFill>
  );
};
