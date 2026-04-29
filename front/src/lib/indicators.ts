import type { Indicator } from './types';

// définition centrale des 4 indicateurs : libellés, couleurs, formattage
// si on rajoute un indicateur plus tard, c'est ici qu'on le branche
export const INDICATORS: Indicator[] = [
  { id: 'price',  label: 'Prix au m² (DVF)',                    short: 'Prix m²',     unit: '€/m²',      color: '#2d6a4f' },
  { id: 'social', label: 'Logements sociaux financés',          short: 'Log. sociaux', unit: 'logements', color: '#52b788' },
  { id: 'income', label: 'Revenu médian (Filosofi)',            short: 'Rev. médian', unit: '€/an',      color: '#40916c' },  
  { id: 'iai',    label: "Indice d'Accessibilité Immobilière",  short: 'IAI',         unit: 'mois/m²',   color: '#74c69d' },  

  { id: 'environnement',    label: "Indice environnemental",  short: 'ENV',         unit: '%',   color: '#74c69d' },  
  { id: 'mobilite',    label: "Indice de mobilité",  short: 'MOB',         unit: '%',   color: '#74c69d' },  
  { id: 'AES',    label: "Indice d'accessibilité éducation et soin",  short: 'AES',         unit: '%',   color: '#74c69d' },  
  { id: 'reseau',    label: "Indice technologique",  short: 'TEC',         unit: '%',   color: '#74c69d' },

];

export const YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];

// formatte une valeur d'indicateur pour l'affichage
export function fmtVal(v: number | null, id: string): string {
  if (v === null || v === undefined) return '—';
  if (id === 'price')  return Math.round(v).toLocaleString('fr-FR') + ' €/m²';
  if (id === 'social') return Math.round(v).toLocaleString('fr-FR') + ' logements';
  if (id === 'income') return Math.round(v).toLocaleString('fr-FR') + ' €/an';
  if (id === 'iai')    return v.toFixed(1) + ' mois/m²';
  return String(v);
}

// version courte pour la légende (kilo-formatée)
export function fmtShort(v: number | null, id: string): string {
  if (v === null || v === undefined) return '—';
  if (id === 'iai') return v.toFixed(1);
  if (id === 'social') return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(Math.round(v));
  return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(Math.round(v));
}
