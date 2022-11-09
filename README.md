icon.png﻿![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.001.png)

![](icon.png)

Manuel d’utilisation                ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.003.png)Full MCE for Public Health

PLUGIN POUR QGIS VERSION 3.X,                                       

ANNEE 2022 ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.004.png)

Par : ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.005.png)

Fanjasoa RAKOTOMANANA Anthonio RAKOTOARISON Mampionona RASAMIMALALA Sarah FAMENONTSOA

Sommaire

1. [A propos ..................................................................................................................... 1 ](#_page1_x69.00_y229.68)
1. [Page d'accueil ............................................................................................................ 1 ](#_page1_x110.00_y449.68)
1. [Répertoire de sortie .................................................................................................... 2 ](#_page2_x110.00_y279.68)
1. [Reclassification des contraintes en booléen ............................................................... 2 ](#_page2_x110.00_y671.68)
1. [Normalisation des facteurs ......................................................................................... 5 ](#_page5_x69.00_y359.68)
1. [Pondération des facteurs ............................................................................................ 8 ](#_page8_x69.00_y318.68)
7. [Agrégation des contraintes et des facteurs ................................................................. 9 ](#_page9_x69.00_y348.68)
1. **A propos**

Le plugin d’Analyse Multicritère pour la Santé Publique (Full MCE for Public Health) est un plugin qui contient les fonctions suivantes :

- Reclassification des contraintes (en Booléen)
- Normalisation des facteurs
- Pondération des facteurs par la méthode de comparaison par paires
- Agrégation par la méthode de combinaison linéaire pondérée

Cette version 0.1 est compatible au QGIS version 3.x.  

Elle supporte les fichiers sources et celles de sortie au format shapefile (.shp). Le présent manuel illustre un traitement complet d’analyse multicritère.

2. **Page d'accueil**

Pour lancer le plugin, cliquer sur l’icône “Full MCE” dans la barre d’outils. Le plugin peut aussi être lancé en cliquant sur le menu “Vecteur > Analyse Multicritère pour la santé publique > Full MCE “.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.006.png)

La page d'accueil du plugin présente les principales fonctionnalités du plugin ainsi que les noms des concepteurs.

Page 10 sur 10

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.007.jpeg)

3. **Répertoire de sortie**

Après la page d’accueil, le plugin demande à l’utilisateur de choisir le répertoire de sortie. Tous les résultats de la reclassification des contraintes, de la normalisation des facteurs et de l’agrégation seront groupés dans ce répertoire. Le format de sortie est de type shapefile (.shp)  

Un fichier nommé **“fullmce\_log[date].txt”** y est également créé afin de sauvegarder tous les paramètres que l’utilisateur saisit au cours du traitement.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.008.jpeg)

4. **Reclassification des contraintes en booléen**

Après avoir choisi le répertoire de sortie, l’utilisateur doit spécifier le nombre de contraintes à utiliser lors du traitement (zone en rouge sur la figure ci-dessous).

Page 10 sur 10

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.009.png)![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.010.png)

Le nombre minimal des contraintes autorisé est **0**, le nombre maximal est **illimité.** Des lignes apparaissent suivant le nombre de contraintes choisies. En effet, l’utilisateur peut saisir les noms et choisir les fichiers sources ainsi que les champs des contraintes.  

Chaque contrainte doit correspondre à un et un seul champ de la table attributaire d’un vecteur source et vice-versa. Le plugin renvoie une erreur si plusieurs contraintes correspondent à un même champ d’un même vecteur source.

Si une ou plusieurs cases "Prêts" ne sont pas cochées (zone en vert sur la figure ci-dessus), le plugin propose de reclassifier les contraintes correspondantes. Dans ce cas, une question sera alors posée à l’utilisateur s’il veut sauvegarder les résultats dans des nouveaux fichiers.

- Si la réponse est “Oui”, le plugin sauvegarde les résultats de la reclassification dans des champs nommés “**[nom\_du\_contrainte]Bl**” de **type entier** dans des nouveaux fichiers nommés **“[nom\_du\_fichier\_source]\_bool.shp**”.  
- Sinon, les résultats seront sauvegardés dans les mêmes fichiers sources.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.011.jpeg)

- **Cas des contraintes de type quantitative :**

La valeur de la colonne « Nouvelle valeur » remplacera les attributs compris entre la valeur de la colonne « Début » et celle de la colonne « Fin ». Si la case “Inclus” est cochée,

Page 10 sur 10

alors l'intervalle correspondant sera fermé. Si les attributs à reclassifier ne sont pas spécifiés alors le plugin remplacera ces valeurs par **0** par défaut.

La colonne “Nouvelle valeur” accepte uniquement les valeurs de type entier ou  **“Null”.** La colonne “Début” et “Fin” accepte les valeurs de type entier ainsi que les valeurs

suivantes :   

- **“min”** (égale à la valeur minimum du champ choisi),  
- **“max”** (égale à la valeur maximale du champ choisi),
- la colonne “Fin” accepte uniquement les valeurs supérieures ou égales à celle de la colonne “Début”, sinon le plugin renvoie une erreur.
- chaque intervalle ("Début", "Fin”) ne devrait pas contenir un autre intervalle spécifié dans d’autres lignes, ni être inclus dans un autre intervalle.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.012.jpeg)

- **Cas des contraintes de type qualitative :**

La valeur de la colonne « Nouvelle valeur » remplacera les attributs ayant la même valeur que « Valeur Initiale ». Si les attributs à reclassifier ne sont pas spécifiés alors le plugin remplacera ces valeurs par **0** par défaut.

La colonne “Nouvelle valeur” accepte uniquement les valeurs de type entier ou **“Null”.** Chaque “Valeur Initiale” ne doit être choisie qu'une seule fois.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.013.jpeg)

Page 10 sur 10

Lorsque les paramètres de classification sont remplis, le plugin résume dans la page suivante valeurs entrées. En cliquant sur le bouton **“Suivant”**, l’utilisateur confirme ces paramètres et lance la reclassification des contraintes.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.014.jpeg)

5. **Normalisation des facteurs**

Le nombre minimal des facteurs autorisé est 3, le nombre maximal est 15. Des lignes seront ajoutées suivant le nombre de contraintes choisies. Ainsi, l’utilisateur peut saisir les noms et choisir les fichiers sources ainsi que les champs des facteurs.  

Chaque facteur doit correspondre à un et un seul champ de la table attributaire d’un vecteur source et vice-versa. Le plugin renvoie une erreur si plusieurs facteurs correspondent à un même champ d’un même vecteur source.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.015.png)

Page 10 sur 10

Si une ou plusieurs cases "Normalisé" ne sont pas cochées (zone en vert sur la figure ci- dessus), le plugin propose de normaliser les facteurs correspondants. Dans ce cas, une question sera alors posée à l’utilisateur s’il veut sauvegarder les résultats dans des nouveaux fichiers:

- Si la réponse est “Oui”, le plugin sauvegarde les résultats de la reclassification dans des champs nommés “**[nom\_du\_contrainte]Fz**” de **type entier** dans des nouveaux fichiers nommés **“[nom\_du\_fichier\_source]\_Fuzz.shp**”.  
- Sinon, les résultats seront sauvegardés dans les mêmes fichiers sources.

Le plugin propose 2 types de fonctions : Linéaire et Sigmoïdal.

Chaque fonction a 3 différents sens :

- Croissant
- Décroissant
- Symétrique (avec ou sans plateau)

Les points de contrôles changent selon le sens choisi. Les valeurs des colonnes “A”, “B”, “C” et “D” devront être de même type que les valeurs des attributs ( c’est à dire de type entier,

réel ou Date) et respecter les règles suivantes:

- “A” ≤ “B” ≤ “C” ≤ “D”
- si la valeur “A” ou “C” est égale à **"min"**, le plugin remplacera cette valeur par la valeur minimum du champ choisi
- si la valeur de "B"ou “D” est égale à **"max"**, le plugin remplacera cette valeur par la valeur maximale du champ  choisi

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.016.jpeg)

Page 10 sur 10

- **Cas de la fonction “linéaire” :**

0            <    ,   ≤    ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.017.png)

- ≤ <   

−

- ≤   
  - ≤   
- <   

( ) =  1            ≤   <     ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.018.png)

- ≤    
  - ≤    
- <    

- <     

−

- ≤   
  - ≤   
- <   

` `0             >     ≥  

- **Cas de la fonction "sigmoïdale" :**

0                         <    ,   ≤  ![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.019.png)![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.020.png)

1

- <    

1 + − ( − ( + )/2)

- ≤    
- ≤    
- <    

( ) =         1                          ≤   <    

- ≤   
  - ≤   
- <   

1

- <    

1+  − ( + )/2

- ≤   
- ≤   
- <   

0                           >     ≥

Page 11 sur 11

Lorsque les paramètres de normalisation sont remplis, le plugin résume dans la page suivante valeurs entrées. En cliquant sur le bouton **“Suivant”**, l’utilisateur confirme ces paramètres et lance la normalisation des facteurs.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.021.jpeg)

6. **Pondération des facteurs**

La pondération des facteurs est réalisée en utilisant la méthode de comparaison par paires. L’utilisateur doit alors remplir la matrice de jugement (suivant l’échelle de Saaty). Lorsqu’on saisit un nombre dans une cellule de la matrice, la cellule symétrique par rapport à la diagonale se remplit automatiquement (inversement symétrique).

Le bouton **“Importer”** permet à l’utilisateur d’importer une matrice de jugement depuis un fichier csv. L’utilisateur peut aussi enregistrer la matrice sous un fichier csv en cliquant sur le bouton **"Enregistrer"**.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.022.jpeg)

Après que la matrice est remplie, il est indispensable de tester sa cohérence en appuyant sur le bouton **« Tester »** :   

- Si le ratio de cohérence (RC) de la matrice est inférieur à 0.1, la matrice est jugée cohérente et acceptable. Dans ce cas, l’utilisateur peut passer à l’étape suivante.  

Page 10 sur 10

- Sinon, la matrice est jugée non cohérente. L’utilisateur est alors obligé de modifier les valeurs saisis et de re-tester la cohérence de la matrice.

Lorsque la matrice de jugement est cohérente, le plugin résume dans la page suivante tous les  paramètres  saisis.  En  cliquant  sur  le  bouton  **“Agréger”**,  l’utilisateur  confirme  ces paramètres et lance l’agrégation des contraintes et des facteurs.

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.023.jpeg)

7. **Agrégation des contraintes et des facteurs**

Avant l’agrégation des contraintes et des facteurs, le plugin vérifie d’abord les sources:

- si les contraintes et les facteurs sont issus du même vecteur, le plugin effectue leur agrégation
- si les contraintes et les facteurs sont issus de différents sources:
- si ces vecteurs ont les mêmes CRS, le plugin joint les entités par localisation puis effectue l'agrégation
- si ces vecteurs ont différents CRS, le plugin renvoie une erreur

La formule de l’agrégation est définie comme suit :

*pour tout  = poids du facteur;  = valeur du facteur;  = valeur de la contrainte*

- = ∑ =1 ∗ 1,   si aucune contrainte est spécifiée
- = ∑ =1 ∏ =1 ,   si au moins une contrainte est spécifiée

Les résultats de l’agrégation sont stockés dans un nouveau champ nommé **"WLC"** **de type réel** (5 chiffres après la virgule) dans un vecteur portant le nom «**resultat\_final.shp »** stocké dans le répertoire de sortie.

Une fois tous les traitements exécutés, une boîte de dialogue affiche **« Agrégation terminée avec  succès  »**.  En  cas  d’erreur,  le  plugin  s’arrête  aussitôt  en  affichant  l’erreur correspondante.

Page 10 sur 10

![](images/Aspose.Words.07f5128e-d9a3-4e28-8325-80e4ff5f72ef.024.jpeg)
Page 10 sur 10
