# Projet TORTELLINI - Cas Test : Bille Unique (Unit Cell)

Ce dépôt contient le cas de validation initial ("Proof of Concept") pour le projet **TORTELLINI**.
Il modélise une "Cellule Unitaire" composée d'une bille de Polyuréthane suspendue dans un cube d'Air, soumise à un gradient de température.

## 📌 Objectifs Scientifiques

1.  **Validation du Maillage :** Tester la capacité de `snappyHexMesh` à mailler l'interface courbe Sphère/Cube sans contact singulier.
2.  **Validation Physique :** Vérifier la continuité des flux thermiques entre l'Air et le Polyuréthane via `chtMultiRegionFoam`.
3.  **Scalabilité :** Préparer une configuration légère (Air stagnant) transposable à un empilement massif (1000+ billes).

## ⚙️ Configuration Physique

### Géométrie
* **Domaine :** Cube de coté $L$.
* **Inclusion :** Sphère de rayon $R$, centrée en $(L/2, L/2, L/2)$.
* **Position :** La sphère est en suspension (pas de contact paroi) pour éviter les singularités de maillage.

### Matériaux
Les propriétés sont définies dans `constant/fluid/thermophysicalProperties` et `constant/solid/...` :
* **Fluide (Air)** : $\lambda \approx 0.026$ W/mK (Considéré immobile initialement).
* **Solide (Polyuréthane)** : $\lambda \approx 0.025$ W/mK.

### Conditions aux Limites (Thermiques)
Configuration de type "Plaque Chaude Gardée" pour forcer un flux unidirectionnel (selon X) :
* **Paroi Gauche (minX)** : $T = T_{hot}$ (Source chaude).
* **Paroi Droite (maxX)** : $T = T_{cold}$ (Source froide).
* **Autres Parois (Y+, Y-, Z+, Z-)** : `zeroGradient` (Adiabatique/Isolé).

Cette configuration permet de calculer la conductivité équivalente $k_{eff}$ via la loi de Fourier globale.

## 📂 Structure du Cas



├── Allrun                   # Script d'automatisation complet
├── Allclean                 # Nettoyage
├── CAD/
│   ├── SingleSphere.py      # Script Salome (Génère sphere.stl et box.stl centré)
│   └── ...
├── 0/                       # Champs initiaux
│   ├── fluid/
│   │   ├── T                # T_hot à gauche, T_cold à droite
│   │   ├── U                # Initialisé à (0 0 0) - Air stagnant
│   │   └── p_rgh
│   └── solid/
│       └── T
├── constant/
│   ├── regionProperties     # Mapping: fluid (air) / solid (sphere)
│   └── ...
└── system/
    ├── controlDict          # Pas de temps (mode transient ou steadyState)
    └── snappyHexMeshDict    # Raffinement niveau 2 ou 3 autour de la sphère
🚀 Utilisation
1. Génération Géométrie
Exécuter le script Salome pour créer les STL dans constant/triSurface :

Bash

salome -t CAD/SingleSphere.py
Le script assure que la sphère est strictement au centre du cube.

2. Lancement
Bash
./Allclean

./Allrun
./Allrun_MeshAndSolve
tail -f log.
paraFoam
touch air.foam
touch solid.foam
Le script exécute : blockMesh > snappyHexMesh > splitMeshRegions > chtMultiRegionFoam.

3. Hypothèse de Simulation
Par défaut, ce cas est configuré en Conduction Dominante. L'équation de quantité de mouvement (Navier-Stokes) pour l'air peut être désactivée dans system/fluid/fvSolution pour accélérer le calcul, simulant un air confiné immobile (hypothèse réaliste pour les mousses isolantes à petits pores).
