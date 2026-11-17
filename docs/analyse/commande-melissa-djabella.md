# Analyse de la commande – Saison feux 2027 (SDMIS 69)

**Exercice 1 – De la commande aux données, partie B (individuelle)**
**Nom :** Melissa DJABELLA
**Projet :** feux-de-foret-auvergne-rhone-alpes
**Module :** Modélisation et Pipeline de données (EU01) – MD5
**Date :** 16/11/2026

## 1. Les questions

Ce que j'ai compris de la commande : la direction du SDMIS doit prendre deux décisions. D'abord, où concentrer ses moyens humains et financiers pour lutter contre les départs de feu. Ensuite, à partir de quel niveau de l'indice Météo des forêts déclencher le dispositif renforcé, sachant que le budget ne permet pas de renforcer tout le département pendant tout l'été.

Voici les questions que je me pose, chacune avec la décision qu'elle permettrait de prendre.

1. **Où se passent vraiment les départs de feu dans le Rhône ?** Quelles communes ou zones sont les plus touchées, pas seulement en nombre de feux mais aussi en gravité ? Ça permettrait de décider où envoyer les patrouilles, le guet et le budget.

2. **À partir de quelle valeur de l'indice le risque de feu grimpe-t-il vraiment chez nous ?** C'est la base pour fixer un nouveau seuil de déclenchement du dispositif renforcé.

3. **Combien de fois l'indice se trompe-t-il ?** Combien de jours il annonce un danger élevé sans aucun feu, et combien de feux partent un jour où il est au plus bas ? Ça permettrait de choisir le seuil qui fait le meilleur compromis entre dépenser pour rien et ne pas être prêt.

4. **À quels moments de l'été les feux partent-ils ?** En juillet-août, en semaine, en fin d'après-midi ? Ça aiderait à renforcer seulement aux bonnes périodes, puisque le budget ne permet pas de tenir tout l'été.

5. **D'où viennent les feux ?** Cause humaine ou naturelle, bords de route, lisières, zones de loisirs ? Selon la réponse, mieux vaut miser sur la prévention, le guet ou les patrouilles.

6. **L'indice se comporte-t-il pareil dans le Rhône et dans les autres départements de la région ?** Si non, un seuil unique n'a pas beaucoup de sens.

7. **Par rapport au reste de la France, où se situe le Rhône ?** Ça servirait à justifier le niveau de moyens demandé.

8. **Est-ce que les feux augmentent vraiment d'année en année ?** La direction part du principe que 2027 sera comme 2026 ou pire : il faut vérifier si les chiffres le confirment avant de dimensionner le budget.

9. **Combien coûte un feu au SDMIS, en effectifs, engins et temps passé ?** Sans ça, impossible de savoir ce qu'un renforcement permet de financer.

J'ai écarté des questions comme « combien de feux en France ? » ou « quel est l'indice moyen ? » : quelle que soit la réponse, la direction ne ferait rien de différent.

## 2. Les termes inconnus

Ce sont des définitions provisoires, à vérifier et à compléter dans le glossaire du groupe.

- **SDMIS** : le service d'incendie et de secours du Rhône, c'est-à-dire le commanditaire.
- **Météo des forêts** : l'indice quotidien de danger de feu de forêt publié par Météo-France. Je dois encore vérifier comment il est calculé, quels sont ses niveaux, à quelle maille géographique il existe et quel historique est disponible.
- **Indice et seuil** : le seuil est la valeur à partir de laquelle on change de niveau de danger. Je ne connais pas le seuil actuel du SDMIS.
- **Dispositif renforcé** : patrouilles, guet, etc. Je ne sais pas quels moyens exacts cela recouvre ni combien cela coûte par jour : à demander au SDMIS.
- **Départ de feu** : le début d'un feu détecté et signalé. À clarifier : à partir de quelle surface on le compte, et si on parle uniquement de feux de forêt ou aussi de végétation et de feux agricoles.
- **Fausse alerte** : indice élevé mais aucun feu. **Feu manqué** : feu qui part un jour d'indice bas. En vocabulaire data, ce sont des faux positifs et des faux négatifs.
- **Grain** : le niveau de détail d'une ligne de données (un feu, un jour, une commune…).
- **Emprise** : la zone géographique couverte par une donnée.
- **Fraîcheur** : le délai entre l'événement et le moment où la donnée est disponible.
- **Maille** : le carreau ou la zone sur lesquels une donnée météo est calculée.
- **Chef de centre** : le responsable d'un centre d'incendie et de secours, une source d'information terrain.
- **Base nationale des feux de forêt** : la base publique qui recense les feux. Je dois confirmer son nom exact et son contenu.
- **Occupation du sol et lisière** : la nature de la surface (forêt, prairie, bâti) et la frontière entre la forêt et les zones habitées.

## 3. Les besoins

Pour répondre à la commande, j'ai besoin de six choses :

- Savoir où et quand les feux sont partis, et leur gravité (questions 1, 4, 5 et 8).
- Connaître l'indice jour par jour, sur la même géographie que les feux (questions 2 et 3).
- Relier les deux par la date et le lieu, pour calculer pour chaque seuil possible les fausses alertes et les feux manqués (questions 2, 3 et 6).
- Refaire la même analyse sur les autres départements de la région et sur la France entière, pour comparer (questions 6 et 7).
- Connaître les moyens engagés sur chaque feu, pour traduire un seuil en budget (question 9).
- Avoir du contexte (occupation du sol, relief, lisières) pour comprendre pourquoi certaines zones brûlent plus que d'autres (questions 1 et 5).

À la fin, la direction attend un seuil recommandé et argumenté, une liste ou une carte des zones prioritaires, et une comparaison régionale et nationale, pour le 11 décembre.

## 4. Les données

Pour chaque besoin, voici la donnée idéale avec son grain, sa période, sa fraîcheur et son emprise. Les sources sont des pistes à valider dans l'inventaire du groupe.

**Les départs de feu** (questions 1, 4, 5, 7 et 8)
- Contenu : date, heure, commune ou coordonnées, surface brûlée, cause, type de végétation.
- Grain : une ligne par départ de feu.
- Période : 15 à 20 ans, jusqu'à l'été 2026 compris.
- Fraîcheur : la saison précédente complète.
- Emprise : France entière pour comparer, avec le détail du Rhône et de la région.
- Source envisagée : la base nationale des feux de forêt, plus les données internes du SDMIS.

**L'indice Météo des forêts** (questions 2, 3, 6 et 7)
- Grain : une ligne par zone et par jour.
- Période : la même que pour les feux, au moins sur les saisons estivales.
- Fraîcheur : quotidienne, avec l'historique complet.
- Emprise : France entière.
- Source envisagée : Météo-France (données publiques).

**Les interventions du SDMIS** (questions 3 et 9)
- Contenu : horaires, effectifs, engins, durée.
- Grain : une ligne par intervention.
- Période : au moins 5 ans, été 2026 inclus.
- Emprise : le Rhône.
- Source envisagée : le SDMIS, à lui demander.

**Le contexte du terrain** (questions 1 et 5)
- Contenu : occupation du sol, relief, lisières entre forêt et habitat.
- Grain : un polygone ou un carreau, qu'on pourra croiser avec les communes.
- Période : la dernière version disponible, ça évolue lentement.
- Emprise : la région.
- Source envisagée : les données publiques d'occupation du sol et de relief.

**Le référentiel des communes et départements** (toutes les questions)
- Grain : une ligne par commune.
- Période : version à jour, mise à jour une fois par an.
- Emprise : France.
- Source envisagée : le référentiel officiel des communes.

**Points de vigilance**
- Les feux non signalés ou éteints par des particuliers n'apparaissent pas : le nombre de feux est probablement sous-estimé.
- Si l'indice n'est pas à la même maille que les communes, il faudra définir une règle de rapprochement et la noter dans le journal des décisions.
- Les coordonnées précises ou adresses éventuelles sont à manier avec précaution (par exemple en agrégeant à la commune). À valider avec la personne responsable qualité et conformité.
- Pour calculer un seuil, il faut aussi les jours **sans feu** : l'historique complet des jours d'été est nécessaire, pas seulement ceux où un feu est parti.
