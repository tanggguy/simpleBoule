# TODO: Finaliser l'adaptation du cas "Simple Boule"

Ce fichier liste les étapes restantes pour finaliser le projet.

## État d'avancement
- [x] Géométrie adaptée (Sphere 4mm dans Cube 10mm).
- [x] Maillage configuré (`blockMesh`, `snappyHexMesh`).
- [x] Refactoring Water -> Air effectué.
- [x] Propriétés physiques mises à jour.
- [x] Conditions limites créées (`0/air`, `0/solid`).
- [x] Scripts de lancement (`Allrun`, `Allclean`) mis à jour.
- [x] Sondes (`Probes`) adaptées aux nouvelles dimensions.

## Reste à faire

### 1. Nettoyage Final
- [x] Supprimer les fichiers obsolètes dans `system/` (ex: `ZGraph_CentreTubeSortie_*`, `ZGraph_Cote*`) pour éviter la confusion.
- [x] Vérifier qu'il ne reste pas de références à "Tube" ou "Water" dans les commentaires ou fichiers de backup.

### 2. Exécution et Validation
- [ ] Lancer la simulation complète : `./Allrun`.
- [ ] Vérifier les logs (`log.chtMultiRegionFoam`) pour s'assurer de la convergence et de l'absence d'erreurs.
- [ ] Vérifier la génération des graphiques dans `postProcessing/`.

### 3. Analyse des Résultats
- [ ] Ouvrir Paraview (`paraFoam -touchAll` puis lancer Paraview).
- [ ] Vérifier visuellement les champs de température (T) et vitesse (U).
- [ ] Confirmer que l'échange thermique Air/Solide se fait correctement (continuité de T à l'interface, gradient correct).
