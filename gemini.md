# 🧠 CONTEXTE & DIRECTIVES - PROJET TORTELLINI

Ce document définit le contexte, la stack technique et les règles de collaboration pour le développement du projet OpenFOAM **TORTELLINI** (Calcul de conductivité thermique équivalente).

## 1. Stack Technique (Immuable)
Toute solution proposée doit être compatible avec cet environnement :
* **OS** : Ubuntu 24.04 LTS
* **CFD** : OpenFOAM (v2406 / v2412 / v2506)
    * *Solveur* : `chtMultiRegionFoam`
    * *Maillage* : `blockMesh` + `snappyHexMesh`
* **CAD/Génération** : Salome (v9.13+) via script Python (API GEOM).
* **Langage Scripting** : Python 3.10 (pour l'automatisation et Salome).
* **Post-Traitement** : Paraview v5.13.

## 2. État Actuel du Projet
**Phase :** Validation Unitaire ("Single Sphere").
**Objectif :** Simuler une bille unique (Polyuréthane) centrée dans un cube (Air) avec un gradient de température pour valider le couplage thermique.

**Structure des dossiers :**
/
├── CAD/            # Scripts Python Salome (SingleSphere.py)
├── constant/       # triSurface/ (STL), regionProperties
├── system/         # snappyHexMeshDict, controlDict
├── 0/              # Conditions limites (T, p_rgh, U)
├── Allrun          # Script maître
└── Allclean        # Script nettoyage

3. Protocole de Débogage (Pour Antigravity)
Si une erreur survient, suivre cette procédure stricte :

Identifier l'étape :

CAD (Python/Salome) ?

Maillage (snappyHexMesh) ?

Split (splitMeshRegions) ?

Solveur (chtMultiRegionFoam) ?

Isoler l'erreur : Ne pas halluciner de solution. Demander le fichier de log spécifique (ex: "Donne-moi les 50 dernières lignes de log.snappyHexMesh").

Vérifier la Topologie :

Si snappyHexMesh échoue : Vérifier la qualité des STL (fermeture, normales).

Si chtMultiRegionFoam crashe : Vérifier regionProperties et les conditions limites dans 0/.

Solution : Proposer un patch précis (bloc de code corrigé) plutôt qu'une explication vague.

4. Conventions de Code
Python (Salome) :

Utiliser salome.geom.geomBuilder.New().

Toujours nommer les groupes (CreateGroup) pour l'export STL.

Utiliser des chemins relatifs pour les exports (../constant/triSurface/).

OpenFOAM :

Les dictionnaires doivent inclure l'en-tête standard FoamFile.

Commenter chaque modification de paramètre physique.
