# Spécification Géométrique : Cas Test "Bille Unique" (Unit Cell)

Ce document décrit les spécifications géométriques exactes pour le script de génération `CAD/SingleSphere.py`.
Le but est de générer les fichiers STL nécessaires au maillage via `snappyHexMesh` pour une simulation `chtMultiRegionFoam`.

## 1. Paramètres Globaux

Les dimensions sont définies pour représenter une "Cellule Unitaire" réaliste mais simplifiée (sans contact paroi).

| Paramètre | Variable Python suggérée | Valeur par défaut | Description |
| :--- | :--- | :--- | :--- |
| **Côté du Cube** | `L_cube` | `0.01` (10 mm) | Dimension du domaine fluide (Air). |
| **Rayon de la Bille** | `R_sphere` | `0.004` (4 mm) | Rayon de l'inclusion solide (Polyuréthane). |
| **Centre X, Y, Z** | `Center` | `L_cube / 2` | La bille est strictement centrée. |
| **Marge de sécurité** | `Gap` | `1 mm` | `(L_cube/2) - R_sphere`. Doit être > 0 pour éviter le contact singulier. |

## 2. Définition des Solides

Le script doit créer deux objets géométriques distincts.

### A. La Bille (Region Solide)
* **Forme** : Sphère parfaite.
* **Position** : Centre $(x, y, z) = (0.005, 0.005, 0.005)$.
* **Rôle** : Définira la zone de maillage `solid` (cellZone).
* **Nom de l'objet dans Salome** : `Solid_Sphere`.

### B. La Boîte (Limites du Domaine Fluide)
* **Forme** : Cube (Box).
* **Dimensions** : De $(0, 0, 0)$ à $(0.01, 0.01, 0.01)$.
* **Rôle** : Servira à définir les frontières extérieures si `blockMesh` n'est pas utilisé seul, ou pour visualiser les patches.
* **Nom de l'objet dans Salome** : `Fluid_Domain`.

## 3. Définition des Groupes (Patchs / Conditions Limites)

C'est l'étape la plus critique. Le script doit créer des **Groupes de Faces** sur l'objet `Fluid_Domain` (la boîte) pour assigner les conditions aux limites thermiques.

| Nom du Groupe (Patch) | Localisation Géométrique | Type de Condition (OpenFOAM) |
| :--- | :--- | :--- |
| **`inlet`** | Face X = 0 (Plan YZ à l'origine) | Température Chaude ($T_{hot}$) |
| **`outlet`** | Face X = `L_cube` (Plan YZ opposé) | Température Froide ($T_{cold}$) |
| **`walls`** | Faces Y=0, Y=`L`, Z=0, Z=`L` | Adiabatique (`zeroGradient`) |

*Note : La surface de la sphère n'a pas besoin de groupe nommé "wall", `snappyHexMesh` créera automatiquement une interface interne nommée `sphere_to_fluid`.*

## 4. Exports Requis (Fichiers de Sortie)

Le script doit exporter les fichiers au format **STL ASCII** dans le dossier approprié.

1.  **Fichier 1 : La Bille**
    * Objet à exporter : `Solid_Sphere`
    * Chemin : `../constant/triSurface/sphere.stl`
    * *Important :* La triangulation doit être assez fine pour que la courbure soit respectée (Paramètres de déflection Salome).

2.  **Fichier 2 : La Boîte (Optionnel mais recommandé)**
    * Objet à exporter : `Fluid_Domain` (contenant les groupes `inlet`, `outlet`, `walls`).
    * Chemin : `../constant/triSurface/box_walls.stl`

## 5. Algorithme du Script Python (`SingleSphere.py`)

1.  **Initialisation** : Charger `salome.geom`.
2.  **Paramètres** : Définir `L` et `R`.
3.  **Création Bille** : `MakeSphere(R)`, puis `MakeTranslation(L/2, L/2, L/2)`.
4.  **Création Boîte** : `MakeBoxDXDYDZ(L, L, L)`.
5.  **Création des Groupes (Boîte)** :
    * `CreateGroup` (Faces) -> Sélection par IDs ou par coordonnées (ex: `GetShapesOnPlaneWithNormal`).
    * Nommer : `inlet`, `outlet`, `walls`.
6.  **Maillage STL (Discrétisation)** :
    * Avant l'export, il faut souvent passer par un maillage simple dans Salome (Mesh module) ou utiliser l'export STL direct de Geom si la précision par défaut suffit.
    * *Recommandation :* Utiliser l'export direct Geom avec une déviation faible.
7.  **Export** : Écriture des fichiers `.stl`.
