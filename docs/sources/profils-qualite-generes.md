# Profils de qualité générés (annexe)

Généré par `src/profil_qualite.py` à partir des extractions du 17/11/2026. Ne pas modifier à la main.

## Météo des forêts 2024-2026 (France)

35616 lignes.

| colonne       | type observé   | complétude   |   distincts | min                  | max                  |
|:--------------|:---------------|:-------------|------------:|:---------------------|:---------------------|
| annee_fichier | numérique      | 100.0%       |           3 | 2024                 | 2026                 |
| date          | texte          | 100.0%       |         371 | 2024-06-03T16:00:00Z | 2026-10-05T14:50:04Z |
| num_dep       | texte          | 100.0%       |         105 | 01                   | 95                   |
| niveau_j1     | numérique      | 100.0%       |           4 | 1                    | 4                    |
| niveau_j2     | numérique      | 100.0%       |           4 | 1                    | 4                    |
| nom_dep       | texte          | 100.0%       |          96 | Ain                  | Yvelines             |

| contrôle                                               | dimension                   | résultat                                                         |
|:-------------------------------------------------------|:----------------------------|:-----------------------------------------------------------------|
| Niveaux dans {1,2,3,4}                                 | validité                    | 100.0% des lignes                                                |
| Unicité (département, date d'émission)                 | unicité                     | 0 doublon                                                        |
| Départements par bulletin                              | complétude de la population | 96 départements dans 371 bulletins                               |
| Code département sur 1 caractère (`1` au lieu de `01`) | cohérence                   | 2160 lignes (fichiers 2024 et 2025)                              |
| Heures d'émission (UTC)                                | cohérence                   | 14:50 : 24096, 16:00 : 11520                                     |
| Période d'émission par année                           | actualité / couverture      | 2024 : 03/06 → 30/09; 2025 : 03/06 → 30/09; 2026 : 28/05 → 05/10 |
| Même niveau J+1 et J+2 pour un même jour cible         | cohérence                   | 93.3% (35328 paires)                                             |

## BDIFF Auvergne-Rhône-Alpes 2006-2025

4072 lignes.

| colonne                                    | type observé   | complétude   |   distincts | min                               | max                               |
|:-------------------------------------------|:---------------|:-------------|------------:|:----------------------------------|:----------------------------------|
| Année                                      | numérique      | 100.0%       |          20 | 2006                              | 2025                              |
| Numéro                                     | numérique      | 100.0%       |        3461 | 1                                 | 9995                              |
| Département                                | numérique      | 100.0%       |          12 | 01                                | 74                                |
| Code INSEE                                 | numérique      | 100.0%       |        1563 | 01014                             | 74313                             |
| Nom de la commune                          | texte          | 100.0%       |        1564 | Abondance                         | Évires                            |
| Date de première alerte                    | texte          | 100.0%       |        4042 | 2006-02-02 15:50:00               | 2025-12-14 21:55:00               |
| Surface parcourue (m2)                     | numérique      | 100.0%       |         689 | 1                                 | 9932                              |
| Surface forêt (m2)                         | numérique      | 92.2%        |         463 | 0                                 | 9849                              |
| Surface maquis garrigues (m2)              | numérique      | 42.3%        |         320 | 0                                 | 9829                              |
| Autres surfaces naturelles hors forêt (m2) | numérique      | 57.8%        |         188 | 0                                 | 9932                              |
| Surfaces agricoles (m2)                    | numérique      | 12.9%        |          19 | 0                                 | 7000                              |
| Autres surfaces (m2)                       | numérique      | 12.9%        |           8 | 0                                 | 56100                             |
| Surface autres terres boisées (m2)         | numérique      | 41.9%        |         176 | 0                                 | 9932                              |
| Surfaces non boisées naturelles (m2)       | numérique      | 41.9%        |          85 | 0                                 | 948                               |
| Surfaces non boisées artificialisées (m2)  | numérique      | 41.9%        |          41 | 0                                 | 952                               |
| Surfaces non boisées (m2)                  | numérique      | 68.9%        |         180 | 0                                 | 98000                             |
| Précision des surfaces                     | texte          | 50.6%        |           2 | Estimées                          | Mesurées                          |
| Type de peuplement                         | numérique      | 47.4%        |           6 | 1                                 | 6                                 |
| Nature                                     | texte          | 46.7%        |           5 | Accidentelle                      | Naturelle                         |
| Décès ou bâtiments touchés                 | texte          | 12.8%        |           2 | Non                               | Oui                               |
| Nombre de décès                            | numérique      | 0.9%         |           2 | 0                                 | 1                                 |
| Nombre de bâtiments totalement détruits    | numérique      | 0.9%         |           2 | 0                                 | 1                                 |
| Nombre de bâtiments partiellement détruits | numérique      | 0.9%         |           1 | 0                                 | 0                                 |
| Précision de la donnée                     | texte          | 3.0%         |           1 | Données partielles ou non valides | Données partielles ou non valides |

| contrôle                                                 | dimension                   | résultat                                                                 |
|:---------------------------------------------------------|:----------------------------|:-------------------------------------------------------------------------|
| Unicité (Année, Numéro)                                  | unicité                     | 0 doublon                                                                |
| Année = année de la date d'alerte                        | cohérence                   | 100.0%                                                                   |
| Département = 2 premiers caractères du code INSEE        | cohérence                   | 100.0%                                                                   |
| Surface parcourue > 0                                    | validité                    | 100.0%                                                                   |
| Somme des surfaces ventilées = surface parcourue (±1 m²) | cohérence                   | 96.0% (163 feux en écart)                                                |
| Code INSEE présent dans le COG 2026                      | conformité au référentiel   | 98.8% ; 48 feux / 25 codes absents, dont 25 retrouvés par les mouvements |
| Libellé BDIFF = libellé COG 2026 (codes valides)         | cohérence                   | 98.6%                                                                    |
| Cause (`Nature`) renseignée                              | complétude                  | 46.7% (69 : 12.9%)                                                       |
| Feux par an dans le 69 (2006 → 2025)                     | complétude de la population | 0 0 0 1 0 1 0 0 0 41 4 0 0 9 0 0 1 2 2 1 ; 11 années à 0                 |
| Feux hors juin-septembre (hors saison du bulletin MdF)   | couverture                  | 49.6% des feux, 40.9% de la surface                                      |

## COG 2026, communes de la région 84

4025 communes.

| colonne   | type observé   | complétude   |   distincts | min                   | max     |
|:----------|:---------------|:-------------|------------:|:----------------------|:--------|
| TYPECOM   | texte          | 100.0%       |           1 | COM                   | COM     |
| COM       | numérique      | 100.0%       |        4025 | 01001                 | 74315   |
| REG       | numérique      | 100.0%       |           1 | 84                    | 84      |
| DEP       | numérique      | 100.0%       |          12 | 01                    | 74      |
| CTCD      | texte          | 100.0%       |          13 | 01D                   | 74D     |
| ARR       | numérique      | 100.0%       |          39 | 011                   | 744     |
| TNCC      | numérique      | 100.0%       |           6 | 0                     | 5       |
| NCC       | texte          | 100.0%       |        3921 | ABERGEMENT CLEMENCIAT | YZEURE  |
| NCCENR    | texte          | 100.0%       |        3921 | Abergement-Clémenciat | Évosges |
| LIBELLE   | texte          | 100.0%       |        3926 | Abondance             | Évosges |
| CAN       | numérique      | 100.0%       |         251 | 0101                  | 7499    |
| COMPARENT | texte          | 0.0%         |           0 |                       |         |

| contrôle                                | dimension   | résultat            |
|:----------------------------------------|:------------|:--------------------|
| Unicité du code commune (TYPECOM = COM) | unicité     | oui                 |
| Communes du 69 par collectivité (CTCD)  | couverture  | 69D : 208, 69M : 58 |
