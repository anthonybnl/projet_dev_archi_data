# projet_dev_archi_data

Projet Développement Architecture de données.

## Sources de données

[sources de données](doc/sources_data.md)

## Architecture

![Architecture](doc/archi.svg)

Cacule reseau:
```text
Score_final (100%)
├── Score_Mobile (45%)
│   ├── Couverture 4G (35%)
│   ├── Couverture 5G (40%)
│   ├── Niveau couverture (15%)
│   └── Densité antennes (10%)
├── Score_Qualite (30%)
│   ├── Débit DL médian (40%)
│   ├── Fiabilité (30%)
│   └── Latence (30%)
└── Score_Fibre (25%)
    ├── Taux déploiement (60%)
    └── Taux PM actif (40%)
```
# Méthodologie du Calcul de Score Réseau

## 1. Formule Globale
Le score final est la somme pondérée des trois piliers principaux :

$$Score_{Final} = (0,45 \times S_{Mobile}) + (0,30 \times S_{Qualité}) + (0,25 \times S_{Fibre})$$

---

## 2. Décomposition des Sous-Scores
Chaque pilier est lui-même calculé selon ses propres indicateurs :

### A. Score Mobile ($S_{Mobile}$)
$$S_{Mobile} = (0,35 \times C_{4G}) + (0,40 \times C_{5G}) + (0,15 \times N_{Couv}) + (0,10 \times D_{Ant})$$

* **$C_{4G} / C_{5G}$** : Taux de couverture (0 à 100%).
* **$N_{Couv}$** : Niveau de signal (souvent basé sur le RSRP normalisé).
* **$D_{Ant}$** : Nombre d'antennes par $km^2$ ou par habitant.

### B. Score Qualité ($S_{Qualité}$)
$$S_{Qualité} = (0,40 \times D_{DL}) + (0,30 \times F_{iab}) + (0,30 \times L_{at})$$

* **$D_{DL}$** : Débit descendant médian.
* **$F_{iab}$** : Taux de réussite des tests (Fiabilité).
* **$L_{at}$** : Score de latence (inversement proportionnel au Ping).

### C. Score Fibre ($S_{Fibre}$)
$$S_{Fibre} = (0,60 \times T_{Depl}) + (0,40 \times T_{PM})$$

* **$T_{Depl}$** : Taux de locaux raccordables.
* **$T_{PM}$** : Taux de Points de Mutualisation actifs.

---

## 3. Formule Développée (Vue d'ensemble)
$$
\begin{aligned}
Score = & \ 0,45 \times [0,35C_{4G} + 0,40C_{5G} + 0,15N_{Couv} + 0,10D_{Ant}] \\
& + 0,30 \times [0,40D_{DL} + 0,30F_{iab} + 0,30L_{at}] \\
& + 0,25 \times [0,60T_{Depl} + 0,40T_{PM}]
\end{aligned}
$$

> **Note technique :** Pour les variables comme la Latence, n'oubliez pas d'utiliser une fonction de normalisation inverse (car une latence élevée doit faire baisser le score), par exemple : $100 - Latence_{mesurée}$ ou $1/Latence$