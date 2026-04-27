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
export const getIndicateursArrondissement = (annee: number) =>
  fetchJson<ZoneData[]>(`/api/indicateurs/arrondissement?annee=${annee}`);

// indicateurs au niveau IRIS (granularité fine, utilisée au zoom)
export const getIndicateursIris = (annee: number) =>
  fetchJson<ZoneData[]>(`/api/indicateurs/iris?annee=${annee}`);
