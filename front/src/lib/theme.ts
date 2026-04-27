// palette extraite directement du design Claude Design
// on garde les mêmes noms que dans le mock pour s'y retrouver
export const C = {
  bg: '#f5f4f1',
  panel: '#ffffff',
  border: '#e8e4de',
  borderMid: '#d4d0ca',
  accent: '#2d6a4f',
  accentHover: '#245840',
  accentMid: '#52b788',
  accentLight: '#e8f5ee',
  accentXLight: '#f0faf4',
  text: '#1a1a18',
  textMid: '#5e5e58',
  textLight: '#9e9e98',
  mapBg: '#e9e5db',
  mapSat: '#2a3420',
};

// rampe verte utilisée pour la coloration choroplèthe
export const RAMP = ['#d8f3dc', '#95d5b2', '#52b788', '#40916c', '#2d6a4f', '#1b4332'];

function hexRgb(h: string): [number, number, number] {
  return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
}
function rgbHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}
function lerpCol(a: string, b: string, t: number): string {
  const [r1, g1, b1] = hexRgb(a);
  const [r2, g2, b2] = hexRgb(b);
  return rgbHex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t);
}
export function rampColor(t: number): string {
  // t entre 0 et 1, on choisit deux couleurs adjacentes de la rampe et on interpole
  const n = RAMP.length - 1;
  const i = Math.min(Math.floor(t * n), n - 1);
  return lerpCol(RAMP[i], RAMP[i + 1], (t * n) - i);
}
