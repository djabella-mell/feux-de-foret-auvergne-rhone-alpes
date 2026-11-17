---
updated: 2026-11-17
---
# Analyse de la commande - Lynda LAZRI

**Projet :** saison des feux de forêt 2027, Auvergne-Rhône-Alpes. **Périmètre principal :** Rhône (69).

## 1. Les questions

Quatre questions dont la réponse aiderait la direction à trancher.

> [!test] Test
> Le test : si la réponse est X, la direction fait A ; si elle est Y, elle fait B. Si A et B sont identiques, ce n'est pas une question analytique pertinente.

1. **Quels secteurs du Rhône concentrent les départs de feu d'été, et cette concentration tient-elle d'une année sur l'autre ?**
   - Quelques communes regroupent l'essentiel des feux chaque année → la direction y affecte en priorité patrouilles et guet.
   - Les feux changent de secteur chaque année → elle garde une réserve mobile plutôt que des postes fixes.
2. **Pour chaque niveau de la Météo des forêts, quelle proportion de journées connaît au moins un départ de feu dans le Rhône ?**
   - La proportion augmente nettement avec le niveau → l'indice est un bon déclencheur, et la direction garde une règle fondée sur lui.
   - La proportion est la même quel que soit le niveau → elle ne s'y fie pas seule et ajoute d'autres critères (période, secteur).
3. **Combien de départs de feu surviennent les jours classés « faible », et à quels moments de l'année ?**
   - Ils sont nombreux et regroupés sur une période (printemps, moissons) → la direction ajoute un déclencheur calendaire sur cette période.
   - Ils sont rares ou dispersés → elle accepte ce risque résiduel avec le dispositif courant.
4. **Combien de journées de dispositif renforcé chaque seuil déclencherait-il, et quelle part des journées avec feu couvrirait-il ?**
   - Un seuil couvre la majorité des journées avec feu pour un nombre de jours compatible avec le budget → la direction adopte ce seuil.
   - Aucun seuil ne concilie les deux → elle combine un seuil plus bas avec un ciblage géographique (Q1).

**Point de vigilance :** un jour sans incendie malgré un danger élevé ne prouve pas que l'indicateur est erroné. Le danger météorologique n'est pas une prédiction certaine d'un départ de feu.

## 2. Les termes inconnus

Les mots de la commande que vous ne savez pas définir précisément, ou qui peuvent se comprendre de plusieurs façons.

| Terme | Ce que je crois qu'il veut dire | Ce qu'il faudrait vérifier |
|---|---|---|
| SDMIS 69 | Service départemental-métropolitain d'incendie et de secours du Rhône et de la Métropole de Lyon | Que l'analyse couvre les deux collectivités (69D et 69M dans le COG) |
| Météo des forêts | Information de danger d'incendie de Météo-France | Échelle géographique (département), niveaux (1 à 4), historique (depuis 2024 seulement) |
| Départ de feu | Feu de forêt ou de végétation constaté | Signalements ou incendies confirmés ? Feux agricoles inclus ? |
| Dispositif renforcé | Patrouilles, guet, prépositionnement | Effectifs, coût par jour, activation par secteur possible ? |
| Seuil de déclenchement | Niveau à partir duquel on active le dispositif | Règle actuelle du SDMIS, échéance J+1 ou J+2 |
| Journée avec feu | Jour et zone où au moins un départ est constaté | Règle d'agrégation (département ou secteur) |
| Fausse alerte / feu non couvert | Indice haut sans feu / feu un jour d'indice bas | À employer avec prudence (voir le point de vigilance) |
| Emprise | Territoire couvert par les données | Rhône, région, France |
| Grain | Niveau de détail d'une ligne | Événement, jour, commune, zone de prévision |

## 3. Les besoins

La décision à éclairer, en une phrase : choisir **où** renforcer la prévention dans le Rhône et **à partir de quel niveau** de la Météo des forêts déclencher le dispositif renforcé à l'été 2027, sans renforcer tout le département tout l'été.

Ce qui manque dans la commande pour y répondre (une information, une précision, une hypothèse à confirmer) :
- La règle de déclenchement actuelle et le coût d'une journée de renforcement.
- La définition d'un « départ de feu » retenu par le SDMIS.
- L'accès aux interventions du SDMIS, notamment pour 2026 (absent des sources publiques).
- La possibilité d'activer le dispositif par secteur plutôt que sur tout le département.
- Hypothèse à confirmer : 2027 « comme 2026 » est un scénario de dimensionnement, pas une prévision.

## 4. Les données

Pour chaque question, la donnée qu'il vous faudrait idéalement pour répondre.

| Question | Donnée idéale | Grain (une ligne = ?) | Période | Fraîcheur | Emprise géographique |
|---|---|---|---|---|---|
| 1 | Départs de feu confirmés : date, commune, type, surface ; surface forestière par commune | 1 feu ; 1 commune pour la forêt | Plusieurs saisons jusqu'en 2026 | Saison précédente consolidée | Rhône (communes), comparaison régionale |
| 2 | Niveau de la Météo des forêts de chaque jour **et** calendrier complet avec les jours sans feu | 1 jour × 1 département | Période commune avec les feux (2024-2026) | Quotidienne | Rhône, région, France |
| 3 | Départs de feu avec mois, heure, cause, et niveau du jour (ou absence de bulletin) | 1 feu | Plusieurs saisons, y compris le printemps | Saison précédente | Rhône, région |
| 4 | Niveaux quotidiens, journées avec feu, coût d'une journée de renfort | 1 jour × 1 département ; 1 type de moyen | Saisons récentes et budget 2027 | Dernier budget | Rhône |
