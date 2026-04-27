// les 4 indicateurs gérés par le front
// les ids matchent ceux exposés par l'API
export type IndicatorId = 'price' | 'social' | 'income' | 'iai';

export interface Indicator {
  id: IndicatorId;
  label: string;
  short: string;
  unit: string;
  color: string;
}

// données indicateurs renvoyées par l'API pour une zone (arrondissement ou IRIS) sur une année
export interface ZoneData {
  // identifiant : code_arinsee (75101) pour les arrondissements, code_iris (751010101) pour IRIS
  code: string;
  // nom lisible
  name: string;
  // arrondissement parent (1 à 20)
  arrondissement: number;
  // valeurs des indicateurs — null si pas dispo pour l'année demandée
  price: number | null;
  social: number | null;
  income: number | null;
  iai: number | null;
}

// niveau de granularité actuellement affiché sur la carte
export type Granularity = 'arrondissement' | 'iris';
