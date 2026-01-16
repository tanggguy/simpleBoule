# Pourquoi la boule ne chauffe pas ? (Diagnostic et Solutions)

Après analyse de votre cas, il semble que la simulation fonctionne correctement d'un point de vue physique, mais deux phénomènes masquent le réchauffement de la boule :

1.  **Inertie thermique élevée** : La boule est en matériau type Aluminium (haute densité et capacité thermique) et l'échange avec l'air est lent.
2.  **Conduction très rapide dans la boule** : La conductivité est très élevée, donc la chaleur se répartit instantanément. On ne voit pas de "front de chaleur" entrer, la boule chauffe uniformément.

## 1. Explication Physique

*   **Temps caractéristique ($\tau$)** : Avec vos paramètres, il faut environ **800 secondes** (13 minutes) pour que la boule chauffe significativement (63% de la différence de température).
*   **Durée actuelle** : Votre simulation ne dure que **30 secondes**.
*   **Résultat** : En 30s, la boule ne gagne qu'environ **0.6°C**. Elle passe de 10°C (283.15 K) à 10.6°C (283.75 K).
*   **Visuel** : Si votre échelle de couleur dans Paraview est réglée sur [10°C, 27°C] (l'air est à 27°C), la boule reste bleue car 10.6°C est très proche de 10°C.

## 2. Marche à suivre pour vérifier

Voici les étapes pour confirmer que le calcul fonctionne et visualiser le réchauffement.

### A. Vérification rapide dans Paraview
1.  Ouvrez Paraview.
2.  Sélectionnez la région `solid`.
3.  Affichez la température `T`.
4.  **Important** : Cliquez sur le bouton "Rescale to Data Range" (l'icône avec une double flèche et un histogramme) **uniquement sur la dernière étape de temps**.
5.  Vous devriez voir que la température est légèrement supérieure à 283.15 K (environ 283.7 K).

### B. Augmenter la durée de simulation
Pour voir la boule chauffer franchement, il faut simuler plus longtemps.
1.  Ouvrez `system/controlDict`.
2.  Modifiez `endTime` :
    ```cpp
    endTime         1000; // Au lieu de 30
    ```
3.  Relancez la simulation.

### C. Test "Accéléré" (Pour le debug)
Si vous voulez voir la chaleur "rentrer" visuellement et rapidement sans attendre 1000s, vous pouvez artificiellement réduire l'inertie de la boule ou augmenter la conductivité de l'air.

**Option : Réduire la capacité de la boule**
1.  Ouvrez `constant/solid/thermophysicalProperties`.
2.  Divisez la densité (`rho`) ou la capacité (`Cp`) par 100.
    ```cpp
    rho         27; // Au lieu de 2700
    ```
3.  Relancez. La boule chauffera 100 fois plus vite (en quelques secondes).

**Note** : N'oubliez pas de remettre les vraies valeurs pour le calcul final !
