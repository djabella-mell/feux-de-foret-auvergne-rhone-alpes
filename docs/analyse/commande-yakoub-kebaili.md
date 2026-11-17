---
updated: 2026-11-17
---
# Analyse de la commande - Yakoub KEBAILI

Angle de cette analyse : en tant que responsable pipeline et modèle, je pars de ce qu'il faudra **joindre et compter** pour que chaque question tienne. Une question dont les données ne peuvent pas être rapprochées au bon grain ne pourra pas être répondue.

## 1. Les questions

Quatre questions dont la réponse aiderait la direction à trancher.

> [!test] Test
> Le test : si la réponse est X, la direction fait A ; si elle est Y, elle fait B. Si A et B sont identiques, ce n'est pas une question analytique pertinente.

1. **Le niveau J+1 publié la veille suffit-il, ou le niveau J+2 de l'avant-veille donne-t-il la même information ?**
   - J+2 donne presque toujours le même niveau → la direction peut décider du renfort **deux jours avant**, ce qui laisse le temps de rappeler du personnel.
   - J+2 se trompe souvent sur les jours qui comptent → elle décide la veille, avec un dispositif d'astreinte capable de monter en 24 h.
2. **Rapporté à la surface boisée, le Rhône a-t-il plus de feux par journée « modéré » ou « élevé » que les départements voisins ?**
   - Plus → le seuil du Rhône doit être plus bas que celui de ses voisins.
   - Moins ou autant → il peut s'aligner, et ses moyens peuvent servir de renfort aux voisins ces jours-là.
3. **Les jours « élevé » du Rhône tombent-ils en même temps que ceux de la Loire, de l'Isère et de l'Ain ?**
   - Oui → pas de renforts extérieurs à attendre ces jours-là : la direction dimensionne une réserve propre.
   - Non → elle peut compter sur des renforts mutualisés et dimensionner plus juste.
4. **Quelle part des feux et de la surface brûlée survient hors de la période de publication du bulletin ?**
   - Une part importante → la direction prévoit un déclencheur printanier distinct du seuil d'été.
   - Une part négligeable → la règle « à partir du niveau X » suffit.

## 2. Les termes inconnus

Les mots de la commande que vous ne savez pas définir précisément, ou qui peuvent se comprendre de plusieurs façons.

| Terme | Ce que je crois qu'il veut dire | Ce qu'il faudrait vérifier |
|---|---|---|
| Niveau de la Météo des forêts | Niveau 1 à 4 par département, J+1 et J+2 | Le seuil actuel porte-t-il sur J+1 ou sur J+2 ? |
| « Date » d'un bulletin | Jour où le niveau s'applique | **Faux** : c'est la date d'émission. Le jour cible est D+1 ou D+2 (D-03). |
| Département 69 | Le Rhône | Il regroupe deux collectivités (69D, 69M) ; les sources ne donnent que « 69 » |
| Commune d'un feu | Code INSEE de la commune | Le code change lors des fusions : quel millésime du COG ? |
| Journée avec feu | Jour où un feu a démarré | Jour calendaire en heure de Paris ou en UTC ? (Les bulletins sont horodatés en UTC.) |
| Surface boisée | Surface de forêt d'une commune | Source (BD Forêt V2), millésime du Rhône |
| Dispositif renforcé | Moyens supplémentaires activés certains jours | Délai d'activation : 24 h ? 48 h ? (conditionne Q1) |
| Région | Auvergne-Rhône-Alpes, 12 départements | — |

## 3. Les besoins

La décision à éclairer, en une phrase : définir une règle d'engagement du dispositif renforcé (où, à quel niveau, avec quelle anticipation) applicable dès le printemps 2027.

Ce qui manque dans la commande pour y répondre (une information, une précision, une hypothèse à confirmer) :
- Le délai de mise en place du dispositif renforcé (il fixe l'échéance utile : J+1 ou J+2).
- Le seuil actuel, pour comparer la nouvelle règle à l'existante.
- Les feux 2026 du Rhône, absents de la BDIFF.
- La règle d'agrégation géographique des décisions (département entier ou secteur).

## 4. Les données

Pour chaque question, la donnée qu'il vous faudrait idéalement pour répondre.

| Question | Donnée idéale | Grain (une ligne = ?) | Période | Fraîcheur | Emprise géographique |
|---|---|---|---|---|---|
| 1 | Niveaux J+1 et J+2 de chaque bulletin, remis au jour cible | 1 département × 1 jour cible × 1 échéance | 2024-2026 | Quotidienne | Rhône, région |
| 2 | Feux par jour et niveau du jour ; surface boisée par département | 1 département × 1 jour ; 1 département | 2024-2025 (période commune) ; BD Forêt 2007-2018 | Annuelle | 12 départements de la région |
| 3 | Niveau J+1 par département et par jour | 1 département × 1 jour cible | 2024-2026 | Quotidienne | Rhône et départements limitrophes |
| 4 | Feux avec date d'alerte toute l'année ; dates de publication du bulletin | 1 feu ; 1 jour | 2006-2025 (feux), 2024-2026 (bulletin) | Annuelle | Région |

**Premiers résultats du 17/11** (scripts `src/analyse_seuils.py`) :
- Q1 : J+1 et J+2 donnent le même niveau dans 93,3 % des cas (France, 2024-2026).
- Q4 : 33 % des feux de la région et 54 % de la surface en 2024-2025 sont hors saison du bulletin.
- Q3 : sur les 15 jours « élevé » du Rhône (2025-2026), au moins un voisin (Ain, Isère, Loire) est aussi « élevé » 12 fois, et les trois voisins sont au moins « modéré » les 15 jours. La Drôme et l'Ardèche sont « élevé » 13 et 12 fois. **Il ne faut pas compter sur les renforts des voisins ces jours-là.**
- Q2 reste à calculer : il faut la surface boisée (T-05).
