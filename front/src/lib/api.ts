// petite couche d'accès à l'API backend
// l'URL de base se configure via VITE_API_URL (par défaut localhost:8000 — port standard FastAPI)
import type { ZoneData } from './types';
import type { FeatureCollection } from 'geojson';

const API_BASE = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

console.log(`API_BASE: ${API_BASE}`);

async function fetchJson<T>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`);
  if (!r.ok) throw new Error(`API ${path} : ${r.status}`);
  return r.json();
}

// les deux geojson nécessaires à la carte — chargés une fois au démarrage
export const getArrondissementsGeojson = () =>
  fetchJson<FeatureCollection>('/api/geo/arrondissements');

export const getIrisGeojson = () =>
  fetchJson<FeatureCollection>('/api/geo/iris');

// indicateurs agrégés au niveau arrondissement
export async function getIndicateursArrondissement(annee: number): Promise<ZoneData[]> {
  const raw = await fetchJson<any[]>(`/api/indicateurs/arrondissement?annee=${annee}`);
  return raw.map(d => {
    const code_insee = '751' + String(d.arrondissement).padStart(2, '0');
    const num_arr_str = `${d.arrondissement}${d.arrondissement === 1 ? 'er' : 'e'} arrondissement`
    return {
      ...d,
      level: 'arrondissement',
      code: String(d.arrondissement),
      nom: `${code_insee} - ${num_arr_str}`,
      score_education: d.score_education ?? null,
      score_sante: d.score_sante ?? null,
      score_aes: d.score_aes ?? null,
    }
  });
}

// indicateurs au niveau IRIS (granularité fine, utilisée au zoom)
export async function getIndicateursIris(annee: number): Promise<ZoneData[]> {
  const raw = await fetchJson<any[]>(`/api/indicateurs/iris?annee=${annee}`);
  return raw.map(d => ({
    ...d,
    level: 'iris',
    code: d.code_iris,
    nom: `${d.code_iris} - ${d.nom_iris}`,
    score_education: d.score_education ?? null,
    score_sante: d.score_sante ?? null,
    score_aes: d.score_aes ?? null,
  }));
}
