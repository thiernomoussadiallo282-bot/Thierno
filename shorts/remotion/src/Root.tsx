import { Composition } from "remotion";
import { Short } from "./Short";
import type { ShortProps } from "./types";

const exemple: ShortProps = {
  fps: 30,
  dureeFrames: 1800,
  accroche: "Exemple d'accroche",
  scenes: [],
  mots: [],
  debutOutro: 56.5,
  audio: "mix.wav",
  marque: { nom: "Diallo IA", compte: "@thierno.agents.ia", whatsapp: "07 77 56 15 66", appel_action: "Abonnez-vous pour la suite" },
};

export const Root: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={1800}
    defaultProps={exemple}
    calculateMetadata={({ props }) => ({ durationInFrames: props.dureeFrames, fps: props.fps })}
  />
);
