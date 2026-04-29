// les indicateurs sélectionnables sur la carte
// les ids matchent les champs de ZoneData (utilisés en z[indicator])
export type IndicatorId =
  | 'prix_m2_median'
  | 'nb_logements_sociaux_finances'
  | 'revenu_median'
  | 'iai'
  | 'score_environnemental'
  | 'score_mobilite'
  | 'score_aes'
  | 'score_reseau';

export interface Indicator {
  id: IndicatorId;
  label: string;
  short: string;
  unit: string;
  color: string;
}

// données renvoyées par l'API pour une zone (arrondissement ou IRIS) sur une année
export interface ZoneData {
  code: string;
  nom: string;
  arrondissement: number;

  // socio-éco
  nb_logements_sociaux_finances: number | null;
  revenu_median: number | null;
  prix_m2_median: number | null;
  iai: number | null;

  // scores thématiques
  score_environnemental: number | null;
  score_reseau: number | null;
  score_transport_collectif: number | null;
  score_velib: number | null;
  score_mobilite: number | null;

  // réseau
  meilleur_operateur_mobile: string | null;
  meilleur_operateur_fibre: string | null;

  // AES (dispo uniquement arrondissement, null pour IRIS)
  score_education: number | null;
  score_sante: number | null;
  score_aes: number | null;
}

export type Granularity = 'arrondissement' | 'iris';
