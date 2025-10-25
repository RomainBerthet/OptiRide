# velopace

Un outil Python pour optimiser le pacing d'une sortie/course de cyclisme route à partir d'un fichier GPX :
- calcul point-par-point de la puissance cible
- estimation du temps optimal
- plan nutrition/hydratation
- visualisations (profil, puissance cible)
- export CSV des cibles

## Installation

```bash
pip install .
```

ou

```bash
pipx install .
```

## Utilisation rapide

```bash
pace-gpx compute \
  --gpx examples/sample.gpx \
  --mass 72 --bike-mass 8 \
  --cda 0.30 --crr 0.0035 \
  --ftp 260 --wprime 20000 \
  --airtemp 15 --pressure 101325 --humidity 0.5 \
  --power-flat 220 \
  --step-m 20
```

Sorties :
- `outputs/summary.json` : récap (temps, kCal, plan carb/hydratation)
- `outputs/targets.csv` : tableau (distance, pente, puissance cible, vitesse, dt cumulée)
- `outputs/plots/*.png` : visualisations

## Notes
- Le modèle utilise Martin et al. (1998) pour la physique vélo et un garde-fou CP/W′ simplifié.
- Pour un solveur d'optimisation plus poussé (CasADi/Ipopt), le code est structuré pour l'ajouter dans `optimizer.py`.

## Météo automatique (Open-Meteo)

Active l'option `--auto-weather` pour que l'outil récupère température, humidité, pression et vent en fonction de la position moyenne du GPX (API Open-Meteo, sans clé). Le vent est projeté le long de la trajectoire (cap des segments) pour calculer la vitesse de l'air relative et donc la puissance aéro plus réaliste.

Exemple :
```bash
pace-gpx compute   --gpx examples/sample.gpx   --mass 72 --bike-mass 8   --cda 0.30 --crr 0.0035   --ftp 260 --wprime 20000   --power-flat 220   --auto-weather   --hour 9
```


## Optimisation de l'heure de départ
Nouvelle commande `optimize-start` qui balaie une plage horaire et choisit l'heure offrant le temps estimé minimal.
Exemple:

```
pace-gpx optimize-start \
  --gpx examples/sample.gpx \
  --mass 72 --bike-mass 8 \
  --cda 0.30 --crr 0.0035 \
  --ftp 260 --wprime 20000 \
  --power-flat 220 \
  --start-hour 6 --end-hour 20 \
  --export-gpx
```

## Export GPX avec puissances cibles
Dans `compute` et `optimize-start`, ajoute `--export-gpx` pour produire une trace `*.gpx` contenant des `<extensions><velopace:target_watts>` par point.
