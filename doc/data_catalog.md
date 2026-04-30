# Data Catalog — Urban Data Explorer

Catalogue de toutes les sources de données intégrées dans le pipeline, classées par domaine.  
Chaque entrée documente l'origine, la structure, la qualité et la justification de son inclusion.

---

## 1. Données Obligatoires (Logement & Revenus)

### 1.1 Demandes de Valeurs Foncières (DVF) — 2021 à 2025

| Champ | Valeur |
|---|---|
| **Fournisseur** | data.gouv.fr / DGFiP |
| **Format** | CSV zippé (`.txt.zip`) |
| **Fréquence de mise à jour** | Annuelle |
| **Couverture temporelle** | 2021 — 2025 |
| **Granularité** | Transaction immobilière individuelle |
| **Colonnes clés** | `code_postal`, `valeur_fonciere`, `surface_reelle_bati`, `type_local`, `date_mutation` |
| **Qualité** | Très bonne — données fiscales officielles. Quelques transactions sans surface (exclus du calcul m²). |
| **Contraintes** | Fichiers volumineux (~500 Mo/an). Filtrage sur `code_postal` commençant par `75` nécessaire. |
| **Indicateurs produits** | Prix médian au m², volume de transactions par arrondissement et par année |
| **Justification** | Source de référence nationale pour les transactions immobilières. Indispensable pour l'indicateur principal du CDC. |

### 1.2 Logements Sociaux Financés à Paris (RPLS)

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;` comme séparateur) |
| **Fréquence de mise à jour** | Annuelle |
| **Granularité** | Logement individuel |
| **Colonnes clés** | `arrondissement`, `nombre_logements`, `type_financement`, `annee_livraison` |
| **Qualité** | Bonne — recensement exhaustif des logements financés par la ville. |
| **Contraintes** | Pas de coordonnées GPS pour tous les biens. |
| **Indicateurs produits** | Part du parc social par arrondissement, évolution annuelle |
| **Justification** | Exigé par le CDC pour mesurer les enjeux sociaux du logement parisien. |

### 1.3 FILOSOFI — Revenus par IRIS (2018–2021)

| Champ | Valeur |
|---|---|
| **Fournisseur** | INSEE |
| **Format** | CSV zippé |
| **Fréquence de mise à jour** | Annuelle |
| **Couverture temporelle** | 2018 — 2021 |
| **Granularité** | Zone IRIS |
| **Colonnes clés** | `IRIS`, `MED18` (revenu médian), `TP6018` (taux pauvreté) |
| **Qualité** | Très bonne — source officielle INSEE. Secret statistique pour les IRIS de moins de 500 habitants. |
| **Contraintes** | Valeurs supprimées pour petits IRIS (secret statistique INSEE). |
| **Indicateurs produits** | Revenu médian par IRIS/arrondissement, indicateur d'accessibilité (ratio prix/revenu) |
| **Justification** | Seule source permettant de croiser prix de l'immobilier et niveau de vie pour l'indicateur d'accessibilité du CDC. |

---

## 2. Environnement

### 2.1 Arbres de Paris

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Fréquence de mise à jour** | Continue |
| **Granularité** | Arbre individuel |
| **Colonnes clés** | `arrondissement`, `libellefrancais`, `hauteurenm`, `geom_x_y` |
| **Qualité** | Très bonne — inventaire géolocalisé de tous les arbres sur voirie parisienne. ~200k entrées. |
| **Indicateurs produits** | Densité arborée par arrondissement (composant score environnemental, poids 30%) |
| **Justification** | Indicateur composite "qualité environnementale". Proxy de la végétalisation et confort thermique. |

### 2.2 Espaces Verts

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Espace vert individuel |
| **Colonnes clés** | `arrondissement`, `surface_totale_reelle`, `type_espace_vert` |
| **Qualité** | Bonne — périmètres officiels de la DAP (Direction des Espaces Verts). |
| **Indicateurs produits** | Surface verte par habitant par arrondissement (poids 40% dans score environnemental) |
| **Justification** | Indicateur de santé urbaine et de confort de vie, corrélé à la valeur immobilière. |

### 2.3 Îlots de Fraîcheur

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Équipement ou zone de fraîcheur |
| **Colonnes clés** | `arrondissement`, `type_equipement`, `acces_libre` |
| **Qualité** | Bonne — inventaire mis à jour chaque été. |
| **Indicateurs produits** | Nombre d'îlots de fraîcheur par arrondissement (poids 20% dans score environnemental) |
| **Justification** | Indicateur d'adaptation climatique, pertinent pour évaluer la résilience des quartiers à la chaleur. |

### 2.4 Points d'Apport Volontaire — Stations Trilib

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Station de collecte sélective |
| **Colonnes clés** | `arrondissement`, `adresse`, `geom` |
| **Qualité** | Bonne — mise à jour régulière par la ville. |
| **Indicateurs produits** | Densité de points de collecte (poids 10% dans score environnemental) |
| **Justification** | Indicateur de qualité de service urbain et d'engagement écologique du quartier. |

---

## 3. Mobilité

### 3.1 Stations Vélib

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Station individuelle |
| **Colonnes clés** | `arrondissement`, `capacity`, `stationcode`, `coordonnees_geo` |
| **Qualité** | Très bonne — données en quasi temps réel. |
| **Indicateurs produits** | Nombre de bornes et capacité Vélib par arrondissement |
| **Justification** | Mesure l'offre en mobilité douce, indicateur clé de qualité de vie urbaine. |

### 3.2 Arrêts de Lignes IDFM

| Champ | Valeur |
|---|---|
| **Fournisseur** | Île-de-France Mobilités (IDFM) |
| **Format** | CSV (`;`) |
| **Granularité** | Arrêt de transport en commun |
| **Colonnes clés** | `arrêt_nom`, `code_insee`, `mode_transport`, `lat`, `lon` |
| **Qualité** | Très bonne — référentiel officiel IDFM. |
| **Indicateurs produits** | Densité d'arrêts TC par arrondissement, carte des arrêts |
| **Justification** | Reflète l'accessibilité aux transports en commun, facteur majeur de désirabilité des quartiers. |

### 3.3 Gares et Stations Metro/RER

| Champ | Valeur |
|---|---|
| **Fournisseur** | data.gouv.fr |
| **Format** | CSV |
| **Granularité** | Station de métro/RER |
| **Colonnes clés** | `nom_gare`, `code_commune_insee`, `latitude`, `longitude`, `ligne` |
| **Qualité** | Bonne — source gouvernementale. Complète pour le réseau RATP. |
| **Indicateurs produits** | Nombre de stations par arrondissement, carte du réseau lourd |
| **Justification** | Complète les arrêts IDFM avec le réseau lourd (métro, RER). |

---

## 4. Réseau Télécom

### 4.1 Couvertures Théoriques Mobile (4G/5G) — ARCEP

| Champ | Valeur |
|---|---|
| **Fournisseur** | ARCEP (data.arcep.fr) |
| **Format** | GeoPackage (`.gpkg`) |
| **Fréquence de mise à jour** | Trimestrielle |
| **Granularité** | Polygone de couverture par opérateur (Bouygues, Free, Orange, SFR) |
| **Qualité** | Officielle — données déclaratives des opérateurs validées par l'ARCEP. |
| **Contraintes** | Fichiers volumineux (`.gpkg`). Intersection spatiale avec les IRIS nécessaire. |
| **Indicateurs produits** | Taux de couverture 4G/5G par arrondissement par opérateur |
| **Justification** | Indicateur composite réseau — pilier "Mobile" (45% du score réseau total). |

### 4.2 Qualité de Service — Mesures QoS Habitations

| Champ | Valeur |
|---|---|
| **Fournisseur** | ARCEP |
| **Format** | CSV |
| **Granularité** | Mesure de débit/latence par département |
| **Colonnes clés** | `operateur`, `debit_dl_median`, `taux_reussite`, `latence_mediane` |
| **Qualité** | Officielle — mesures réalisées par l'ARCEP sur le terrain. |
| **Indicateurs produits** | Score de qualité réseau (débit, fiabilité, latence) — pilier "Qualité" (30% du score réseau) |
| **Justification** | La qualité effective du réseau est distincte de la couverture théorique. Indispensable pour un score réseau représentatif. |

### 4.3 Antennes Relais

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Antenne individuelle |
| **Colonnes clés** | `arrondissement`, `operateur`, `type_antenne`, `lat`, `lon` |
| **Qualité** | Bonne — inventaire Paris uniquement. |
| **Indicateurs produits** | Densité d'antennes par arrondissement (composant densité du score Mobile) |
| **Justification** | Proxy de l'intensité d'infrastructure réseau dans un quartier. |

### 4.4 Déploiement Fibre (Immeubles) — ARCEP 2025 T4

| Champ | Valeur |
|---|---|
| **Fournisseur** | ARCEP |
| **Format** | CSV |
| **Granularité** | Immeuble |
| **Colonnes clés** | `code_iris`, `nb_locaux_raccordables`, `nb_pm_actifs` |
| **Qualité** | Très bonne — source exhaustive nationale. |
| **Indicateurs produits** | Taux de déploiement fibre et taux de PM actifs par IRIS — pilier "Fibre" (25% du score réseau) |
| **Justification** | La fibre est un indicateur de modernité de l'infrastructure et d'attractivité résidentielle. |

---

## 5. Éducation, Action Sociale (AES)

### 5.1 Écoles Élémentaires

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Établissement |
| **Colonnes clés** | `nom`, `adresse`, `arrondissement`, `lat`, `lon` |
| **Qualité** | Bonne — annuaire officiel des écoles parisiennes. |
| **Indicateurs produits** | Carte des écoles élémentaires, dénombrement par arrondissement |

### 5.2 Écoles Maternelles

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Établissement |
| **Colonnes clés** | `nom`, `adresse`, `arrondissement`, `lat`, `lon` |
| **Qualité** | Bonne. 102 établissements "Polyvalents" présents dans les deux fichiers (maternelle + élémentaire) — dédupliqués en Silver. |
| **Indicateurs produits** | Carte des maternelles |

### 5.3 Collèges

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Établissement |
| **Colonnes clés** | `nom`, `adresse`, `arrondissement`, `lat`, `lon` |
| **Indicateurs produits** | Indicateur E2 (nb collèges / pop 11-17 ans), carte des collèges |

### 5.4 Effectifs Scolaires par Classe

| Champ | Valeur |
|---|---|
| **Fournisseur** | data.gouv.fr / MEN |
| **Format** | CSV |
| **Granularité** | École par année scolaire |
| **Colonnes clés** | `Code département`, `Nombre total d'élèves en élémentaire hors ULIS`, `Code Postal` |
| **Qualité** | Très bonne — données officielles Éducation Nationale. |
| **Contraintes** | Utilisé comme proxy pour "places primaires" (pas une capacité d'accueil théorique). |
| **Indicateurs produits** | Indicateur E1 (élèves élémentaires / pop 3-10 ans) |
| **Justification** | Permet de mesurer la pression scolaire dans les arrondissements. |

### 5.5 Établissements Hospitaliers Franciliens

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.iledefrance.fr |
| **Format** | CSV (`;`) |
| **Granularité** | Établissement |
| **Colonnes clés** | `RAISON_SOCIALE`, `ADRESSE_COMPLETE`, `CP_VILLE`, `CATEGORIE_DE_L_ETABLISSEMENT`, `lat`, `lon` |
| **Qualité** | Bonne — 237 établissements identifiés sur Paris. |
| **Indicateurs produits** | Carte des hôpitaux et cliniques, catégorisés (CHR, clinique, CMP) |

### 5.6 Base Permanente des Équipements — Santé (BPE INSEE)

| Champ | Valeur |
|---|---|
| **Fournisseur** | INSEE |
| **Format** | XLSX zippé |
| **Granularité** | Commune / Arrondissement (ARM) |
| **Colonnes clés** | `Médecin généraliste`, `Infirmier`, `Centre de santé`, `Pharmacie` |
| **Qualité** | Très bonne — référentiel INSEE exhaustif. |
| **Indicateurs produits** | Indicateurs S1 à S4 (médecins, infirmiers, centres, pharmacies par habitant), score santé |
| **Justification** | Source de référence pour mesurer l'offre de soins de premier recours dans chaque arrondissement. |

### 5.7 Population par Âge (INSEE 2020)

| Champ | Valeur |
|---|---|
| **Fournisseur** | data.gouv.fr / INSEE |
| **Format** | XLSX |
| **Granularité** | Commune/Arrondissement (codes INSEE 75101–75120) |
| **Colonnes clés** | `F3-5`, `F6-10`, `H3-5`, `H6-10`, `F11-17`, `H11-17` |
| **Indicateurs produits** | Pop 3-10 ans et 11-17 ans (dénominateurs pour E1 et E2) |
| **Justification** | Indispensable pour normaliser les indicateurs éducatifs par la population cible. |

### 5.8 Population par IRIS (INSEE 2022)

| Champ | Valeur |
|---|---|
| **Fournisseur** | INSEE |
| **Format** | CSV zippé |
| **Granularité** | Zone IRIS |
| **Colonnes clés** | `IRIS`, `P22_POP` |
| **Indicateurs produits** | Population totale par IRIS pour normalisation |
| **Justification** | Granularité IRIS nécessaire pour les calculs des scores environnementaux et réseau. |

---

## 6. Cartographie

### 6.1 Fonds de Carte IRIS — Île-de-France

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.iledefrance.fr |
| **Format** | GeoJSON |
| **Granularité** | Zone IRIS (maille infra-communale INSEE) |
| **Colonnes clés** | `code_iris`, `nom_iris`, `dep`, `geometry` |
| **Qualité** | Officielle — périmètres INSEE 2022. |
| **Usage** | Stocké dans MongoDB. Sert de référentiel spatial pour tous les enrichissements géographiques et pour la carte choroplèthe IRIS du frontend. |

### 6.2 Arrondissements de Paris (GeoJSON)

| Champ | Valeur |
|---|---|
| **Fournisseur** | opendata.paris.fr (inclus dans le dépôt) |
| **Format** | GeoJSON |
| **Granularité** | Arrondissement (20 entités) |
| **Usage** | Stocké dans MongoDB. Fond de carte choroplèthe du dashboard. |

---

## Résumé des Sources

| Domaine | Nb sources | Fournisseurs principaux |
|---|---|---|
| Logement & Revenus | 3 | DGFiP, opendata.paris.fr, INSEE |
| Environnement | 4 | opendata.paris.fr |
| Mobilité | 3 | opendata.paris.fr, IDFM, data.gouv.fr |
| Réseau Télécom | 4 | ARCEP, opendata.paris.fr |
| Éducation & Santé | 8 | opendata.paris.fr, INSEE, data.gouv.fr, MEN |
| Cartographie | 2 | opendata.iledefrance.fr, opendata.paris.fr |
| **Total** | **24** | |

Toutes les sources sont publiques et librement réutilisables (Licence Ouverte / Open Database License).
