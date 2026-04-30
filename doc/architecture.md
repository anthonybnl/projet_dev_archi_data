# Architecture Technique — Urban Data Explorer

## Vue d'ensemble

Urban Data Explorer est une plateforme d'exploration des données de logement parisien construite sur une architecture **Medallion (Bronze → Silver → Gold)**, exposant ses données via une **API FastAPI** et un **dashboard cartographique React/MapLibre**.

```
Sources ouvertes          Pipeline Python            Stockage              Exposition
(data.gouv, INSEE,   →   Raw → Silver → Gold   →   PostgreSQL           →   API FastAPI
 ARCEP, Paris OD)                                   MongoDB (GeoJSON)        Frontend React
```

---

## 1. Architecture Medallion (Pipeline de données)

### 1.1 Couche Raw (Bronze) — Ingestion

**Rôle :** Téléchargement des données brutes depuis les APIs publiques.

**Scripts :** `pipeline/raw/download_all.py` + `pipeline/raw/download_*.py`  
**Configuration :** `pipeline/raw/url_data.yaml` (24 URLs organisées par domaine)  
**Stockage :** `data/raw/` (CSV, XLSX, GeoJSON, GeoPackage)

**Domaines ingérés :**

| Domaine | Fichiers | Taille estimée |
|---|---|---|
| Obligatoire (DVF 2021-2025 + FILOSOFI + RPLS) | 10 fichiers | ~2 Go |
| Réseau (couvertures mobile 4G/5G + QoS + fibre + antennes) | 13 fichiers | ~500 Mo |
| AES (écoles + hôpitaux + BPE santé + population) | 8 fichiers | ~50 Mo |
| Environnement (arbres + espaces verts + îlots fraîcheur + Trilib) | 4 fichiers | ~30 Mo |
| Mobilité (Vélib + arrêts IDFM + gares) | 3 fichiers | ~20 Mo |
| Cartographie (IRIS GeoJSON) | 1 fichier | ~10 Mo |

**Parallélisation :** `download.py` utilise un pool de threads (`ThreadPoolExecutor`) par domaine.

---

### 1.2 Couche Silver — Nettoyage & Standardisation

**Rôle :** Filtrer, nettoyer, normaliser et géocoder les données brutes. Chaque module produit une table PostgreSQL propre dans le schéma `silver`.

**Scripts :** `pipeline/silver/main_*.py` → `pipeline/silver/<domaine>/<module>.py`

**Tables Silver produites :**

| Table | Source | Opérations clés |
|---|---|---|
| `silver.dvf` | ValeursFoncieres 2021-2025 | Filtre Paris (CP 75xxx), calcul prix/m², jointure IRIS |
| `silver.filosofi` | FILOSOFI 2018-2021 | Filtre IRIS parisiens, secret statistique géré |
| `silver.logements_sociaux` | RPLS | Standardisation arrondissement |
| `silver.arbres` | Arbres Paris | Agrégation par arrondissement |
| `silver.espaces_verts` | Espaces verts | Calcul surface totale par arrondissement |
| `silver.ilots_fraicheur` | Îlots de fraîcheur | Dénombrement par arrondissement |
| `silver.trilib` | Stations Trilib | Dénombrement par arrondissement |
| `silver.map_velib` | Vélib | Nettoyage coordonnées GPS |
| `silver.map_arrets` | Arrêts IDFM | Filtre Paris, normalisation mode transport |
| `silver.map_gares` | Gares/Stations | Filtre Paris |
| `silver.mobile` | Couvertures 4G/5G | Intersection spatiale IRIS ↔ polygones de couverture |
| `silver.qualite_reseau` | QoS ARCEP | Agrégation par opérateur |
| `silver.fibre` | Fibre ARCEP | Agrégation par IRIS |
| `silver.ecoles_elementaires_paris` | Effectifs scolaires | Filtre Paris, agrégation par arrondissement |
| `silver.colleges_paris` | Collèges | Déduplication sur (adresse, arrondissement) |
| `silver.map_scolaire` | Écoles + collèges | Fusion 3 sources, déduplication 102 Polyvalents |
| `silver.map_sante` | Hôpitaux franciliens | Filtre CP 75xxx, extraction arrondissement |
| `silver.sante_paris` | BPE INSEE | Indicateurs S1-S4 par arrondissement |
| `silver.population_enfants_paris` | Pyramide des âges INSEE | Pop 3-10 ans, 11-17 ans |
| `silver.population_totale_paris` | Population Paris 2026 | Standardisation |
| `silver.population_iris` | Population IRIS 2022 | Granularité IRIS |

**Stratégie d'insertion :** `ON CONFLICT DO NOTHING` sur clé unique → idempotent, re-exécutable sans doublon.

---

### 1.3 Couche Gold — Indicateurs & Scores

**Rôle :** Calculer les indicateurs métier agrondissement/IRIS à partir des tables Silver, prêts à être exposés par l'API.

**Scripts :** `pipeline/gold/main_*.py` → `pipeline/gold/<domaine>.py`

**Tables Gold produites :**

| Table | Sources Silver | Indicateurs |
|---|---|---|
| `gold.dvf_iris` | `silver.dvf` | Prix médian m², nb transactions, évolution YoY par IRIS |
| `gold.filosofi_iris` | `silver.filosofi` | Revenu médian, taux de pauvreté par IRIS |
| `gold.logements_sociaux_arr` | `silver.logements_sociaux` | Part logements sociaux par arrondissement |
| `gold.score_environnement` | arbres, espaces_verts, ilots, trilib | Score pondéré (arb 30%, EV 40%, IF 20%, Trilib 10%) |
| `gold.score_mobilite` | map_velib, map_arrets, map_gares | Score accessibilité TC + Vélib par arrondissement |
| `gold.score_reseau` | silver.mobile, qualite, fibre | Score_Final = 45%×Mobile + 30%×Qualité + 25%×Fibre |
| `gold.indicateurs_education` | ecoles, colleges, population | E1 = élèves/pop 3-10 ; E2 = collèges/pop 11-17 ; NE1, NE2 |
| `gold.indicateurs_sante` | sante_paris, population_totale | S1-S4 (médecins, infirmiers, centres, pharmacies/hab) ; NS1-NS4 |
| `gold.score_aes` | indicateurs_education + sante | Score_AES = [(NE1+NE2)/2 + (NS1+NS2+NS3+NS4)/4] / 2 |

**Stratégie d'insertion :** Append avec `created_at` — l'API filtre toujours sur `MAX(created_at)`.

---

## 2. Stockage

### 2.1 PostgreSQL (données tabulaires)

- **Image :** `postgres:15-alpine`
- **Schémas :** `silver` (nettoyage) + `gold` (indicateurs)
- **Initialisation :** Scripts SQL `sql/01-init.sql` à `sql/14-*.sql` montés dans `/docker-entrypoint-initdb.d`
- **Connexion :** `SQLAlchemy` via `pipeline/db.py` et `pipeline/config.py`

### 2.2 MongoDB (données géospatiales)

- **Image :** `mongo:8.2.7`
- **Collections :** `arrondissements` (GeoJSON 20 polygones) + `iris` (GeoJSON ~800 zones IRIS)
- **Usage :** Stockage et service des fonds de carte GeoJSON via l'API (`api/geo.py`)
- **Chargement :** `no_sql/iris_arr__mongodb.py`

---

## 3. API Backend (FastAPI)

**Fichiers :** `api/main.py`, `api/indicateurs.py`, `api/geo.py`, `api/nosql_db.py`  
**Lancement :** `uvicorn api.main:app --host 0.0.0.0 --port 8000`

**Endpoints :**

| Méthode | Route | Description | Paramètres |
|---|---|---|---|
| GET | `/api/geo/arrondissements` | GeoJSON des 20 arrondissements | — |
| GET | `/api/geo/iris` | GeoJSON des zones IRIS Paris | — |
| GET | `/api/indicateurs/arrondissement` | Indicateurs gold par arrondissement | `annee` (défaut: 2025) |
| GET | `/api/indicateurs/iris` | Indicateurs gold par IRIS | `annee` (défaut: 2025) |

**Architecture :**
- GeoJSON servi depuis MongoDB (lecture rapide, pas de calcul)
- Indicateurs calculés depuis PostgreSQL Gold (agrégats pré-calculés)
- CORS activé pour le frontend (`http://localhost:5173` en dev, configurable en prod)

---

## 4. Frontend (React + MapLibre)

**Stack :** React 19 + TypeScript + Vite + MapLibre GL JS 5  
**Fichiers clés :** `front/src/components/Map.tsx`, `front/src/components/Sidebar.tsx`

**Fonctionnalités :**
- Carte choroplèthe (coloration par score : rouge → orange → vert)
- Fond de carte : OpenFreeMap (style "bright")
- Centrage Paris : `[48.8534, 2.3488]`, zoom 11
- Sidebar : sélecteur d'indicateur (Total / Environnement / Mobilité / Aucun)
- Couche espaces verts toggleable
- Infobulles au survol/clic sur les arrondissements

---

## 5. Infrastructure Docker

**Fichier :** `docker-compose.yml`

| Service | Image | Port | Rôle |
|---|---|---|---|
| `postgres_urban_data` | `postgres:15-alpine` | 5432 | Base de données principale |
| `mongo` | `mongo:8.2.7` | 27017 | Stockage GeoJSON |
| `pipeline` | Build local | — | Exécute Raw + Silver + Gold (run once) |
| `nosql_loader` | Build local | — | Charge GeoJSON dans MongoDB |
| `api` | Build local | 8000 | Sert l'API FastAPI |
| `frontend` | Build local (Nginx) | 80 | Dashboard React compilé |
| `scheduler` | Build local | — | Re-ingestion planifiée (hebdomadaire) |
| `mongo-express` | `mongo-express:1.0.2` | 8081 | Admin MongoDB |
| `adminer` | `adminer:5.4.2` | 8080 | Admin PostgreSQL |

**Ordre de démarrage :**
```
postgres (healthy) + mongo → pipeline → nosql_loader → api → frontend
                                     ↑
                                 scheduler (boucle hebdomadaire)
```

---

## 6. Flux de Données Complet

```
APIs publiques
     │
     ▼
[Raw Layer] ─── CSV/XLSX/GeoPackage ──► data/raw/
     │
     ▼
[Silver Layer] ─── nettoyage/filtrage ──► PostgreSQL schema silver
     │
     ▼
[Gold Layer] ─── agrégation/scoring ──► PostgreSQL schema gold
     │
     ├──► [API /api/indicateurs/*] ──► Frontend (scores arrondissements)
     │
[MongoDB] ◄── GeoJSON IRIS + arrondissements
     │
     └──► [API /api/geo/*] ──► Frontend (fonds de carte)
```

---

## 7. Choix Techniques — Justifications

| Choix | Alternative écartée | Raison |
|---|---|---|
| PostgreSQL (Silver/Gold) | SQLite | Performances sur jointures spatiales, support multi-utilisateur |
| MongoDB (GeoJSON) | PostGIS | Stockage natif JSON/GeoJSON sans schéma rigide, lecture directe |
| FastAPI | Flask | Validation Pydantic automatique, doc Swagger intégrée, async natif |
| MapLibre GL JS | Leaflet | Rendu WebGL haute performance, support tuiles vectorielles |
| Vite + React | Next.js | Dashboard SPA pur, pas de SSR nécessaire, build plus simple |
| Medallion Architecture | Pipeline monolithique | Traçabilité, ré-exécution partielle, qualité progressive |
| Docker Compose | Déploiement manuel | Reproductibilité totale, un seul `docker compose up` |
