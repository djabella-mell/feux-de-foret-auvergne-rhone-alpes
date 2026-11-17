# Profils de qualité v1 (17/11/2026)

Responsable : Lynda LAZRI (qualité et conformité). Profils établis sur les fichiers ouverts le 17/11/2026.

Pour chaque source, on donne ce qui est fiable, ce qui ne l'est pas, et le verdict d'usage : **utilisable**, **utilisable avec réserve** ou **non utilisable** pour nos questions.

## Météo des forêts 2024-2026

| Dimension | Constat | Conséquence |
|---|---|---|
| Complétude des valeurs | 100 % pour toutes les colonnes | — |
| Complétude de la population | 96 départements dans chacun des 371 bulletins | — |
| Unicité | 0 doublon (département, date d'émission) | — |
| Validité | niveaux tous compris entre 1 et 4 | — |
| Cohérence | code `1` au lieu de `01` (2 160 lignes en 2024-2025) ; colonne `nom_dep` / `dep_nom` ; séparateur `,` puis `;` ; heure d'émission 16:00Z (2024) puis 14:50Z | Harmoniser à la lecture |
| Cohérence J+1 / J+2 | même niveau pour le même jour cible dans 93,3 % des cas | Les deux échéances sont exploitables |
| Couverture temporelle | émissions du 03/06 au 30/09 (2024, 2025), du 28/05 au 05/10 (2026) ; rien hors saison | Voir [décision face au manque](decision-manque.md) |
| Piège de sens | `date` = date d'**émission** ; le niveau s'applique au lendemain (J+1) ou au surlendemain (J+2) | À rappeler dans toute jointure avec des feux |

**Verdict : utilisable** pour la période et la saison couvertes.

## BDIFF Auvergne-Rhône-Alpes 2006-2025

| Dimension | Constat | Conséquence |
|---|---|---|
| Unicité | 0 doublon (Année, Numéro) | — |
| Validité | surfaces toutes > 0 ; `Année` = année de la date d'alerte à 100 % | — |
| Cohérence | département = préfixe du code INSEE à 100 % ; ventilation des surfaces cohérente pour 96 % des feux (163 en écart) | Utiliser `Surface parcourue`, pas la somme des ventilations |
| Conformité au référentiel | 48 feux (25 codes) absents du COG 2026, **tous** retrouvés par la table des mouvements ; 1,4 % de libellés différents du COG | Joindre par le code, jamais par le libellé |
| Complétude des valeurs | cause renseignée pour 46,7 % des feux, et 12,9 % dans le Rhône ; précision des surfaces 50,6 % | La cause ne peut pas porter une conclusion |
| **Complétude de la population** | Rhône : 62 feux en 20 ans, dont 41 en 2015, et 11 années à 0 feu. Ardèche : 1 608. Le site signale des campagnes au nombre d'incendies inconnu. | **Sous-déclaration probable** dans le Rhône |
| Couverture temporelle | jusqu'en 2025 ; 2026 non publiée | Voir [décision face au manque](decision-manque.md) |
| Couverture saisonnière | 49,6 % des feux et 40,9 % de la surface hors juin-septembre (2006-2025) | Une partie des feux n'a pas de bulletin MdF correspondant |

**Verdict : utilisable avec réserve.** Elle est fiable pour la région, mais **pas pour le Rhône seul** (population incomplète).

## COG 2026

| Dimension | Constat | Conséquence |
|---|---|---|
| Unicité | code commune unique | Clé de jointure |
| Complétude | 100 % hors `COMPARENT` (vide sauf pour les communes déléguées, ce qui est normal) | — |
| Couverture | 266 communes dans le 69 : 208 dans le Rhône (69D), 58 dans la Métropole (69M) | Distinction possible |

**Verdict : utilisable.** C'est le référentiel retenu.

## Sources non profilées

- **BD Forêt V2** : fichier pas encore ouvert. Profil à faire.
- **Interventions SDMIS** : aucun fichier reçu.
