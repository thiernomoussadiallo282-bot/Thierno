export type Mot = { text: string; start: number; end: number };
export type Scene = { debut: number; fin: number; image: string };
export type ShortProps = {
  fps: number;
  dureeFrames: number;
  accroche: string;
  scenes: Scene[];
  mots: Mot[];
  debutOutro: number;
  audio: string;
  marque: {
    nom: string;
    compte: string;
    whatsapp: string;
    appel_action: string;
    logo_fin: string;
    logo_fichier: string;
    phrase_fin: string;
  };
};
