# Plan d'implémentation — Paris Data Explorer

## Architecture globale (Medallion)

```
Bronze (raw)  →  Silver (nettoyage/filtrage)  →  Gold (indicateurs + score final)
```

---

## Sources Bronze disponibles

| Fichier | Usage |
|---|---|
| `fr-en-ecoles-effectifs-nb_classes.csv` | Calcul E1 (places primaires) |
| `etablissements-scolaires-colleges.csv` | Map + calcul E2 (nb collèges) |
| `etablissements-scolaires-ecoles-elementaires.csv` | Map uniquement |
| `etablissements-scolaires-maternelles.csv` | Map uniquement |
| `age-insee-2020.xlsx` (onglet COM) | Pop 3-10 ans et 11-17 ans par arrondissement |
| `population_paris_2026.csv` | Population totale par arrondissement |
| `BPE_SANTE_ACTION_SOCIALE_FR.xlsx` (onglet ARM) | Indicateurs S1, S2, S3, S4 |
| `les_etablissements_hospitaliers_franciliens.csv` | ⚠️ Fichier manquant |

---

## Étape 1 — Bronze → Silver (nettoyage par source)

### `silver.ecoles_elementaires_paris`
- **Source :** `nb_classes.csv`
- **Opérations :**
  - Filtrer sur Code département = `75` (Paris) et année scolaire la plus récente
  - Exclure les maternelles (garder uniquement les écoles élémentaires)
  - Extraire l'arrondissement depuis le Code Postal (ex: 75011 → 11e)
  - Sommer `Nombre total d'élèves en élémentaire hors ULIS` par arrondissement *(proxy pour "places primaires")*
- **Colonnes produites :** `arrondissement`, `nb_places_primaires`

### `silver.colleges_paris`
- **Source :** `etablissements-scolaires-colleges.csv`
- **Opérations :**
  - Filtrer sur Paris (colonne `Arrondissement`)
  - Année la plus récente
  - Compter le nombre de collèges par arrondissement
  - Conserver toutes les infos utiles par établissement
- **Colonnes produites :** `nom`, `adresse`, `arrondissement`, `lat`, `lon`
- **Agrégation pour calcul E2 :** `nb_colleges` = COUNT par arrondissement

### `silver.population_enfants_paris`
- **Source :** `age-insee-2020.xlsx` (onglet COM)
- **Opérations :**
  - Filtrer sur codes INSEE 75101 → 75120 (arrondissements parisiens)
  - Pop 3-10 ans = `F3-5` + `F6-10` + `H3-5` + `H6-10`
  - Pop 11-17 ans = `F11-17` + `H11-17`
- **Colonnes produites :** `arrondissement`, `pop_3_10`, `pop_11_17`

### `silver.population_totale_paris`
- **Source :** `population_paris_2026.csv`
- **Opérations :**
  - Standardiser le nom d'arrondissement
- **Colonnes produites :** `arrondissement`, `population_totale`

### `silver.sante_paris`
- **Source :** `BPE_SANTE_ACTION_SOCIALE_FR.xlsx` (onglet ARM)
- **Opérations :**
  - Filtrer sur codes géo 75101 → 75120
  - Extraire les colonnes utiles :
    - `Médecin généraliste` → S1
    - `Infirmier` → S2
    - `Centre de santé` → S3 *(proxy "centre médical")*
    - `Pharmacie` → S4
- **Colonnes produites :** `arrondissement`, `nb_medecins`, `nb_infirmiers`, `nb_centres_sante`, `nb_pharmacies`

### `silver.map_scolaire`
- **Source :** `colleges.csv` + `elementaires.csv` + `maternelles.csv`
- **Opérations :**
  - Extraire et unifier les colonnes des 3 fichiers
  - ⚠️ **Déduplication des Polyvalents** : les 102 établissements `Polyvalent` apparaissent dans les deux fichiers elementaires et maternelles avec le même nom et adresse. On les garde **une seule fois** (depuis `maternelles.csv`) avec le type `Polyvalent`.
  - Règle appliquée : lors du concat, si doublon sur (`Libellé établissement`, `Adresse`), on supprime le doublon issu du fichier elementaires
  - Standardiser les types : `Collège`, `Élémentaire`, `Maternelle`, `Polyvalent`
- **Colonnes produites :**
  - `nom` — libellé de l'établissement
  - `adresse` — adresse complète
  - `type` — type d'établissement (filtre front)
  - `arrondissement`
  - `lat`, `lon` — coordonnées GPS pour la map

### `silver.map_sante`
- **Source :** `les_etablissements_hospitaliers_franciliens.csv` (237 établissements sur Paris)
- **Opérations :**
  - Filtrer sur Paris : `CP_VILLE` commence par `75`
  - Extraire l'arrondissement depuis `CP_VILLE` (ex: `75011` → `11e`)
- **Colonnes produites :**
  - `nom` — `RAISON_SOCIALE`
  - `adresse` — `ADRESSE_COMPLETE`
  - `telephone` — `NUM_TEL`
  - `categorie` — `CATEGORIE_DE_L_ETABLISSEMENT` (filtre front : C.H.R., clinique, CMP…)
  - `type_etablissement` — `TYPE_ETABLISSEMENT` (niveau plus agrégé)
  - `arrondissement`
  - `lat`, `lon`

---

## Schéma des tables Silver

### Tables agrégées par arrondissement

| Table | Source CSV | Colonnes | Clé | Stratégie |
|---|---|---|---|---|
| `silver.ecoles_elementaires_paris` | `fr-en-ecoles-effectifs-nb_classes.csv` | `id SERIAL`, `numero_ecole`, `nom`, `type`, `secteur`, `arrondissement`, `nb_eleves`, `created_at` | `numero_ecole` | Append — insère uniquement les nouvelles écoles (`ON CONFLICT DO NOTHING`) |
| `silver.population_enfants_paris` | `age-insee-2020.xlsx` (onglet COM) | `id SERIAL`, `arrondissement`, `pop_3_10`, `pop_11_17`, `created_at` | `arrondissement` | Append — Gold/Front prennent le `MAX(created_at)` |
| `silver.population_totale_paris` | `population_paris_2026.csv` | `id SERIAL`, `arrondissement`, `population_totale`, `created_at` | `arrondissement` | Append — Gold/Front prennent le `MAX(created_at)` |
| `silver.sante_paris` | `BPE_SANTE_ACTION_SOCIALE_FR.xlsx` (onglet ARM) | `id SERIAL`, `arrondissement`, `nb_medecins`, `nb_infirmiers`, `nb_centres_sante`, `nb_pharmacies`, `created_at` | `arrondissement` | Append — Gold/Front prennent le `MAX(created_at)` |

### Tables d'établissements

| Table | Source CSV | Colonnes | Clé unique | Stratégie |
|---|---|---|---|---|
| `silver.colleges_paris` | `etablissements-scolaires-colleges.csv` | `id SERIAL`, `nom`, `adresse`, `arrondissement`, `lat`, `lon`, `created_at` | `(adresse, arrondissement)` | Append — insère uniquement les nouveaux établissements (`ON CONFLICT DO NOTHING`) |
| `silver.map_scolaire` | `colleges.csv` + `elementaires.csv` + `maternelles.csv` | `id SERIAL`, `nom`, `adresse`, `type`, `arrondissement`, `lat`, `lon`, `created_at` | `(adresse, arrondissement)` | Append — insère uniquement les nouveaux établissements (`ON CONFLICT DO NOTHING`) |
| `silver.map_sante` | `les_etablissements_hospitaliers_franciliens.csv` | `id SERIAL`, `finess`, `nom`, `adresse`, `telephone`, `categorie`, `type_etablissement`, `arrondissement`, `lat`, `lon`, `created_at` | `finess` | Append — insère uniquement les nouveaux établissements (`ON CONFLICT DO NOTHING`) |

---

## Étape 2 — Silver → Gold (calcul des indicateurs)

### `gold.indicateurs_education`

| Indicateur | Formule |
|---|---|
| E1 | `nb_places_primaires / pop_3_10` par arrondissement |
| E2 | `nb_colleges / pop_11_17` par arrondissement |
| NE1, NE2 | Normalisation min-max × 100 |

### `gold.indicateurs_sante`

| Indicateur | Formule |
|---|---|
| S1 | `nb_medecins / population_totale` |
| S2 | `nb_infirmiers / population_totale` |
| S3 | `nb_centres_sante / population_totale` |
| S4 | `nb_pharmacies / population_totale` |
| NS1…NS4 | Normalisation min-max × 100 |

### `gold.score_final`

```
Score_final = [ (NE1 + NE2) / 2  +  (NS1 + NS2 + NS3 + NS4) / 4 ] / 2
```

Par arrondissement — table finale exposée au front.

---

## Schéma des tables Gold

> Stratégie : INSERT à chaque run (même logique que Silver agrégé). Front filtre sur `MAX(created_at)`.

| Table | Sources Silver | Colonnes | Stratégie |
|---|---|---|---|
| `gold.indicateurs_education` | `ecoles_elementaires_paris`, `colleges_paris`, `population_enfants_paris` | `id SERIAL`, `arrondissement`, `E1`, `E2`, `NE1`, `NE2`, `created_at` | Append — Front prend le `MAX(created_at)` |
| `gold.indicateurs_sante` | `sante_paris`, `population_totale_paris` | `id SERIAL`, `arrondissement`, `S1`, `S2`, `S3`, `S4`, `NS1`, `NS2`, `NS3`, `NS4`, `created_at` | Append — Front prend le `MAX(created_at)` |
| `gold.score_final` | `indicateurs_education`, `indicateurs_sante` | `id SERIAL`, `arrondissement`, `score_education`, `score_sante`, `score_final`, `created_at` | Append — Front prend le `MAX(created_at)` |

---

## Structure des scripts Python

```
pipeline/
├── __init__.py
├── config.py              # Lecture config.yaml
├── db.py                  # Connexion SQLAlchemy
├── bronze/
│   └── loader.py          # Chargement raw → tables bronze (optionnel)
├── silver/
│   ├── ecoles.py
│   ├── colleges.py
│   ├── population.py
│   ├── sante.py
│   └── map_data.py
├── gold/
│   ├── indicateurs_education.py
│   ├── indicateurs_sante.py
│   └── score_final.py
└── main.py                # Orchestration séquentielle
```

---

## Questions ouvertes

1. **E1 — "Nombre de places primaires"** : le fichier nb_classes.csv contient les effectifs inscrits, pas une capacité d'accueil. On utilise `Nombre total d'élèves en élémentaire hors ULIS` comme proxy ou tu as une autre définition ?

2. **E2 — Source des collèges** : pour compter les collèges par arrondissement (calcul E2), on utilise `colleges.csv` (même fichier que la map) ?

3. **Fichier hospitalier manquant** : `les_etablissements_hospitaliers_franciliens.csv` n'est pas encore dans `Data/Bronze/Sante/`. Quand sera-t-il disponible ? Le silver `map_sante` sera bloqué sans lui.
