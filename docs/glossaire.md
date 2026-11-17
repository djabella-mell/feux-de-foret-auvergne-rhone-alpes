# Glossaire du projet (v1, 17/11/2026)

Ce glossaire fixe le sens de chaque mot **dans ce projet**. Pour chaque terme, on donne la définition retenue, sa source et ce qui reste à vérifier. Il reprend les termes inconnus des quatre analyses individuelles.

| Terme | Définition retenue dans le projet | Source / statut |
|---|---|---|
| **SDMIS 69** | Service départemental-métropolitain d'incendie et de secours. Il couvre le département du Rhône (69D) et la Métropole de Lyon (69M). Le sujet écrit « SMDIS 69 », ce qui est une coquille. | Commande. Les collectivités 69D et 69M figurent dans le COG 2026 (`v_ctcd_2026.csv`). |
| **Météo des forêts** | Bulletin public de Météo-France qui donne un niveau de danger « feux de forêt » par département, de 1 à 4, pour le lendemain (J+1) et le surlendemain (J+2). Il est émis chaque jour pendant la saison des feux. Ce n'est **pas** une prévision de départs de feu. | Fiche de jeu de données data.gouv.fr ; fichiers ouverts le 17/11 (voir la fiche source). |
| **Niveau de danger** | Valeur entière de 1 à 4 : 1 faible, 2 modéré, 3 élevé, 4 très élevé. C'est un niveau départemental, pas une valeur d'indice continue. | data.gouv.fr. Les fichiers ne contiennent que les niveaux 1 à 4. |
| **Jour cible** | Jour auquel s'applique un niveau : date d'émission + 1 pour `niveau_j1`, + 2 pour `niveau_j2`. La colonne `date` des fichiers est la date d'**émission**. | Fiche Météo des forêts. |
| **Seuil de déclenchement** | Niveau J+1 minimal à partir duquel le dispositif renforcé est activé dans un territoire. Exemple : « seuil modéré » signifie un renforcement les jours de niveau 2, 3 et 4. | Commande. Seuil actuel du SDMIS **inconnu** (question ouverte Q-02). |
| **Dispositif renforcé** | Moyens ajoutés au dispositif courant les jours de danger : patrouilles, guet, prépositionnement de groupes. | Commande. Composition et coût par jour **à obtenir** du SDMIS. |
| **Feu de forêt (BDIFF)** | Incendie enregistré dans la BDIFF, au sens du type de feu « F » de l'export. Il peut toucher la forêt, d'autres terres boisées ou des surfaces naturelles non boisées : l'export ventile la surface entre ces catégories. | Export BDIFF du 17/11 (critère « Type de feu : F »). Définitions détaillées dans `Définitions.pdf` du zip, **non vérifiées** : le fichier n'a pas encore été relu. |
| **Départ de feu** | Une ligne de la BDIFF, ou une intervention « feu de végétation » du SDMIS. La date retenue est la **date de première alerte**. | BDIFF, colonne « Date de première alerte ». |
| **Feu significatif** | Feu dont la surface parcourue atteint au moins 1 ha (définition provisoire). | Proposition du groupe, à valider avec la direction. |
| **Journée-département** | Une ligne de calendrier « département × jour cible » pendant la saison du bulletin. C'est l'unité de comptage des jours de renforcement. | Analyses individuelles. |
| **Couverture d'un seuil** | Part des feux (ou des feux significatifs, ou de la surface) survenus un jour où le niveau J+1 atteignait le seuil. | Analyses individuelles. |
| **Fausse alerte** | Journée-département où le seuil est atteint sans aucun départ de feu. Ce n'est pas une erreur de l'indice, qui mesure un danger et non une probabilité de feu. C'est un coût de renforcement « inutile » a posteriori. | Analyses individuelles. |
| **Feu non couvert** | Feu survenu un jour où le niveau J+1 était sous le seuil, ou hors de la période de publication du bulletin. | Analyses individuelles. |
| **Hors saison** | Période sans bulletin Météo des forêts. Les données montrent des émissions du 03/06 au 30/09 en 2024-2025 et du 28/05 au 05/10 en 2026. | Fichiers MdF ouverts le 17/11. |
| **Emprise** | Territoire couvert par une donnée : Rhône, région Auvergne-Rhône-Alpes (84) ou France métropolitaine (96 départements dans la Météo des forêts). | Cours S1. |
| **Grain** | Ce que représente une ligne. Exemples : « un feu » (BDIFF) ; « un département × un jour d'émission » (Météo des forêts) ; « une commune » (COG). | Cours S1. |
| **Millésime (COG)** | Année de référence du Code officiel géographique. Les fusions de communes changent les codes chaque 1er janvier. | Cours S1, piège « référentiel ». Contrôlé le 17/11 : 25 codes BDIFF absents du COG 2026. |
| **Source de vérité** | Source retenue quand deux sources se contredisent sur une même donnée. Le choix par donnée est fait dans la matrice. | Cours S1. |
| **Proxy** | Donnée de remplacement, moins exacte, utilisée quand la donnée idéale manque. Son biais est documenté. | Cours S1. |
| **Vérité à date** | Valeur telle qu'elle était connue à une date donnée. Pour la Météo des forêts, c'est le niveau publié la veille, jamais une valeur recalculée après coup. | Cours S2. |
