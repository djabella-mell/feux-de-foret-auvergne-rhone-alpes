# Règles de qualité et contrôles du pipeline v1 (18/11/2026)

- **Responsable :** Lynda LAZRI (qualité et conformité) · **Relecture :** Yakoub KEBAILI (pipeline et modèle)
- **S'applique à :** l'entrepôt décrit dans le [modèle cible](modele-cible.md), couches raw, staging et intermédiaire.
- **Implémentation :** chaque règle est une requête dans `pipeline/construire_entrepot.py`, exécutée à chaque construction. Le résultat est enregistré dans `qualite.resultats_tests`.
- **Résultats ci-dessous :** construction du 18/11/2026. Le périmètre est national (BDIFF : 52 810 feux, 97 départements) et la BD Forêt couvre Auvergne-Rhône-Alpes.

Chaque règle est un **test qui renvoie les lignes en faute** : zéro ligne, le test passe ; au moins une ligne, il échoue et l'on sait lesquelles regarder. Une règle porte toujours un seuil, une décision en cas d'échec et la question qu'elle protège.

Les trois décisions possibles :
- **Bloquer :** le script s'arrête, la couche suivante n'est pas alimentée.
- **Alerter :** le chargement continue, le défaut est signalé.
- **Tolérer :** le défaut est connu, stable et documenté.

Les dimensions utilisées sont les six du cours (DAMA). La correspondance avec ISO/IEC 25012 est donnée en section 5.

**Bilan du 18/11 :** 38 règles exécutées, 27 réussies, 5 alertes, 6 défauts tolérés. Aucune règle bloquante n'échoue.

## 1. Raw : chargement

| ID | Dimension | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|---|
| Q-PIP-01 | Unicité | …les tables raw dont le compte change quand on recharge les mêmes fichiers (option `--idempotence`) | 0 | Bloquer | ✅ 0 écart sur 25 tables |
| Q-PIP-02 | Validité (contrat de schéma) | …les fichiers où manque une colonne attendue | 0 | Bloquer | ✅ Implicite : une colonne absente fait échouer le staging. Le schéma de la Météo des forêts a changé deux fois en trois ans. |
| Q-PIP-03 | Complétude | …les chargements où lues ≠ insérées + rejetées, ou insérées ≠ nombre annoncé par la BDIFF | 0 | Bloquer | ✅ 0, les 18 fichiers BDIFF compris |
| Q-PIP-04 | Complétude | …les chargements en succès sans aucune ligne insérée | 0 | Alerter | ⚠️ Guyane : 0 feu sur 2006-2025, avec une ligne « Aucune données trouvées » mise en rejet. Normal. |
| Q-BDF-00 | Unicité | …les feux (Année, Numéro) livrés plusieurs fois par la source | 0 | Alerter | ⚠️ 1 : le feu 2013-6664 (Haute-Corse) apparaît sur deux lignes identiques. Dédoublonné en staging. |

## 2. Staging : une source à la fois

### Météo des forêts

| ID | Dimension | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|---|
| Q-MDF-01 | Unicité | …les (département, date d'émission) en double | 0 | Bloquer | ✅ |
| Q-MDF-02 | Validité | …les niveaux hors de 1 à 4 | 0 | Bloquer | ✅ |
| Q-MDF-03 | Complétude des valeurs | …les niveaux vides | 0 | Bloquer | ✅ |
| Q-MDF-04 | Complétude de la population | …les couples bulletin × département de métropole absents | 0 | Alerter | ✅ 96 départements dans les 371 bulletins |
| Q-MDF-05 | Complétude de la population | …les jours sans bulletin à l'intérieur d'une saison | 0 | Alerter | ✅ |
| Q-MDF-06 | Cohérence | …les codes département absents du COG | 0 | Bloquer | ✅ |
| Q-MDF-07 | Actualité | …en saison, un dernier bulletin vieux de plus de 2 jours | 2 jours | Alerter | Contrôle de saison, à automatiser avec le chargement quotidien |

### BDIFF

| ID | Dimension | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|---|
| Q-BDF-01 | Unicité | …les `id_feu_bdiff` en double après staging | 0 | Bloquer | ✅ |
| Q-BDF-02 | Validité | …les dates hors de l'année ou futures | 0 | Bloquer | ✅ |
| Q-BDF-03 | Validité | …les surfaces vides ou ≤ 0 | 0 | Alerter | ✅ |
| Q-BDF-04 | Cohérence | …les feux où surface forêt > surface parcourue | 0 | Alerter | ✅ |
| Q-BDF-05 | Cohérence | …les feux dont le département ≠ début du code commune | 0 | Alerter | ✅ |
| Q-BDF-06 | Validité | …les valeurs hors liste (précision, cause, peuplement) | 0 | Alerter | ✅ |
| Q-BDF-07 | Validité (plausibilité) | …les heures d'alerte à 00:00 | < 1 % | Tolérer | 135 feux (0,26 %) |
| Q-BDF-08 | Complétude des valeurs | …les feux sans cause | suivi | Tolérer (M-7) | 25 619 (48,5 %) ; Rhône : 54 sur 62 |
| Q-BDF-09 | Complétude des valeurs | …les feux sans surface forêt | suivi | Tolérer | 4 650 (8,8 %) |
| Q-BDF-10 | Complétude de la population | …les couples département × année sans aucun feu | suivi | Alerter (M-1) | 743 couples sur 1 940 ; Rhône : 11 années sur 20. S'y ajoutent les campagnes signalées sans données par la source (`stg_bdiff__notes_campagnes`). |
| Q-BDF-11 | Actualité | …une dernière année antérieure à N-1 | 1 an | Alerter | ✅ dernier feu le 31/12/2025 |
| Q-BDF-12 | Exactitude (source) | …les fiches signalées « partielles ou non valides » | suivi | Tolérer | 1 285 (2,4 %) |

### COG et BD Forêt

| ID | Dimension | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|---|
| Q-COG-01 | Unicité | …les codes commune en double | 0 | Bloquer | ✅ |
| Q-COG-02 | Complétude de la population | …un 69 différent de 208 communes 69D + 58 communes 69M | 0 | Bloquer | ✅ |
| Q-COG-03 | Cohérence | …plus d'un millésime COG | 0 | Bloquer | ✅ |
| Q-BDF-13 | Cohérence | …les départements dont les métadonnées BD Forêt datent la fin avant le début | suivi | Tolérer | 1 : Rhône (20/12/2010 → 26/07/2010) |
| Q-BDF-14 | Validité | …les polygones sans catégorie (forêt, lande, herbacée) | 0 | Alerter | ✅ |

## 3. Intermédiaire : consolidation et non-perte

| ID | Dimension | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|---|
| Q-CONS-01 | Unicité | …les codes de la table de passage menant à plusieurs communes | 0 | Bloquer | ✅ |
| Q-CONS-02 | Complétude (non-perte) | …les feux ni rattachés ni rejetés | 0 | Bloquer | ✅ 52 810 = 52 798 + 12 |
| Q-CONS-03 | Cohérence | …les feux en table de rejet | 0 | Alerter | ⚠️ 12 feux du Var au code 83999 (« commune inconnue »), 801 ha. Gardés à l'échelle du département. |
| Q-CONS-04 | Complétude (non-perte) | …un écart de surface entre staging et rattachés + rejetés | 0 m² | Bloquer | ✅ 246 449 ha des deux côtés |
| Q-CONS-05 | Unicité | …les feux dupliqués dans `int_feux__danger`, ou un total différent de la staging | 0 | Bloquer | ✅ |
| Q-CONS-06 | Unicité | …les (département, jour cible) en double | 0 | Bloquer | ✅ |
| Q-CONS-07 | Complétude (non-perte) | …les niveaux J+1 ou J+2 perdus entre staging et `int_mdf__danger_jour` | 0 | Bloquer | ✅ 35 616 et 35 616 |
| Q-CONS-08 | Cohérence (jointure) | …les feux dans la fenêtre des bulletins mais sans niveau | 0 | Bloquer | ✅ |
| Q-CONS-09 | Complétude de la population | …les feux 2024-2025 sans niveau | suivi | Tolérer | 1 296 sur 3 908 (1 252 hors saison, 44 outre-mer) |
| Q-CONS-10 | Complétude (non-perte) | …les départements dont la surface des polygones ≠ somme des morceaux par commune (> 0,1 %) | 0,1 % | Alerter | ⚠️ Haute-Savoie : 0,23 % hors des communes françaises (débord sur la Suisse) |

Les nombres **et** les sommes se réconcilient : 37 lignes perdues et 37 dupliquées donneraient le bon total, mais de faux chiffres. Après un échec, on lit la table de rejet, on corrige, puis on rejoue. Le rejeu est sans risque grâce à Q-PIP-01.

## 4. Conformité RGPD

| ID | Le test renvoie… | Seuil | Décision | Résultat 18/11 |
|---|---|---|---|---|
| Q-RGPD-01 | …les colonnes interdites dans `staging` ou `intermediate` (décès, bâtiments, adresse, requérant, victimes, agents, coordonnées) | 0 | Bloquer | ✅ |
| Q-RGPD-02 | …les communes où une cause est affichée avec moins de 3 feux | 0 | Bloquer | À écrire avec la couche gold (S4) |

## 5. Correspondance avec ISO/IEC 25012

| Caractéristique | Où elle est traitée |
|---|---|
| Exactitude | Exactitude syntaxique : Q-MDF-02, Q-BDF-02, 03, 06, 07. Exactitude sémantique **non vérifiée** : pas de référence terrain, le fichier SDMIS servira de comparaison pour le 69. |
| Complétude | Q-MDF-03 à 05, Q-BDF-08 à 10, Q-COG-02, Q-CONS-02, 04, 07, 10 |
| Cohérence | Q-BDF-04, 05, 13, Q-MDF-06, Q-CONS-01, 03, 08 |
| Crédibilité | Fiches d'identité ; sous-déclaration probable de la BDIFF hors zone méditerranéenne ; notes de la source sur les campagnes perdues |
| Actualité | Q-MDF-07, Q-BDF-11 |
| Traçabilité | Colonnes `_fichier_source`, `_ligne_source`, `_empreinte_fichier` ; journal ; `SHA256SUMS.txt` des silos |
| Disponibilité, récupérabilité | Silos datés jamais écrasés : la base se reconstruit par rejeu (3 à 6 min) |
| Confidentialité, accessibilité | Aucune colonne personnelle après raw (Q-RGPD-01) ; fichier hors Git |
| Conformité | Contrat de schéma (Q-PIP-02) ; licences (modèle, section 5) |
| Compréhensibilité | Noms explicites avec unité (`_m2`) ; glossaire ; dictionnaire de données au rendu final |
| Précision | Grain déclaré pour chaque table ; le niveau de danger n'existe qu'au département |
| Portabilité, efficience | Un fichier DuckDB au format 1.2, SQL standard, formats d'origine conservés |

L'unicité, dimension du cours, n'a pas de caractéristique dédiée dans ISO/IEC 25012 : elle est couverte par Q-PIP-01, Q-BDF-00 et 01, Q-MDF-01, Q-COG-01, Q-CONS-01, 05 et 06.

## 6. Synthèse pour la direction au 18/11/2026

| Question | Verdict | Ce que cela veut dire |
|---|---|---|
| Q1. Où les feux deviennent-ils graves ? | **Avec réserves** pour la région ; **non utilisable** pour le Rhône seul | La BDIFF ne compte que 62 feux en 20 ans dans le Rhône, dont 41 la même année. La surface boisée par commune est désormais disponible pour rapporter les feux à l'exposition. |
| Q2. À quel niveau se produisent les feux ? | **Avec réserves** | 2 612 feux de 2024-2025 ont un niveau en France, 225 en Auvergne-Rhône-Alpes, 3 dans le Rhône. Un seuil s'estime à l'échelle régionale ou nationale et se transpose au Rhône. |
| Q3. Pourquoi des feux à niveau bas ? | **Avec réserves** | Un feu sur trois (2024-2025) survient hors saison du bulletin ; la cause manque pour un feu sur deux |
| Q4. Le Rhône face à ses voisins et à la France ? | **Utilisable** côté indice et feux ; **avec réserves** côté exposition | Les feux sont maintenant nationaux. La surface boisée ne couvre que les 12 départements de la région. |

## 7. Règles ajoutées le 19/11/2026 (nouvelles sources)

| Règle | Couche | Dimension | Énoncé | Décision | Résultat du 19/11 |
|---|---|---|---|---|---|
| Q-SIS-01 | staging | Unicité | (année, SIS) en double dans les statistiques DGSCGC | bloquer | réussi |
| Q-SIS-02 | staging | Complétude de la population | année 2008-2024 sans ligne pour le SDMIS (69) | alerter | réussi |
| Q-SIS-03 | staging | Complétude des valeurs | SIS × année sans détail « feux de végétations » (schéma 2010-2013) | tolérer | 396 lignes, attendu |
| Q-MET-01 | staging | Unicité | (station, date) en double dans les données quotidiennes Météo-France | bloquer | réussi |
| Q-MET-02 | staging | Complétude des valeurs | année 1991-2025 où Lyon-Bron a moins de 98 % de TX renseignées | alerter | réussi |
| Q-MET-03 | staging | Validité | TX hors de -30 à 50 °C ou pluie négative | alerter | réussi |
| Q-GAS-01 | staging | Conformité au référentiel | commune GASPAR « feu de forêt » absente du COG 2026 | alerter | 3 communes (fusions), sans effet sur le Rhône |
| Q-CAS-01 | staging | Validité | site SDMIS hors de l'emprise du Rhône | alerter | réussi |

Q-RGPD-01 s'applique aussi au schéma `marts`. Bilan de l'exécution du 19/11/2026 : 45 règles, 33 réussies, 5 alertes et 7 tolérances connues, aucune règle bloquante en échec. Les résultats sont exportés à chaque exécution dans `data/marts/_qualite_tests.parquet` et affichés sur la page « Sources et méthode » du tableau de bord.
