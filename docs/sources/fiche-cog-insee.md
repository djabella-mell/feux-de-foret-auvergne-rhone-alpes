# Fiche source : Code officiel géographique (COG), millésime 2026

- **Autrice de la fiche :** Lynda LAZRI
- **Fiche remplie le :** 17/11/2026, avec les fichiers ouverts (`v_commune_2026.csv`, `v_mvt_commune_2026.csv`, `v_departement_2026.csv`, `v_ctcd_2026.csv`)
- **Trois dates :**
  - réalité décrite : découpage administratif au 01/01/2026, plus l'historique des mouvements ;
  - publication : page Insee « Code officiel géographique » publiée le 24/02/2026 ;
  - mise à jour de la fiche : 17/11/2026.

| Catégorie | Rubrique | Valeur |
|---|---|---|
| Identité | Nom | Code officiel géographique, millésime 2026 |
| | Description | Nomenclature des communes, départements, régions et collectivités, avec les mouvements de communes (fusions, rétablissements…) |
| Provenance et propriété | Producteur | Insee. Les modifications sont validées chaque année avec la DGCL. |
| Technique | Format | CSV, séparateur `,`, valeurs entre guillemets |
| | Schéma (communes) | `TYPECOM, COM, REG, DEP, CTCD, ARR, TNCC, NCC, NCCENR, LIBELLE, CAN, COMPARENT` |
| | Schéma (mouvements) | `MOD, DATE_EFF, TYPECOM_AV, COM_AV, …, TYPECOM_AP, COM_AP, …, LIBELLE_AP` |
| | Clés | `COM` (code commune), unique pour `TYPECOM = COM` |
| | Localisation | insee.fr/fr/information/8740222 (également sur data.gouv.fr) |
| Accès | Mode | Téléchargement de fichier publié. API Métadonnées Insee disponible (non testée). |
| Couverture | Grain | Une ligne = une commune (ou un arrondissement municipal, ou une commune déléguée) au 01/01/2026 |
| | Emprise | France entière. Extrait conservé : région 84, soit 4 025 communes (+ 9 arrondissements municipaux de Lyon) et 1 279 mouvements touchant la région. |
| | Rhône | 266 communes : 208 dans le Rhône (69D) et 58 dans la Métropole de Lyon (69M), colonne `CTCD` |
| Fraîcheur | Fréquence | Annuelle (nouveau millésime au 1er janvier) |
| | Volumétrie | 37 496 lignes au national pour les communes, 13 734 pour les mouvements |
| Qualité | Usage dans le projet | Référentiel des jointures. 48 feux BDIFF ont un code absent du COG 2026 et tous sont retrouvés par les mouvements (MOD 32 « création de commune nouvelle » : 22 ; MOD 35 « suppression de commune déléguée » : 3). |
| Gouvernance | Données personnelles | Aucune |
| | Licence | **Non vérifiée** : la licence n'est pas affichée sur la page data.gouv.fr consultée, et les conditions de réutilisation d'insee.fr n'ont pas été lues. |
| Lineage | Transformations | Aucune |
| Besoin | Questions servies | Q1 (localiser), Q4 (rapporter à un territoire), et toutes les jointures |

**Piège relevé :** joindre la BDIFF 2006 sur le COG 2026 sans table de passage fait perdre 1,2 % des feux de la région. Pour l'Ardèche (18 feux) et le Cantal (9 feux), ce ne sont pas des marges négligeables à l'échelle d'une commune.
