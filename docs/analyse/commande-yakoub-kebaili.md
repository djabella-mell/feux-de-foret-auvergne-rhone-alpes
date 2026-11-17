# Analyse de la commande — Yakoub Kebaili

Projet : feux-de-foret-auvergne-rhone-alpes
Commanditaire : Direction du SDMIS 69 (Rhône)
Échéance : réponse attendue le 11 décembre

---

## 0. Reformulation de la commande

Le SDMIS 69 prépare la saison feux 2027 avec un budget limité : il ne peut pas renforcer le dispositif sur tout le département pendant tout l'été. Il doit donc arbitrer :

1. **Où** concentrer les moyens humains et financiers pour lutter contre les départs de feu ?
2. **À partir de quel niveau** de la Météo des forêts déclencher le dispositif renforcé (patrouilles, guet, etc.) ?

Le seuil actuel est contesté sur le terrain, dans deux sens opposés :

- **fausses alertes** : danger annoncé élevé, aucun feu ;
- **feux « surprises »** : feux partis des jours où l'indice était au plus bas.

Le commanditaire veut comprendre le comportement de l'indice : dans le Rhône, dans les autres départements de la région, et par rapport au reste de la France.

**Décisions attendues** : (a) une carte de priorisation territoriale ; (b) un seuil d'indice (ou une règle) de déclenchement, avec son coût (jours de dispositif) et son efficacité (feux couverts).

---

## 1. Questions

Chaque question est reliée à une décision. Une question qui ne change rien à ce que ferait la direction n'est pas retenue.

| # | Question | Décision pilotée |
|---|----------|------------------|
| Q1 | Quelles communes ou zones du Rhône concentrent le plus de départs de feu (en nombre, par km² de surface combustible) sur les dernières années ? | Où positionner patrouilles, guet et moyens financiers |
| Q2 | Parmi ces zones, lesquelles cumulent beaucoup de départs **et** un fort enjeu (habitations en lisière de forêt, établissements recevant du public, accès difficile) ? | Arbitrer entre « là où ça brûle le plus » et « là où ça coûte le plus cher quand ça brûle » |
| Q3 | Quelle est la part des départs de feu survenus lorsque l'indice était au niveau le plus bas (les « feux surprises » dénoncés par certains chefs de centre) ? | Savoir si le seuil actuel laisse passer trop de feux |
| Q4 | Quelle est la part des jours à indice élevé sans aucun départ (les « fausses alertes ») ? | Savoir ce que coûte le seuil actuel en jours de dispositif inutiles |
| Q5 | Pour chaque seuil possible de l'indice, combien de jours de dispositif renforcé cela représente-t-il par été, et quelle part des départs de feu est couverte ? | **Choisir le seuil de déclenchement** (compromis coût / couverture) |
| Q6 | L'indice se comporte-t-il de la même façon dans le Rhône et dans les autres départements d'Auvergne-Rhône-Alpes (mêmes niveaux, même lien avec les départs) ? | Savoir si on peut s'appuyer sur les retours des départements voisins ou s'il faut un seuil propre au Rhône |
| Q7 | Comment le Rhône se situe-t-il par rapport au reste de la France (fréquence des feux, distribution de l'indice, lien indice / départs) ? | Positionner le Rhône (risque faible, moyen ou fort) pour justifier la demande de moyens |
| Q8 | L'indice (calculé à l'échelle d'un massif ou d'une zone) est-il adapté à la **maille fine** du département ? Les écarts entre la valeur de l'indice et la météo locale expliquent-ils les « feux surprises » ? | Décider s'il faut compléter l'indice par d'autres critères (vent, sécheresse des sols, jours depuis la dernière pluie, jour de la semaine) |
| Q9 | Quelles sont les causes des départs de feu (humaine, accidentelle, foudre, etc.) et à quels moments (jour de semaine, week-end, horaires, vacances) ? | Choisir **quand** et **comment** renforcer : guet, patrouilles, prévention auprès du public |
| Q10 | L'été 2026 était-il exceptionnel, et que dit-il sur 2027 ? Les étés comparables (météo, sécheresse) ont-ils eu les mêmes caractéristiques ? | Calibrer l'hypothèse « autant ou plus de feux qu'en 2026 » et dimensionner le budget |

**Question prioritaire (cœur de la commande)** : Q5, soutenue par Q3 et Q4. C'est elle qui produit la recommandation chiffrée de seuil.

**Hypothèses à tester** :

- H1 : l'indice est un bon prédicteur des départs de feu **à l'échelle régionale**, mais moins bon à l'échelle locale du Rhône.
- H2 : une partie des départs de feu est liée à des facteurs humains (week-end, vacances) que l'indice ne capture pas.
- H3 : un seuil unique est sous-optimal, et un seuil différencié selon la zone ou le moment de la saison serait meilleur.

---

## 2. Termes inconnus

À intégrer au glossaire du groupe. Les définitions sont à **valider** (source à citer dans le glossaire).

| Terme | Définition provisoire | À vérifier / pourquoi c'est important |
|-------|-----------------------|----------------------------------------|
| **SDMIS** | Service départemental-métropolitain d'incendie et de secours du Rhône (SDMIS 69) : les pompiers du Rhône et de la Métropole de Lyon | Notre commanditaire ; périmètre = Rhône + Métropole de Lyon, ce qui change l'emprise |
| **Météo des forêts** | Service de Météo-France qui informe sur le niveau de danger météorologique de feu de forêt, par zone et par jour | Quel niveau exact de zonage ? Quelle fréquence de mise à jour ? Quelle historisation ? |
| **Indice (IFM, Indice Forêt Météo)** | Indice numérique de danger météorologique de feu de forêt, calculé à partir de la température, de l'humidité, du vent et des précipitations | Formule, échelle, découpage en niveaux (faible à extrême), historique disponible |
| **Niveau de danger** | Classe de l'indice (du plus faible au plus élevé) | Correspondances entre valeurs d'indice et niveaux ; seuils de passage |
| **Dispositif renforcé** | Mesures supplémentaires (patrouilles, guet, etc.) déclenchées par le SDMIS en période de danger | Quel coût par jour ? Quelles ressources ? Définition précise à demander |
| **Départ de feu** | Début d'incendie signalé et pris en charge | Définition retenue (seuil de surface ? intervention SDMIS ?) à préciser pour ne pas mélanger les sources |
| **Feu de forêt / feu de végétation** | Incendie touchant forêt, lande, garrigue, broussailles (seuil de surface selon la base) | Les sources n'utilisent pas toutes la même définition |
| **BDIFF** | Base de données sur les incendies de forêt en France | Source potentielle des départs de feu : couverture géographique, période, qualité de géolocalisation |
| **Prométhée** | Base des incendies de forêt de l'espace méditerranéen | À vérifier : couvre-t-elle notre région ? Probablement pas le Rhône |
| **Grain** | Niveau de détail d'une ligne de donnée (un jour × une commune, un feu, etc.) | Essentiel pour croiser indice et feux |
| **Emprise** | Zone géographique couverte par la donnée | Rhône seul, région, France |
| **Fraîcheur** | Délai entre l'événement et sa disponibilité dans la donnée | Pour un usage opérationnel, il faut un indice du jour et du lendemain |
| **Faux positif / faux négatif** | Alerte sans feu / feu sans alerte | Cadre du compromis de seuil (Q3, Q4, Q5) |
| **Rappel / précision** | Part des feux couverts par l'alerte / part des alertes suivies d'un feu | Métriques pour comparer les seuils |
| **Zone Naturelle-Urbaine (interface forêt-habitat), lisière** | Zone où habitations et végétation se touchent | Facteur d'enjeu (Q2) |
| **Maille / zonage** | Découpage du territoire utilisé pour publier l'indice | Peut ne pas coïncider avec les communes ou le périmètre du SDMIS |
| **Titre RNCP** | Certification professionnelle visée par la formation | Contexte de l'évaluation (gestion de projet, traçabilité) |

---

## 3. Besoins

### 3.1 Ce que le livrable doit permettre

1. Une **carte de priorisation** du Rhône (où concentrer les moyens), argumentée.
2. Une **recommandation de seuil** de la Météo des forêts, avec le compromis chiffré : jours de dispositif par été vs. part des feux couverts.
3. Un **positionnement comparatif** : Rhône vs. autres départements de la région vs. France.
4. Les **limites** de l'analyse (qualité des données, représentativité, hypothèses).

### 3.2 Besoins fonctionnels

- Pouvoir **joindre**, au même grain (jour × zone), l'indice et les départs de feu.
- Pouvoir **rejouer** l'analyse avec un autre seuil ou un autre zonage.
- Pouvoir **comparer** des territoires (Rhône, départements de la région, France).
- Pouvoir **documenter** la provenance et la qualité de chaque donnée (fiches d'identité des sources).

### 3.3 Contraintes et points d'attention

- **Calendrier** : réponse attendue le 11 décembre (travail de groupe puis individuel, donc périmètre à resserrer).
- **Budget du commanditaire** : la recommandation doit chiffrer le coût en jours de dispositif.
- **Données personnelles** : les bases d'intervention peuvent contenir des adresses ou des informations nominatives ; à anonymiser ou agréger (responsable qualité et conformité).
- **Rareté des événements** : peu de feux par an dans le Rhône, donc risque de conclusions fragiles ; à signaler et à compenser par la comparaison régionale.
- **Cohérence des définitions** entre les sources (feu de forêt vs. feu de végétation).

---

## 4. Données

Pour chaque question, la donnée idéale (grain, période, fraîcheur, emprise) et la source envisagée. Les sources citées sont des **pistes à vérifier** (accès, licence, couverture réelle).

| Q | Donnée idéale | Grain | Période | Fraîcheur | Emprise | Source envisagée |
|---|---------------|-------|---------|-----------|---------|------------------|
| Q1, Q2, Q9 | Liste des départs de feu avec date, heure, localisation, surface, cause | 1 ligne = 1 départ de feu (géolocalisé) | 10 à 15 ans au minimum, dont l'été 2026 | Mise à jour annuelle acceptable (analyse a posteriori) | Rhône (avec marge sur les départements voisins) | Interventions du SDMIS 69 (idéal), BDIFF, données publiques d'interventions |
| Q3, Q4, Q5, Q6, Q7 | Indice de danger de la Météo des forêts, valeur et niveau, historisé | 1 ligne = 1 jour × 1 zone de la Météo des forêts | Même période que les feux | Quotidienne en opérationnel ; historique complet pour l'analyse | France entière (pour la comparaison nationale) | Météo-France (data.gouv.fr ou portail de données publiques) : à vérifier si l'historique par zone existe |
| Q6, Q7 | Départs de feu au niveau national et régional | Départ de feu ou commune × année, selon disponibilité | Même période | Annuelle | France, avec détail Auvergne-Rhône-Alpes | BDIFF ; Prométhée pour la zone méditerranéenne |
| Q8 | Données météo fines (température, humidité, vent, cumul de pluie, sécheresse des sols) | 1 ligne = 1 jour × 1 point ou une maille fine | Même période | Quotidienne | Rhône et départements voisins | Météo-France (observations, réanalyses) |
| Q2 | Occupation du sol (forêt, lande, urbain), lisières, bâti | Polygone ou maille de 100 m | Dernière version disponible | Mise à jour tous les quelques ans | Rhône | Corine Land Cover, IGN (BD Forêt, BD TOPO) |
| Q2 | Enjeux : établissements sensibles, densité de population | Commune ou carreau | Dernière version | Annuelle | Rhône | INSEE, IGN, données publiques |
| Q1, Q5, Q7 | Référentiels géographiques et calendrier | Commune, département, région ; jour | Toute la période | Stable | France | IGN (Admin Express), INSEE (COG), calendrier des jours fériés et vacances scolaires |
| Q10 | Indicateurs de sécheresse / caractérisation de l'été 2026 | 1 ligne = 1 jour × zone, ou agrégat saisonnier | Étés historiques + 2026 | Annuelle | Rhône et région | Météo-France |
| Q5 | Coût du dispositif renforcé | 1 ligne = 1 jour de dispositif (ou forfait) | Récent | À fournir par le SDMIS | Rhône | **À demander au commanditaire** : sans cela, on exprime le coût en jours uniquement |

### 4.1 Données à demander au commanditaire

- Le **seuil actuel** et la règle exacte de déclenchement du dispositif.
- Les **dates et lieux des feux de 2026** ainsi que l'historique d'interventions.
- Le **coût unitaire** d'un jour de dispositif renforcé et le budget disponible.
- Le **périmètre exact** (Rhône seul ou Rhône + Métropole de Lyon).

### 4.2 Points de vigilance sur la qualité

- Départs de feu non déclarés ou mal géolocalisés (le biais touche surtout les petits feux).
- Changements de définition ou de méthode de collecte au fil des années.
- Décalage de zonage entre l'indice (zones) et les feux (points) : il faudra une table de correspondance commune → zone.
- Valeurs manquantes de l'indice certains jours, ou hors saison (l'indice peut n'être publié qu'en été).

### 4.3 Priorité de collecte (premier lot)

1. Départs de feu (SDMIS ou BDIFF), indispensables.
2. Historique de l'indice par zone, indispensable.
3. Référentiels géographiques (communes, zones), nécessaires pour la jointure.
4. Occupation du sol et enjeux : dans un second temps.

---

## Annexe : matrice questions × données (aperçu)

| Q | Départs de feu | Indice | Météo fine | Occupation du sol | Enjeux | Référentiels | Coût |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Q1 | ● | | | | | ● | |
| Q2 | ● | | | ● | ● | ● | |
| Q3 | ● | ● | | | | ● | |
| Q4 | ● | ● | | | | ● | |
| Q5 | ● | ● | | | | ● | ● |
| Q6 | ● | ● | | | | ● | |
| Q7 | ● | ● | | | | ● | |
| Q8 | ● | ● | ● | | | ● | |
| Q9 | ● | | | | | ● | |
| Q10 | ● | ● | ● | | | | |
