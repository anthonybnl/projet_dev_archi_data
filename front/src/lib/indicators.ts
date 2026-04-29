import type { Indicator } from './types';

// définition centrale des indicateurs : libellés, couleurs, formattage
// si on rajoute un indicateur plus tard, c'est ici qu'on le branche
export const INDICATORS: Indicator[] = [
  { id: 'prix_m2_median',               label: 'Prix au m² (DVF)',                           short: 'Prix m²',     unit: '€/m²',      color: '#2d6a4f' },
  { id: 'nb_logements_sociaux_finances', label: 'Logements sociaux financés',                 short: 'Log. sociaux', unit: 'logements', color: '#52b788' },
  { id: 'revenu_median',                label: 'Revenu médian (Filosofi)',                    short: 'Rev. médian', unit: '€/an',      color: '#40916c' },
  { id: 'iai',                           label: "Indice d'Accessibilité Immobilière",         short: 'IAI',         unit: 'mois/m²',   color: '#74c69d' },
  { id: 'score_environnemental',         label: 'Indice environnemental',                     short: 'ENV',         unit: '%',         color: '#74c69d' },
  { id: 'score_mobilite',               label: 'Indice de mobilité',                          short: 'MOB',         unit: '%',         color: '#74c69d' },
  { id: 'score_aes',                    label: "Indice d'accessibilité éducation et soin",    short: 'AES',         unit: '%',         color: '#74c69d' },
  { id: 'score_reseau',                 label: 'Indice technologique',                        short: 'TEC',         unit: '%',         color: '#74c69d' },
];

export const YEARS = [2020, 2021, 2022, 2023, 2024, 2025];

// formatte une valeur d'indicateur pour l'affichage
export function fmtVal(v: number | null, id: string): string {
  if (v === null || v === undefined) return '—';
  if (id === 'prix_m2_median')  return Math.round(v).toLocaleString('fr-FR') + ' €/m²';
  if (id === 'nb_logements_sociaux_finances') return Math.round(v).toLocaleString('fr-FR') + ' logements';
  if (id === 'revenu_median') return Math.round(v).toLocaleString('fr-FR') + ' €/an';
  if (id === 'iai')    return v.toFixed(1) + ' mois/m²';
  if (id.startsWith('score_')) return (v * 100).toFixed(1).replace('.', ',') + ' %';
  return String(v);
}   

// version courte pour la légende (kilo-formatée)
export function fmtShort(v: number | null, id: string): string {
  if (v === null || v === undefined) return '—';
  if (id === 'iai') return v.toFixed(1);
  if (id === 'nb_logements_sociaux_finances') return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(Math.round(v));
  if (id.startsWith('score_')) return (v * 100).toFixed(1).replace('.', ',') + '%';
  return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(Math.round(v));
}
