# Analyse de la commande — SDMIS 69 (Rhône)

**Projet :** Saison des feux de forêt 2027 — Auvergne-Rhône-Alpes  
**Périmètre principal :** département du Rhône (69)  
**Nature du livrable :** analyse individuelle préliminaire de la commande

## 1. Questions métier et décisions associées

La direction du SDMIS souhaite savoir où concentrer les moyens de prévention et à partir de quel niveau de la Météo des forêts déclencher un dispositif renforcé. Les questions ci-dessous sont formulées pour conduire à des décisions opérationnelles.

| Question à analyser | Décision que la direction pourrait prendre |
|---|---|
| Quelles zones du Rhône concentrent les départs de feu, notamment pendant la saison estivale ? | Prioriser les secteurs à surveiller et y affecter davantage de patrouilles ou de moyens de guet. |
| À quelles périodes et dans quelles conditions les départs de feu sont-ils les plus fréquents ? | Adapter les calendriers de surveillance et les effectifs aux périodes les plus sensibles. |
| Pour chaque niveau de la Météo des forêts, quelle proportion de journées connaît au moins un départ de feu dans le Rhône ? | Vérifier si les niveaux de danger distinguent utilement les journées avec et sans départ de feu. |
| Combien de départs de feu surviennent lors des journées classées à faible danger ? | Mesurer le risque de ne pas déclencher le dispositif et envisager des mesures complémentaires. |
| Combien de journées de dispositif renforcé seraient déclenchées selon différents seuils, et combien de journées avec feu seraient couvertes ? | Choisir un seuil conciliant couverture du risque et coût de mobilisation. |
| Le comportement de l'indicateur dans le Rhône diffère-t-il de celui observé dans les autres départements d'Auvergne-Rhône-Alpes et en France ? | Déterminer si un seuil spécifique au Rhône doit être étudié plutôt qu'une règle uniforme. |
| Quels secteurs et quelles périodes devraient être prioritaires si le budget ne permet pas de renforcer la surveillance partout ? | Construire un scénario de déploiement ciblé, sous contrainte budgétaire. |

**Point de vigilance :** un jour sans incendie malgré un danger élevé ne prouve pas, à lui seul, que l'indicateur est erroné : le danger météorologique n'est pas une prédiction certaine d'un départ de feu. Il faut distinguer le risque d'éclosion, l'exposition et les moyens de prévention déjà mobilisés.

## 2. Termes inconnus ou à clarifier

| Terme | Définition ou clarification nécessaire |
|---|---|
| SDMIS 69 | Service départemental-métropolitain d'incendie et de secours du Rhône et de la métropole de Lyon. |
| Météo des forêts | Information de danger d'incendie diffusée par Météo-France ; préciser son échelle géographique, ses niveaux et la disponibilité de l'historique. |
| Départ de feu | Préciser les événements retenus : feux de forêt et de végétation, signalements ou incendies confirmés. |
| Dispositif renforcé | Préciser les mesures concernées : patrouilles, guet, prépositionnement, effectifs et coûts. |
| Seuil de déclenchement | Niveau de danger à partir duquel le dispositif est activé ; vérifier la règle actuellement appliquée. |
| Journée avec feu | Journée et zone géographique où au moins un départ de feu est constaté ; définir la règle d'agrégation. |
| Fausse alerte / feu non couvert | Termes d'évaluation d'un seuil ; à employer avec prudence, car un danger élevé n'implique pas nécessairement un incendie. |
| Emprise | Territoire couvert par les données : Rhône, autres départements de la région, France. |
| Grain | Niveau de détail d'un enregistrement : événement, jour, commune, zone de prévision, etc. |

## 3. Besoins métier

1. **Localiser les priorités :** identifier les zones du Rhône où les moyens de prévention auraient le plus d'utilité.
2. **Comprendre les périodes à risque :** repérer les variations saisonnières et météorologiques pour planifier les équipes.
3. **Évaluer la Météo des forêts :** comparer les niveaux annoncés aux départs de feu réellement constatés, y compris les journées sans feu.
4. **Arbitrer le seuil :** comparer plusieurs règles de déclenchement selon les journées couvertes, les journées non couvertes et la charge de surveillance.
5. **Situer le Rhône :** comparer les résultats aux autres départements d'Auvergne-Rhône-Alpes et au niveau national, en tenant compte des différences d'exposition.
6. **Respecter le budget :** proposer des priorités géographiques et temporelles plutôt qu'un renforcement permanent sur tout le département.

**Livrable décisionnel visé :** une recommandation argumentée sur les zones prioritaires et le seuil de renforcement pour l'été 2027, sous réserve de la qualité et de la disponibilité des données.

## 4. Données idéales

Les données ci-dessous constituent des **besoins à vérifier**, et non une liste de sources déjà obtenues.

| Donnée souhaitée | Grain idéal | Période souhaitée | Fraîcheur souhaitée | Emprise |
|---|---|---|---|---|
| Départs de feu confirmés (date, localisation, type, surface si disponible) | Un événement | Plusieurs saisons récentes, idéalement jusqu'en 2026 | Données consolidées les plus récentes | Rhône, région, France |
| Historique des niveaux de la Météo des forêts | Jour × zone de prévision | Toute la période historique disponible, alignée sur les feux | Quotidienne | Rhône, région, France |
| Calendrier complet, y compris jours sans feu | Jour × zone de prévision | Même période que l'indicateur | Quotidienne | Rhône, région, France |
| Conditions météo (vent, température, humidité, pluie) | Jour × zone ou station | Même période que les feux | Quotidienne | Rhône, éventuellement comparateurs |
| Surface forestière et autres mesures d'exposition | Commune ou département | Millésime récent cohérent | Annuelle ou selon actualisation | Rhône, région, France |
| Patrouilles, moyens engagés et règle actuelle de déclenchement | Jour × secteur × type de moyen | Saisons récentes | Données opérationnelles consolidées | Rhône |
| Coûts des moyens renforcés et enveloppe disponible | Jour × type de moyen / budget saisonnier | Saisons récentes et prévision 2027 | Dernier budget disponible | Rhône |

### Points à vérifier avant l'analyse

- L'historique de la Météo des forêts est-il accessible et comparable sur toute la période ? Si non, limiter l'étude croisée à la période commune.
- Les zones de prévision correspondent-elles aux communes ou secteurs des incendies ? Définir une règle de rapprochement géographique.
- Les dates et heures des feux permettent-elles un rapprochement fiable avec le niveau de danger du jour ?
- Les données incluent-elles les journées sans incendie, indispensables pour évaluer les seuils ?
- Les données de coûts et de moyens sont-elles accessibles au groupe ? Sinon, expliciter les hypothèses et les limites.
- Les comparaisons territoriales peuvent-elles être rapportées à une exposition comparable (surface forestière, par exemple) ?

**Conclusion provisoire :** l'analyse doit aider le SDMIS 69 à choisir *où* renforcer la prévention et *quand* déclencher le dispositif. Aucune recommandation chiffrée sur le seuil ou les secteurs ne peut être arrêtée avant la collecte et l'étude des données.
