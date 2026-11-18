# Règles de qualité et contrôles du pipeline v1 (18/11/2026)

- **Responsable :** Lynda LAZRI (qualité et conformité) · **Relecture :** Yakoub KEBAILI (pipeline et modèle)
- **S'applique au :** [modèle cible](modele-cible.md), couches bronze et silver
- **État mesuré :** sur les fichiers extraits le 17/11/2026. Les tests eux-mêmes seront écrits avec le pipeline v0.1.

Chaque règle est un **test qui renvoie les lignes en faute** : zéro ligne, le test passe ; au moins une ligne, il échoue et l'on sait lesquelles regarder. Une règle porte toujours :
- un seuil ;
- une décision en cas d'échec ;
- la question qu'elle protège.

Les trois décisions possibles :
- **Bloquer :** le chargement s'arrête, rien ne passe vers la couche suivante.
- **Alerter :** le chargement continue, la responsable est prévenue et le rapport de qualité le signale.
- **Tolérer :** le défaut est connu, stable et documenté.

Les dimensions utilisées sont les six du cours (DAMA). La correspondance avec ISO/IEC 25012 est donnée en section 5.

Le type de test est celui de dbt. Les tests génériques sont `unique`, `not_null`, `accepted_values` et `relationships` ; un test **singulier** est une requête dédiée.

## 1. Bronze : chargement

| ID | Dimension | Énoncé : le test renvoie… | Type | Seuil | Décision | Protège | État au 17/11 |
|---|---|---|---|---|---|---|---|
| Q-PIP-01 | Unicité | …les tables dont le compte change quand on recharge les mêmes fichiers | singulier (charger, compter, recharger, recompter) | 0 | Bloquer | Toutes | À prouver au premier chargement |
| Q-PIP-02 | Validité (contrat de schéma) | …les fichiers où manque une colonne attendue (MDF : `date`, `num_dep`, `niveau_j1`, `niveau_j2` ; BDIFF : les 24 colonnes) | contrôle au chargement, statut « échec » au journal | 0 | Bloquer | Toutes | Justifié : le schéma de la Météo des forêts a changé deux fois en trois ans (nom de colonne en 2025 ; séparateur et format du code en 2026) |
| Q-PIP-03 | Complétude | …les chargements où lues ≠ insérées + rejetées, et pour la BDIFF où lues ≠ nombre annoncé dans le fichier | singulier sur le journal | 0 | Bloquer | Toutes | BDIFF : 4 072 lues = 4 072 annoncées |
| Q-PIP-04 | Complétude | …les chargements en succès qui n'insèrent aucune ligne | singulier sur le journal | 0 | Alerter | Toutes | — |

## 2. Staging : une source à la fois

### Météo des forêts : `stg_mdf__bulletins`

| ID | Dimension | Énoncé : le test renvoie… | Type | Seuil | Décision | Protège | État au 17/11 |
|---|---|---|---|---|---|---|---|
| Q-MDF-01 | Unicité | …les couples (`code_departement`, `date_emission`) présents plus d'une fois | `unique` | 0 | Bloquer | Q2 | 0 doublon |
| Q-MDF-02 | Validité | …les niveaux J+1 ou J+2 hors de {1, 2, 3, 4} | `accepted_values` | 0 | Bloquer | Q2 | 0 |
| Q-MDF-03 | Complétude des valeurs | …les niveaux vides | `not_null` | 0 | Bloquer | Q2 | 0 vide |
| Q-MDF-04 | Complétude de la population | …les couples bulletin × département métropolitain du COG absents | singulier | 0 | Alerter ; bloquer si le 69 manque | Q2, Q4 | 96 départements dans chacun des 371 bulletins |
| Q-MDF-05 | Complétude de la population | …les jours sans bulletin entre le premier et le dernier bulletin d'une saison | singulier | 0 | Alerter | Q2 | 0 trou (120, 120 et 131 bulletins) |
| Q-MDF-06 | Cohérence | …les codes département absents du COG | `relationships` | 0 | Bloquer | Q2, Q4 | 0 (96 codes) |
| Q-MDF-07 | Actualité | …en saison (juin à septembre), un dernier bulletin vieux de plus de 2 jours | singulier | 2 jours | Alerter en saison ; tolérer hors saison | Q2 | Saison 2026 close (dernier bulletin le 05/10/2026) |

### BDIFF : `stg_bdiff__feux`

| ID | Dimension | Énoncé : le test renvoie… | Type | Seuil | Décision | Protège | État au 17/11 |
|---|---|---|---|---|---|---|---|
| Q-BDF-01 | Unicité | …les `id_feu_bdiff` en double | `unique` | 0 | Bloquer | Toutes | 0 doublon |
| Q-BDF-02 | Validité | …les dates d'alerte hors de l'année `annee`, ou postérieures à l'extraction | singulier | 0 | Bloquer | Q2, Q3 | 0 |
| Q-BDF-03 | Validité | …les surfaces parcourues vides ou ≤ 0 | singulier | 0 | Alerter (un feu sans surface ne peut pas être classé « significatif ») | Q1, Q2 | 0 |
| Q-BDF-04 | Cohérence | …les feux où surface forêt > surface parcourue | singulier | 0 | Alerter | Q1, Q4 | 0 |
| Q-BDF-05 | Cohérence | …les feux dont le département ≠ les 2 premiers caractères du code commune | singulier | 0 | Alerter | Q1 | 0 |
| Q-BDF-06 | Validité | …les valeurs hors liste : `precision_surfaces` (Estimées, Mesurées), `cause_nature` (5 valeurs), `type_peuplement_code` (1 à 6) | `accepted_values` | 0 | Alerter : une nouvelle valeur signale un changement de formulaire | Q3 | 0 |
| Q-BDF-07 | Validité (plausibilité) | …les heures d'alerte à 00:00, probablement non saisies | singulier | < 1 % | Tolérer, documenté | Q3 (créneaux horaires) | 6 feux (0,15 %) |
| Q-BDF-08 | Complétude des valeurs | …les feux sans cause | singulier | suivi seulement | Tolérer : la cause est un indice, jamais une conclusion (M-7) | Q3 | Cause renseignée pour 46,7 % des feux (12,9 % dans le Rhône) |
| Q-BDF-09 | Complétude des valeurs | …les feux sans surface forêt | `not_null` en avertissement | suivi seulement | Tolérer | Q1, Q4 | 316 vides (7,8 %) |
| Q-BDF-10 | Complétude de la population | …les couples département × année sans aucun feu, comparés à la grille 12 départements × 20 ans | singulier | suivi seulement | Alerter, avec le verdict « avec réserve » (M-1) | Q1, Q4 | 68 couples sur 240. Rhône : 11 années sur 20 à 0 feu, et 41 de ses 62 feux en 2015. |
| Q-BDF-11 | Actualité | …une dernière année présente antérieure à N-1 | singulier | 1 an | Alerter | Q2 | 2025 présente (dernier feu le 14/12/2025) |
| Q-BDF-12 | Exactitude (signalée par la source) | …les fiches marquées « Données partielles ou non valides » | singulier | suivi seulement | Tolérer, signalé dans les analyses | Toutes | 122 feux (3,0 %) |

### COG 2026 : `stg_cog__*`

| ID | Dimension | Énoncé : le test renvoie… | Type | Seuil | Décision | Protège | État au 17/11 |
|---|---|---|---|---|---|---|---|
| Q-COG-01 | Unicité | …les `code_commune` en double | `unique` | 0 | Bloquer | Jointures | 0 |
| Q-COG-02 | Complétude de la population | …un nombre de communes du 69 différent de 266, ou une commune du 69 sans `code_ctcd` 69D ou 69M | singulier | 0 | Bloquer | Q1 (Rhône contre Métropole) | 208 (69D) + 58 (69M) |
| Q-COG-03 | Cohérence | …plus d'un millésime COG chargé | singulier | 0 | Bloquer | Jointures | 2026 seul |

## 3. Intermédiaire : consolidation et non-perte

| ID | Dimension | Énoncé : le test renvoie… | Type | Seuil | Décision | Protège | État au 17/11 |
|---|---|---|---|---|---|---|---|
| Q-CONS-01 | Unicité | …les codes de la table de passage qui mènent à plus d'une commune 2026 | `unique` sur `code_commune_origine` | 0 | Bloquer : sinon un feu serait dupliqué | Q1 | 25 codes, 25 destinations uniques |
| Q-CONS-02 | Complétude (non-perte) | …les feux de staging ni rattachés ni rejetés | singulier (anti-jointure) | 0 | Bloquer | Toutes | 4 072 = 4 072 rattachés + 0 rejeté |
| Q-CONS-03 | Cohérence | …les feux en table de rejet | singulier | 0 | Alerter : lire le motif, corriger la table de passage, rejouer | Q1 | 0 (les 48 feux à code ancien sont rattachés) |
| Q-CONS-04 | Complétude (non-perte) | …un écart entre la somme des surfaces de staging et celle des rattachés + rejetés | singulier | 0 m² | Bloquer | Q1, Q2 | 124 054 889 m² des deux côtés (≈ 12 405 ha) |
| Q-CONS-05 | Unicité (non-multiplication) | …les `feu_sk` en double dans `int_feux__danger`, ou un nombre de lignes différent de la staging | `unique` + singulier | 0 | Bloquer | Q2, Q3 | 4 072 attendus |
| Q-CONS-06 | Unicité | …les couples (`code_departement`, `jour_cible`) en double dans `int_mdf__danger_jour` | `unique` | 0 | Bloquer : garantit Q-CONS-05 | Q2 | — |
| Q-CONS-07 | Complétude (non-perte) | …un écart entre les niveaux J+1 non vides et les lignes de staging (et de même pour J+2) | singulier | 0 | Bloquer | Q2 | 35 616 J+1 et 35 616 J+2, sur 35 904 couples |
| Q-CONS-08 | Cohérence (jointure) | …les feux dont la date tombe dans la fenêtre des jours cibles J+1 mais qui n'ont pas de niveau | singulier | 0 | Bloquer : signale une jointure fausse (fuseau, format du code) | Q2 | 0 |
| Q-CONS-09 | Complétude de la population | …la part des feux sans bulletin, par année | indicateur | suivi seulement | Tolérer, reporté dans le rapport | Q3 | 2024-2025 : 112 feux sur 337 (33,2 %) |

Les nombres **et** les sommes se réconcilient : 37 lignes perdues et 37 dupliquées donneraient le bon total, mais de faux chiffres.

Quand un test bloquant échoue, on lit la table de rejet, on corrige (souvent la table de passage), puis on rejoue. Le rejeu est sans risque parce que le chargement est idempotent (Q-PIP-01).

## 4. Conformité RGPD

| ID | Énoncé : le test renvoie… | Type | Seuil | Décision | État |
|---|---|---|---|---|---|
| Q-RGPD-01 | …les colonnes interdites présentes dans `staging`, `intermediate` ou `marts` : décès et bâtiments (BDIFF) ; pour le SDMIS, adresse, coordonnées, requérant, agents, victimes | singulier sur le catalogue des colonnes | 0 | Bloquer | 0 attendu : ces colonnes sont supprimées en staging |
| Q-RGPD-02 | …les communes où une cause de feu est affichée alors qu'elles comptent moins de 3 feux | singulier sur la couche gold | 0 | Bloquer | À écrire avec la couche gold (S4) |

## 5. Correspondance avec ISO/IEC 25012

Le cours mentionne ISO/IEC 25012 comme référence. Les 15 caractéristiques se répartissent entre les règles ci-dessus et l'architecture du [modèle cible](modele-cible.md).

| Caractéristique ISO/IEC 25012 | Où elle est traitée |
|---|---|
| Exactitude | Exactitude syntaxique : règles de validité (Q-MDF-02, Q-BDF-02, 03, 06, 07). Exactitude sémantique **non vérifiée** : aucune source de référence terrain ; le fichier SDMIS servira de comparaison pour le 69. |
| Complétude | Q-MDF-03 à 05, Q-BDF-08 à 10, Q-COG-02, Q-CONS-02, 04, 07 |
| Cohérence | Q-BDF-04, 05, Q-MDF-06, Q-CONS-01, 03, 08 |
| Crédibilité | Fiches d'identité (producteur, méthode) ; sous-déclaration probable de la BDIFF hors zone méditerranéenne, écrite dans le rapport |
| Actualité | Q-MDF-07, Q-BDF-11 |
| Traçabilité | Colonnes `_fichier_source`, `_ligne_source`, `_empreinte_fichier` ; journal de chargement ; lineage généré par dbt |
| Disponibilité, récupérabilité | Silos datés jamais écrasés : tout l'entrepôt se reconstruit par rejeu |
| Confidentialité, accessibilité | Rôles par couche (modèle, section 5) ; Q-RGPD-01 |
| Conformité | Contrat de schéma Q-PIP-02 ; licences (modèle, section 5) |
| Compréhensibilité | Noms de colonnes explicites avec leur unité (`_m2`) ; glossaire ; dictionnaire de données au rendu final |
| Précision | Grain déclaré pour chaque table. Le niveau de danger n'existe qu'au département : c'est une limite pour Q1. |
| Portabilité, efficience | Formats d'origine conservés, SQL standard. Petits volumes : l'efficience n'est pas un enjeu. |

L'unicité, dimension du cours, n'a pas de caractéristique dédiée dans ISO/IEC 25012. Elle est couverte par les règles Q-*-01 et Q-CONS-05.

## 6. Rapport de qualité

Le rapport est daté et refait à chaque chargement important. Il comprend :
- le périmètre : source, date d'extraction, période couverte ;
- la synthèse par question, avec un verdict en mots ;
- le résultat des règles : lignes en faute, seuil, décision appliquée ;
- le détail des défaillances : dimension, test, décision faussée, propriétaire ;
- les limites : ce qui n'a pas pu être vérifié, écrit comme tel.

**Synthèse au 18/11/2026**

| Question | Verdict | Ce que cela veut dire pour la direction |
|---|---|---|
| Q1. Où les feux deviennent-ils graves ? | **Avec réserves** pour la région ; **non utilisable** pour le Rhône seul | La BDIFF ne compte que 62 feux en 20 ans dans le Rhône, dont 41 la même année : elle ne permet pas de dessiner une carte des secteurs du Rhône |
| Q2. À quel niveau se produisent les feux ? | **Avec réserves** | Une seule période commune aux deux sources (2024-2025) : 225 feux régionaux ont un niveau, mais 3 seulement dans le Rhône. Un seuil peut être estimé pour la région et transposé au Rhône, pas fixé pour le Rhône seul. |
| Q3. Pourquoi des feux à niveau bas ? | **Avec réserves** | Un feu sur trois (2024-2025) survient hors de la saison du bulletin ; la cause manque pour plus d'un feu sur deux |
| Q4. Le Rhône face à ses voisins ? | **Utilisable** côté indice ; **non utilisable** côté feux au national | La Météo des forêts couvre les 96 départements ; la BDIFF n'est extraite que pour la région, et la surface boisée manque encore |
