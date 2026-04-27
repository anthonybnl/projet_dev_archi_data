# Urban Data Explorer — Front

Interface React + Vite + TypeScript pour explorer le marché du logement à Paris.

## Stack

- **React 19** + **TypeScript** + **Vite**
- **MapLibre GL** pour la carte (tuiles OpenStreetMap, pas de clé API)
- Polices Google : DM Sans

## Démarrage

```bash
cd front
npm install
npm run dev
```

Le front se lance sur http://localhost:5173

⚠️ Le front a besoin de l'API backend pour fonctionner. Lance-la avant :
```bash
# depuis la racine du projet
uvicorn mock.api_indicateurs:app --reload --port 8000
```

## Structure

```
src/
├── App.tsx                   shell principal
├── main.tsx                  entry point
├── index.css                 reset + typo
├── lib/
│   ├── theme.ts              palette + rampe de couleurs
│   ├── types.ts              types TS partagés
│   ├── indicators.ts         définition des 4 indicateurs + helpers de format
│   └── api.ts                client de l'API backend
└── components/
    ├── Header.tsx            barre du haut
    ├── MapView.tsx           carte MapLibre (arrondissements + IRIS)
    ├── Section.tsx           wrapper pliable
    ├── Icons.tsx             pack d'icônes SVG
    ├── IAIGauge.tsx          jauge colorée pour l'IAI
    ├── SearchSection.tsx     barre de recherche
    ├── IndicatorsSection.tsx checkboxes des 4 indicateurs
    ├── TimelineSection.tsx   slider d'années
    ├── DetailsSection.tsx    détails de la zone sélectionnée
    └── CompareSection.tsx    comparaison de 2 zones épinglées
```

## Comportement de la carte

- **Zoom < 13** : choroplèthe par arrondissement (20 zones)
- **Zoom ≥ 13** : choroplèthe par IRIS (~992 zones)
- **Plan / Satellite** : toggle pour basculer entre OSM et tuiles satellite Esri
- **Hover** : tooltip avec le nom et la valeur de l'indicateur
- **Click** : ouvre les détails de la zone dans la sidebar
