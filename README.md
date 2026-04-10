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
## 1. Formule Globale
Le score final est la somme pondérée des trois piliers principaux :

$$Score_{Final} = (0,45 	imes S_{Mobile}) + (0,30 	imes S_{Qualité}) + (0,25 	imes S_{Fibre})$$

---

## 2. Décomposition des Sous-Scores

### A. Score Mobile ($S_{Mobile}$) - Poids : 45%
$$S_{Mobile} = (0,35 	imes C_{4G}) + (0,40 	imes C_{5G}) + (0,15 	imes N_{Couv}) + (0,10 	imes D_{Ant})$$

* **Couverture 4G ($C_{4G}$)** : Taux de disponibilité de la technologie 4G (35%).
* **Couverture 5G ($C_{5G}$)** : Taux de disponibilité de la technologie 5G (40%).
* **Niveau de couverture ($N_{Couv}$)** : Puissance du signal (RSRP normalisé) (15%).
* **Densité antennes ($D_{Ant}$)** : Nombre de supports actifs par zone (10%).

### B. Score Qualité ($S_{Qualité}$) - Poids : 30%
$$S_{Qualité} = (0,40 	imes D_{DL}) + (0,30 	imes F_{iab}) + (0,30 	imes L_{at})$$

* **Débit DL médian ($D_{DL}$)** : Vitesse de téléchargement médiane (40%).
* **Fiabilité ($F_{iab}$)** : Taux de réussite des tests / absence d'échecs (30%).
* **Latence ($L_{at}$)** : Rapidité de réponse (Ping) - Score inverse (30%).

### C. Score Fibre ($S_{Fibre}$) - Poids : 25%
$$S_{Fibre} = (0,60 	imes T_{Depl}) + (0,40 	imes T_{PM})$$

* **Taux déploiement ($T_{Depl}$)** : Pourcentage de locaux raccordables (60%).
* **Taux PM actif ($T_{PM}$)** : Pourcentage de Points de Mutualisation activés (40%).

---

## 3. Formule Développée Complète

$$
\begin{aligned}
Score = & \ 0,45 \times [0,35C_{4G} + 0,40C_{5G} + 0,15N_{Couv} + 0,10D_{Ant}] \\
& + 0,30 \times [0,40D_{DL} + 0,30F_{iab} + 0,30L_{at}] \\
& + 0,25 \times [0,60T_{Depl} + 0,40T_{PM}]
\end{aligned}
$$